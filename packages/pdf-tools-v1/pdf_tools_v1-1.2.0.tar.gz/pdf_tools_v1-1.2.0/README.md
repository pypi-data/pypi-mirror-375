# PDF Tools

A simple Python package for PDF related tools koro sob gulai kore.

## Installation

```bash
pip install pdf-tools-v1
```

## Usage

```python
from pdf_tools import extract_text, get_page_count

text = extract_text("document.pdf")
print(text)

pages = get_page_count("document.pdf")
print(pages)
```

## Functions

- `extract_text(pdf_path)`: Extracts text from a PDF file
- `get_page_count(pdf_path)`: Gets the number of pages in a PDF file

## License

MIT License
