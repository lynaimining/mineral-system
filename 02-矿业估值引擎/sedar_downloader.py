# -*- coding: utf-8 -*-
"""
SEDAR+ NI 43-101报告自动下载器
从加拿大SEDAR+系统下载公开的NI 43-101技术报告
"""
import requests
import json
import time
import os
from datetime import datetime, timedelta

SEDAR_API_BASE = 'https://www.sedarplus.ca/csa-party/api/v1'
DOWNLOAD_DIR = r'C:\Users\39555\.claude\tools\mining-price-engine\reports'

def search_ni43101_reports(keyword='gold', from_date='2023-01-01', max_results=10):
    """
    搜索NI 43-101报告
    keyword: 搜索关键词（gold/copper/nickel/lithium）
    from_date: 起始日期
    max_results: 最大结果数
    """
    # SEDAR+ 搜索API端点
    search_url = f'{SEDAR_API_BASE}/documents/search'

    params = {
        'q': f'{keyword} 43-101',
        'from': from_date,
        'size': max_results,
        'sort': 'filingDate:desc'
    }

    try:
        print(f'搜索关键词: {keyword}, 起始日期: {from_date}')
        response = requests.get(search_url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            reports = data.get('hits', {}).get('hits', [])
            print(f'找到 {len(reports)} 份报告')
            return reports
        else:
            print(f'搜索失败: HTTP {response.status_code}')
            return []
    except Exception as e:
        print(f'搜索出错: {e}')
        return []

def download_report(doc_id, filename):
    """下载单个报告PDF"""
    download_url = f'{SEDAR_API_BASE}/documents/{doc_id}/files'

    try:
        response = requests.get(download_url, timeout=60)
        if response.status_code == 200:
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f'  已下载: {filename}')
            return filepath
        else:
            print(f'  下载失败: HTTP {response.status_code}')
            return None
    except Exception as e:
        print(f'  下载出错: {e}')
        return None

def extract_metadata_from_search_result(hit):
    """从搜索结果中提取元数据"""
    source = hit.get('_source', {})
    return {
        'doc_id': hit.get('_id'),
        'company': source.get('issuerName', 'Unknown'),
        'title': source.get('documentTitle', 'Unknown'),
        'filing_date': source.get('filingDate', 'Unknown'),
        'document_type': source.get('documentType', 'Unknown'),
        'size_kb': source.get('fileSize', 0) / 1024 if source.get('fileSize') else 0
    }

def batch_download_reports(keyword='gold', from_date='2023-01-01', max_downloads=5):
    """批量下载报告"""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    reports = search_ni43101_reports(keyword, from_date, max_downloads * 2)

    downloaded = []
    for i, hit in enumerate(reports[:max_downloads]):
        meta = extract_metadata_from_search_result(hit)

        print(f'\n[{i+1}/{max_downloads}] {meta["company"]} - {meta["filing_date"]}')
        print(f'  标题: {meta["title"][:80]}...')
        print(f'  大小: {meta["size_kb"]:.1f} KB')

        # 生成文件名
        safe_company = "".join(c for c in meta['company'] if c.isalnum() or c in (' ', '-', '_'))[:50]
        filename = f"{meta['filing_date']}_{safe_company}_{keyword}.pdf"

        # 下载
        filepath = download_report(meta['doc_id'], filename)
        if filepath:
            meta['local_path'] = filepath
            downloaded.append(meta)

        # 避免请求过快
        time.sleep(2)

    # 保存元数据
    meta_file = os.path.join(DOWNLOAD_DIR, f'{keyword}_reports_metadata.json')
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(downloaded, f, ensure_ascii=False, indent=2)

    print(f'\n成功下载 {len(downloaded)} 份报告')
    print(f'元数据已保存: {meta_file}')
    return downloaded

if __name__ == '__main__':
    # 测试：下载最近的金矿NI 43-101报告
    print('=== SEDAR+ NI 43-101报告下载器 ===\n')

    # 注意：SEDAR+ API可能需要认证或有访问限制
    # 如果直接访问失败，需要：
    # 1. 注册SEDAR+账号
    # 2. 获取API token
    # 3. 或者使用网页爬虫方式

    print('注意：SEDAR+ API可能需要认证')
    print('如果失败，将使用备用方案（手动下载列表）\n')

    try:
        reports = batch_download_reports('gold', '2023-01-01', 3)
    except Exception as e:
        print(f'\n自动下载失败: {e}')
        print('\n备用方案：')
        print('1. 访问 https://www.sedarplus.ca')
        print('2. 搜索 "43-101 gold"')
        print('3. 手动下载PDF到: ' + DOWNLOAD_DIR)
        print('4. 运行数据提取脚本')
