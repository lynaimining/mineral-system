# -*- coding: utf-8 -*-
"""
JORC/NI 43-101报告PDF数据提取器
使用PyMuPDF提取关键成本和资源数据
"""
import fitz  # PyMuPDF
import re
import json
import os

def extract_text_from_pdf(pdf_path):
    """提取PDF全文"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f'PDF读取失败: {e}')
        return None

def extract_opex_data(text):
    """提取OPEX数据（USD/t或USD/oz）"""
    patterns = {
        'mining_cost': r'mining\s+cost[s]?\s*[:=]?\s*\$?\s*([\d,]+\.?\d*)\s*/\s*t',
        'processing_cost': r'processing\s+cost[s]?\s*[:=]?\s*\$?\s*([\d,]+\.?\d*)\s*/\s*t',
        'total_opex': r'total\s+(?:operating\s+)?cost[s]?\s*[:=]?\s*\$?\s*([\d,]+\.?\d*)\s*/\s*t',
        'aisc': r'AISC\s*[:=]?\s*\$?\s*([\d,]+\.?\d*)\s*/\s*oz',
    }

    results = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # 取第一个匹配，去除逗号
            value = float(matches[0].replace(',', ''))
            results[key] = value

    return results

def extract_capex_data(text):
    """提取CAPEX数据（百万美元）"""
    patterns = {
        'initial_capex': r'initial\s+capital\s*[:=]?\s*\$?\s*([\d,]+\.?\d*)\s*(?:million|M)',
        'total_capex': r'total\s+capital\s*[:=]?\s*\$?\s*([\d,]+\.?\d*)\s*(?:million|M)',
    }

    results = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            value = float(matches[0].replace(',', ''))
            results[key] = value

    return results

def extract_resource_data(text):
    """提取资源量数据"""
    # 查找资源量表格（通常包含Measured/Indicated/Inferred）
    patterns = {
        'measured_tonnage': r'Measured\s+[\d,]+\.?\d*\s+([\d,]+\.?\d*)',
        'indicated_tonnage': r'Indicated\s+[\d,]+\.?\d*\s+([\d,]+\.?\d*)',
        'inferred_tonnage': r'Inferred\s+[\d,]+\.?\d*\s+([\d,]+\.?\d*)',
        'grade': r'grade\s*[:=]?\s*([\d,]+\.?\d*)\s*g/t',
    }

    results = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            value = float(matches[0].replace(',', ''))
            results[key] = value

    return results

def extract_project_metadata(text, filename):
    """提取项目元数据"""
    # 项目名称（通常在标题）
    title_match = re.search(r'(?:Technical\s+Report|NI\s+43-101).*?for\s+(?:the\s+)?([\w\s]+?)(?:Project|Property|Mine)',
                           text[:2000], re.IGNORECASE)
    project_name = title_match.group(1).strip() if title_match else filename

    # 国家
    country_patterns = [
        r'(?:located\s+in|situated\s+in)\s+([\w\s]+?)(?:,|\.|$)',
        r'Country:\s*([\w\s]+)',
    ]
    country = None
    for pattern in country_patterns:
        match = re.search(pattern, text[:5000], re.IGNORECASE)
        if match:
            country = match.group(1).strip()
            break

    # 报告日期
    date_match = re.search(r'(?:Effective\s+Date|Report\s+Date):\s*(\w+\s+\d{1,2},?\s+\d{4})',
                          text[:3000], re.IGNORECASE)
    report_date = date_match.group(1) if date_match else None

    return {
        'project_name': project_name,
        'country': country,
        'report_date': report_date
    }

def process_pdf_report(pdf_path):
    """处理单个PDF报告，提取所有关键数据"""
    print(f'\n处理报告: {os.path.basename(pdf_path)}')

    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None

    # 提取各类数据
    metadata = extract_project_metadata(text, os.path.basename(pdf_path))
    opex = extract_opex_data(text)
    capex = extract_capex_data(text)
    resources = extract_resource_data(text)

    result = {
        'source_file': os.path.basename(pdf_path),
        'metadata': metadata,
        'opex': opex,
        'capex': capex,
        'resources': resources,
        'extraction_success': bool(opex or capex or resources)
    }

    # 打印提取结果
    print(f'  项目: {metadata.get("project_name", "Unknown")}')
    print(f'  国家: {metadata.get("country", "Unknown")}')
    print(f'  日期: {metadata.get("report_date", "Unknown")}')
    if opex:
        print(f'  OPEX: {opex}')
    if capex:
        print(f'  CAPEX: {capex}')
    if resources:
        print(f'  资源量: {resources}')

    return result

def batch_process_reports(reports_dir):
    """批量处理reports目录下的所有PDF"""
    if not os.path.exists(reports_dir):
        print(f'目录不存在: {reports_dir}')
        return []

    pdf_files = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]
    print(f'找到 {len(pdf_files)} 个PDF文件')

    results = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(reports_dir, pdf_file)
        result = process_pdf_report(pdf_path)
        if result:
            results.append(result)

    # 保存提取结果
    output_file = os.path.join(reports_dir, 'extracted_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'\n提取完成，结果已保存: {output_file}')
    print(f'成功提取 {len([r for r in results if r["extraction_success"]])} / {len(results)} 份报告')

    return results

if __name__ == '__main__':
    REPORTS_DIR = r'C:\Users\39555\.claude\tools\mining-price-engine\reports'

    print('=== JORC/NI 43-101报告数据提取器 ===\n')
    print('使用说明：')
    print('1. 将JORC/NI 43-101报告PDF放入: ' + REPORTS_DIR)
    print('2. 运行本脚本自动提取成本、资源量等数据')
    print('3. 提取结果保存为 extracted_data.json\n')

    # 创建目录
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # 检查是否有PDF文件
    pdf_count = len([f for f in os.listdir(REPORTS_DIR) if f.endswith('.pdf')])
    if pdf_count == 0:
        print(f'未找到PDF文件，请将报告放入: {REPORTS_DIR}')
        print('\n示例报告来源：')
        print('- SEDAR+: https://www.sedarplus.ca (搜索 "43-101 gold")')
        print('- ASX: https://www.asx.com.au (搜索公司公告)')
        print('- 公司网站: 在Investor Relations页面查找Technical Reports')
    else:
        results = batch_process_reports(REPORTS_DIR)
