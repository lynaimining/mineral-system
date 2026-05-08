#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF 文本提取脚本 - pdf2skill Phase 1
用法: python extract_pdf.py <pdf_path> [--output <txt_path>]
"""
import sys
import subprocess
import argparse
from pathlib import Path


def extract_with_pdftotext(pdf_path: str) -> str:
    """使用 pdftotext 提取（速度最快，适合纯文本 PDF）"""
    result = subprocess.run(
        ['pdftotext', '-layout', '-enc', 'UTF-8', pdf_path, '-'],
        capture_output=True, text=True, encoding='utf-8'
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {result.stderr}")
    return result.stdout


def is_text_garbled(text: str) -> bool:
    """
    检测文本是否乱码（mojibake）。
    判断依据：Unicode 替换字符（U+FFFD）占比超过 1%，或非打印字符占比超过 5%。
    """
    if not text or len(text.strip()) < 50:
        return True
    sample = text[:5000]
    replacement_ratio = sample.count('\ufffd') / len(sample)
    if replacement_ratio > 0.01:
        return True
    # 检查非打印、非空白字符（排除常见标点）
    non_printable = sum(
        1 for c in sample
        if ord(c) < 32 and c not in ('\n', '\r', '\t', '\f')
    )
    if non_printable / len(sample) > 0.05:
        return True
    return False


def extract_with_pymupdf(pdf_path: str) -> str:
    """使用 PyMuPDF 提取（备选，支持更多 PDF 格式）"""
    import fitz
    with fitz.open(pdf_path) as doc:
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text("text")
            pages.append(f"--- Page {i+1} ---\n{text}")
    return "\n".join(pages)


def extract_pdf(pdf_path: str) -> dict:
    """
    主提取函数，自动选择工具，返回结构化结果
    Returns: {
        'text': str,          # 完整文本
        'page_count': int,    # 页数（pdftotext 输出基于 \f 形式符计数，为近似值）
        'tool': str,          # 使用的工具
        'file_size_mb': float # 文件大小
    }
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    file_size_mb = path.stat().st_size / (1024 * 1024)
    text = None
    tool_used = None

    # 优先尝试 pdftotext（速度快）
    try:
        text = extract_with_pdftotext(pdf_path)
        tool_used = "pdftotext"
    except (RuntimeError, FileNotFoundError):
        pass

    # fallback: PyMuPDF（pdftotext 不可用、输出为空、或输出乱码时）
    if not text or len(text.strip()) < 100 or is_text_garbled(text):
        if is_text_garbled(text):
            print("[pdf2skill] Warning: pdftotext output appears garbled, falling back to PyMuPDF", file=sys.stderr)
        try:
            text = extract_with_pymupdf(pdf_path)
            tool_used = "PyMuPDF"
        except ImportError:
            raise RuntimeError(
                "No PDF extraction tool available. "
                "Install PyMuPDF: pip install PyMuPDF"
            )

    # 统计页数
    page_count = text.count("--- Page ") if "--- Page " in text else text.count("\f") + 1

    return {
        'text': text,
        'page_count': page_count,
        'tool': tool_used,
        'file_size_mb': round(file_size_mb, 2)
    }


def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF for pdf2skill')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output', '-o', help='Output text file path (default: stdout)')
    args = parser.parse_args()

    result = extract_pdf(args.pdf_path)

    print(f"[pdf2skill] Extracted: {result['page_count']} pages, "
          f"{result['file_size_mb']} MB, tool={result['tool']}", file=sys.stderr)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        print(f"[pdf2skill] Saved to: {args.output}", file=sys.stderr)
    else:
        print(result['text'])


if __name__ == '__main__':
    main()
