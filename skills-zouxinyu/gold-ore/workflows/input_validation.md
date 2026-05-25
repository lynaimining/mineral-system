# 两阶段输入验证（共享工作流）

> 适用于 chinese-paper、gold-ore 及所有处理用户上传文件的 skill。
> **核心原则**：用廉价的规则检查过滤明显问题，只对通过的文件做昂贵的 LLM 解析。

---

## 触发时机

在任何 skill 开始处理用户上传的文件之前，**必须**先执行本工作流。
- 用户上传了 DOCX / PDF / XLSX / 图片文件
- 用户指定了一个包含多个文件的目录路径

---

## 阶段一：快速规则检查（<10秒，无 LLM 调用）

```python
import os
import zipfile
from pathlib import Path

def phase1_quick_check(file_path: str, skill_type: str) -> dict:
    """
    阶段一：快速规则检查
    skill_type: 'chinese-paper' | 'gold-ore' | 'general'
    返回: {'pass': bool, 'issues': list, 'warnings': list}
    """
    issues = []    # FAIL 级别，阻断处理
    warnings = []  # WARN 级别，继续但提示

    path = Path(file_path)

    # 1. 文件存在性检查
    if not path.exists():
        return {'pass': False, 'issues': [f'文件不存在: {file_path}'], 'warnings': []}

    # 2. 文件大小检查
    size_kb = path.stat().st_size / 1024
    if size_kb < 1:
        issues.append(f'文件过小（{size_kb:.1f}KB），可能为空文件')
    elif size_kb > 200 * 1024:  # 200MB
        warnings.append(f'文件较大（{size_kb/1024:.0f}MB），处理可能较慢')

    # 3. 文件格式检查
    suffix = path.suffix.lower()
    SUPPORTED = {'.docx', '.pdf', '.xlsx', '.xls', '.csv', '.pptx',
                 '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp'}
    if suffix not in SUPPORTED:
        issues.append(f'不支持的文件格式: {suffix}')

    # 4. DOCX 完整性检查（DOCX 本质是 ZIP）
    if suffix == '.docx':
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                names = z.namelist()
                if 'word/document.xml' not in names:
                    issues.append('DOCX 文件损坏：缺少 word/document.xml')
        except zipfile.BadZipFile:
            issues.append('DOCX 文件损坏：无法作为 ZIP 打开')

    # 5. 编码检查（仅 CSV/TXT）
    if suffix in {'.csv', '.txt'}:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    f.read(1024)
                warnings.append('文件编码为 GBK，将自动转换为 UTF-8')
            except UnicodeDecodeError:
                issues.append('文件编码无法识别（非 UTF-8 也非 GBK）')

    # 6. skill 特定关键字段检查
    if skill_type == 'gold-ore' and suffix == '.docx':
        try:
            from docx import Document
            doc = Document(file_path)
            full_text = '\n'.join([p.text for p in doc.paragraphs])
            REQUIRED_KEYWORDS = ['品位', '资源量', '矿床', 'grade', 'resource', 'deposit']
            found = [kw for kw in REQUIRED_KEYWORDS if kw in full_text]
            if len(found) == 0:
                warnings.append('文档中未找到矿业相关关键词，请确认文件是否正确')
        except Exception:
            pass  # 关键字检查失败不阻断

    if skill_type == 'chinese-paper' and suffix == '.docx':
        try:
            from docx import Document
            doc = Document(file_path)
            full_text = '\n'.join([p.text for p in doc.paragraphs])
            if len(full_text.strip()) < 500:
                warnings.append(f'文档内容较少（{len(full_text)}字），可能为空文档或扫描件')
        except Exception:
            pass

    return {
        'pass': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }
```

**阶段一结果处理**：
- `pass=True`：进入阶段二
- `pass=False`：**立即停止**，告知用户具体问题，不进行 LLM 解析
- 有 warnings：继续处理，但在最终报告中注明

---

## 阶段二：深度内容验证（LLM 驱动，仅对通过阶段一的文件）

阶段二只在以下情况触发：
- 文件通过阶段一，但内容疑似异常（如文件大小正常但文本极少）
- 用户上传了多个文件，需要判断哪些是主要材料

**阶段二提示词模板**：

```
你是一个文件内容验证助手。请快速扫描以下文档内容，回答三个问题：

1. 这份文档的主要内容是什么？（1句话）
2. 文档是否包含 {skill_type} 任务所需的核心信息？（是/否，说明原因）
3. 是否有明显的数据质量问题？（如：大量乱码、内容截断、格式混乱）

文档内容（前2000字）：
{document_preview}

请用 JSON 格式回答：
{{"summary": "...", "relevant": true/false, "reason": "...", "quality_issues": "..."}}
```

**阶段二结果处理**：
- `relevant=true` + 无质量问题 → 正常处理
- `relevant=false` → 警告用户，询问是否继续
- 有质量问题 → 在处理结果中标注，建议用户检查原始文件

---

## 批量文件处理规则

当用户提供目录路径时：

```python
def validate_directory(dir_path: str, skill_type: str) -> dict:
    """批量验证目录中的文件"""
    results = {'passed': [], 'failed': [], 'warnings': []}

    for file in Path(dir_path).rglob('*'):
        if file.is_file():
            result = phase1_quick_check(str(file), skill_type)
            if result['pass']:
                results['passed'].append(str(file))
            else:
                results['failed'].append({
                    'file': str(file),
                    'issues': result['issues']
                })
            if result['warnings']:
                results['warnings'].append({
                    'file': str(file),
                    'warnings': result['warnings']
                })

    return results
```

**批量处理原则**：
- 只对 `passed` 列表中的文件进行 LLM 解析
- `failed` 文件列出问题，告知用户，跳过处理
- 如果 `passed` 为空，停止并告知用户

---

## 输出格式（告知用户）

```
【输入验证报告】
检查文件数：X 个
通过：X 个 ✓
失败：X 个 ✗
警告：X 个 ⚠

失败文件：
- file.docx：文件损坏，无法打开
- data.csv：编码无法识别

警告：
- report.docx：文档内容较少（200字），可能为扫描件

将对 X 个通过的文件进行深度分析...
```

---

## 版本记录

- v1.0 (2026-05-08)：初始版本，适用于 chinese-paper 和 gold-ore
