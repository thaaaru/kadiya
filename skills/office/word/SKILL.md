---
name: office-word
description: Generate Word documents using python-docx (workspace only)
homepage: https://python-docx.readthedocs.io/
metadata: {"nanobot":{"emoji":"📝","requires":{"bins":["python3"]}}}
---

# Word Document Generation with python-docx

Create and manipulate Word documents using Python's python-docx library.

## Requirements

```bash
pip install python-docx
```

## Usage

Ask to create Word documents:
```
Create a Word document with a meeting agenda
```

Or:
```
Generate a letter template in Word format
```

## Output Rules

1. **Workspace only**: Files saved to workspace directory
2. **Minimal code**: No unnecessary comments
3. **Direct execution**: Code runs without modification

## Basic Templates

### Simple Document

```python
from docx import Document
from pathlib import Path

doc = Document()
doc.add_heading("Document Title", 0)
doc.add_paragraph("This is the first paragraph.")
doc.add_paragraph("This is another paragraph.")

doc.save(Path.home() / ".nanobot" / "workspace" / "output.docx")
```

### Letter Template

```python
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path
from datetime import datetime

doc = Document()

# Header with date
header = doc.add_paragraph()
header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
header.add_run(datetime.now().strftime("%B %d, %Y"))

doc.add_paragraph()  # Spacing

# Recipient
doc.add_paragraph("To:")
doc.add_paragraph("[Recipient Name]")
doc.add_paragraph("[Address]")

doc.add_paragraph()

# Subject
subject = doc.add_paragraph()
subject.add_run("Subject: ").bold = True
subject.add_run("[Subject Line]")

doc.add_paragraph()

# Body
doc.add_paragraph("Dear Sir/Madam,")
doc.add_paragraph()
doc.add_paragraph("[Letter body goes here]")
doc.add_paragraph()

# Closing
doc.add_paragraph("Yours faithfully,")
doc.add_paragraph()
doc.add_paragraph("[Your Name]")
doc.add_paragraph("[Title]")

doc.save(Path.home() / ".nanobot" / "workspace" / "letter.docx")
```

### Report with Sections

```python
from docx import Document
from docx.shared import Pt, Inches
from pathlib import Path

doc = Document()

# Title
doc.add_heading("Monthly Report", 0)
doc.add_paragraph("January 2024")

# Section 1
doc.add_heading("Executive Summary", level=1)
doc.add_paragraph("Brief overview of the month's activities and achievements.")

# Section 2
doc.add_heading("Key Metrics", level=1)

# Table
table = doc.add_table(rows=4, cols=3)
table.style = "Table Grid"

# Headers
headers = ["Metric", "Target", "Actual"]
for i, header in enumerate(headers):
    table.rows[0].cells[i].text = header

# Data
data = [
    ["Revenue", "Rs. 1,000,000", "Rs. 1,150,000"],
    ["Users", "500", "520"],
    ["Satisfaction", "85%", "88%"],
]
for row_idx, row_data in enumerate(data, 1):
    for col_idx, value in enumerate(row_data):
        table.rows[row_idx].cells[col_idx].text = value

doc.add_paragraph()

# Section 3
doc.add_heading("Next Steps", level=1)
doc.add_paragraph("• Action item 1", style="List Bullet")
doc.add_paragraph("• Action item 2", style="List Bullet")
doc.add_paragraph("• Action item 3", style="List Bullet")

doc.save(Path.home() / ".nanobot" / "workspace" / "report.docx")
```

### Document with Images

```python
from docx import Document
from docx.shared import Inches
from pathlib import Path

doc = Document()
doc.add_heading("Document with Image", 0)

# Add image (must exist in workspace)
workspace = Path.home() / ".nanobot" / "workspace"
image_path = workspace / "image.png"

if image_path.exists():
    doc.add_picture(str(image_path), width=Inches(4))
    doc.add_paragraph("Figure 1: Description")

doc.save(workspace / "with_image.docx")
```

## Common Operations

| Task | Code |
|------|------|
| Bold text | `run.bold = True` |
| Italic text | `run.italic = True` |
| Underline | `run.underline = True` |
| Font size | `run.font.size = Pt(12)` |
| Font name | `run.font.name = "Arial"` |
| Alignment | `para.alignment = WD_ALIGN_PARAGRAPH.CENTER` |
| Page break | `doc.add_page_break()` |
| Bullet list | `style="List Bullet"` |
| Numbered list | `style="List Number"` |

## Token Limits

- Max output: 1024 tokens
- Generate minimal, runnable code
- No explanations unless asked
