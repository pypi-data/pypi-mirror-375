# A Python tool for translating docx files

## Installation

```bash
pip install docx_translate
```

## Usage

### Use in CMD

```bash
docx_translate --help

docx_translate --version

docx_translate input.docx -o output.docx

docx_translate input.docx -o output.ja.docx -t ja
```

### Use in Python

```python
from docx_translate.core.translate import DocxTranslator

trans = DocxTranslator(target='en')
trans.translate_docx('input.docx', 'output.docx')
```
