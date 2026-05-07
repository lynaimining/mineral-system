# -*- coding: utf-8 -*-
"""
JORC/NI 43-101报告PDF数据提取器 v2.0
使用pdfplumber提取表格 + PyMuPDF提取文本
"""
import fitz  # PyMuPDF
import pdfplumber
import re
import json
import os
from typing import Dict, List, Any

def extract_tables_from_pdf(pdf_path: str) -> List[List[List[str]]]:
    """使用pdfplumber提取所有表格"""
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:50]:  # 只处理前50页，避免太慢
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
    except Exception as e:
        print(f'    表格提取失败: {e}')
    return tables

def find_cost_in_tables(tables: List[List[List[str]]]) -> Dict[str, float]:
    """从表格中查找成本数据"""
    costs = {}

    for table in tables:
        if not table or len(table) < 2:
            continue

        # 将表格转换为字符串以便搜索
        table_text = '\n'.join([' '.join([str(cell) if cell else '' for cell in row]) for row in table])

        # 查找OPEX相关数据
        if any(keyword in table_text.lower() for keyword in ['operating cost', 'opex', 'c1 cost', 'aisc']):
            for row in table:
                row_text = ' '.join([str(cell) if cell else '' for cell in row]).lower()

                # 提取AISC (All-in Sustaining Cost)
                if 'aisc' in row_text or 'all-in sustaining' in row_text:
                    for cell in row:
                        if cell:
                            match = re.search(r'[\$]?\s*([\d,]+\.?\d*)\s*/\s*oz', str(cell))
                            if match:
                                costs['aisc_usd_oz'] = float(match.group(1).replace(',', ''))

                # 提取mining cost
                if 'mining' in row_text and 'cost' in row_text:
                    for cell in row:
                        if cell:
                            match = re.search(r'[\$]?\s*([\d,]+\.?\d*)', str(cell))
                            if match and match.group(1).replace(',', '').strip():
                                try:
                                    costs['mining_cost_usd_t'] = float(match.group(1).replace(',', ''))
                                except ValueError:
                                    pass

                # 提取processing cost
                if 'processing' in row_text or 'milling' in row_text:
                    for cell in row:
                        if cell:
                            match = re.search(r'[\$]?\s*([\d,]+\.?\d*)', str(cell))
                            if match and match.group(1).replace(',', '').strip():
                                try:
                                    costs['processing_cost_usd_t'] = float(match.group(1).replace(',', ''))
                                except ValueError:
                                    pass

        # 查找CAPEX相关数据
        if any(keyword in table_text.lower() for keyword in ['capital', 'capex', 'initial capital']):
            for row in table:
                row_text = ' '.join([str(cell) if cell else '' for cell in row]).lower()

                if 'total' in row_text and 'capital' in row_text:
                    for cell in row:
                        if cell:
                            match = re.search(r'[\$]?\s*([\d,]+\.?\d*)\s*(?:million|m)', str(cell), re.IGNORECASE)
                            if match:
                                costs['capex_total_musd'] = float(match.group(1).replace(',', ''))

    return costs

def find_resources_in_tables(tables: List[List[List[str]]]) -> Dict[str, Any]:
    """从表格中查找资源量数据"""
    resources = {}

    for table in tables:
        if not table or len(table) < 2:
            continue

        table_text = '\n'.join([' '.join([str(cell) if cell else '' for cell in row]) for row in table])

        # 查找资源量表格
        if any(keyword in table_text.lower() for keyword in ['mineral resource', 'ore reserve', 'measured', 'indicated', 'inferred']):
            # 查找表头
            header_row = None
            for i, row in enumerate(table):
                row_text = ' '.join([str(cell) if cell else '' for cell in row]).lower()
                if 'category' in row_text or 'classification' in row_text or 'measured' in row_text:
                    header_row = i
                    break

            if header_row is not None:
                # 解析数据行
                for row in table[header_row+1:]:
                    if not row:
                        continue
                    row_text = ' '.join([str(cell) if cell else '' for cell in row]).lower()

                    # Measured
                    if 'measured' in row_text:
                        for cell in row:
                            if cell:
                                match = re.search(r'([\d,]+\.?\d*)', str(cell))
                                if match and match.group(1).replace(',', '').strip():
                                    try:
                                        val = float(match.group(1).replace(',', ''))
                                        if val > 0.1:  # 过滤掉品位数据
                                            resources['measured_tonnage_mt'] = val
                                            break
                                    except ValueError:
                                        pass

                    # Indicated
                    if 'indicated' in row_text:
                        for cell in row:
                            if cell:
                                match = re.search(r'([\d,]+\.?\d*)', str(cell))
                                if match and match.group(1).replace(',', '').strip():
                                    try:
                                        val = float(match.group(1).replace(',', ''))
                                        if val > 0.1:
                                            resources['indicated_tonnage_mt'] = val
                                            break
                                    except ValueError:
                                        pass

                    # Inferred
                    if 'inferred' in row_text:
                        for cell in row:
                            if cell:
                                match = re.search(r'([\d,]+\.?\d*)', str(cell))
                                if match and match.group(1).replace(',', '').strip():
                                    try:
                                        val = float(match.group(1).replace(',', ''))
                                        if val > 0.1:
                                            resources['inferred_tonnage_mt'] = val
                                            break
                                    except ValueError:
                                        pass

    return resources

def extract_metadata_from_text(text: str, filename: str) -> Dict[str, Any]:
    """从文本中提取元数据"""
    metadata = {
        'project_name': filename.replace('.pdf', ''),
        'country': None,
        'report_date': None,
        'company': None
    }

    # 提取公司名称（通常在前几页）
    first_2000 = text[:2000]

    # 澳大利亚公司通常有ABN
    abn_match = re.search(r'ABN\s+[\d\s]+', first_2000)
    if abn_match:
        metadata['country'] = 'Australia'

    # 查找日期
    date_patterns = [
        r'(?:Effective Date|Report Date|Date):\s*(\d{1,2}\s+\w+\s+\d{4})',
        r'(\d{1,2}\s+\w+\s+\d{4})',
        r'(\w+\s+\d{4})'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, first_2000)
        if match:
            metadata['report_date'] = match.group(1)
            break

    return metadata

def process_pdf_report_v2(pdf_path: str) -> Dict[str, Any]:
    """处理单个PDF报告（v2版本）"""
    filename = os.path.basename(pdf_path)
    print(f'\n处理报告: {filename}')

    # 1. 提取文本（用于元数据）
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc[:10]:  # 只读前10页用于元数据
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f'  文本提取失败: {e}')
        text = ""

    # 2. 提取表格
    print(f'  正在提取表格...')
    tables = extract_tables_from_pdf(pdf_path)
    print(f'  找到 {len(tables)} 个表格')

    # 3. 从表格中提取数据
    metadata = extract_metadata_from_text(text, filename)
    costs = find_cost_in_tables(tables)
    resources = find_resources_in_tables(tables)

    result = {
        'source_file': filename,
        'metadata': metadata,
        'costs': costs,
        'resources': resources,
        'extraction_success': bool(costs or resources),
        'tables_found': len(tables)
    }

    # 打印提取结果
    print(f'  项目: {metadata.get("project_name", "Unknown")}')
    print(f'  国家: {metadata.get("country", "Unknown")}')
    print(f'  日期: {metadata.get("report_date", "Unknown")}')
    if costs:
        print(f'  成本数据: {costs}')
    if resources:
        print(f'  资源量: {resources}')

    return result

def batch_process_reports_v2(reports_dir: str, max_reports: int = 5):
    """批量处理报告（v2版本，先处理少量测试）"""
    if not os.path.exists(reports_dir):
        print(f'目录不存在: {reports_dir}')
        return []

    pdf_files = sorted([f for f in os.listdir(reports_dir) if f.endswith('.pdf')])
    print(f'找到 {len(pdf_files)} 个PDF文件')
    print(f'先处理最新的 {max_reports} 份报告进行测试\n')

    # 优先处理最新的报告（2024-2025年）
    recent_files = [f for f in pdf_files if '2024' in f or '2025' in f][:max_reports]

    results = []
    for pdf_file in recent_files:
        pdf_path = os.path.join(reports_dir, pdf_file)
        result = process_pdf_report_v2(pdf_path)
        if result:
            results.append(result)

    # 保存提取结果
    output_file = os.path.join(reports_dir, 'extracted_data_v2.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'\n提取完成，结果已保存: {output_file}')
    print(f'成功提取 {len([r for r in results if r["extraction_success"]])} / {len(results)} 份报告')

    # 统计
    total_costs = sum(1 for r in results if r['costs'])
    total_resources = sum(1 for r in results if r['resources'])
    print(f'提取到成本数据: {total_costs} 份')
    print(f'提取到资源量数据: {total_resources} 份')

    return results

if __name__ == '__main__':
    REPORTS_DIR = r'C:\Users\39555\.claude\tools\mining-price-engine\reports'

    print('=== JORC/NI 43-101报告数据提取器 v2.0 ===')
    print('使用pdfplumber提取表格 + PyMuPDF提取文本\n')

    results = batch_process_reports_v2(REPORTS_DIR, max_reports=5)
