---
name: office-pptx
description: Generate PowerPoint presentations using python-pptx (workspace only)
homepage: https://python-pptx.readthedocs.io/
metadata: {"nanobot":{"emoji":"📽️","requires":{"bins":["python3"]}}}
---

# PowerPoint Generation with python-pptx

Create presentations using Python's python-pptx library.

## Requirements

```bash
pip install python-pptx
```

## Usage

Ask to create presentations:
```
Create a PowerPoint with 5 slides about project status
```

Or:
```
Generate a presentation template for quarterly review
```

## Output Rules

1. **Workspace only**: Files saved to workspace directory
2. **Minimal code**: No unnecessary comments
3. **Direct execution**: Code runs without modification

## Basic Templates

### Simple Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pathlib import Path

prs = Presentation()

# Title slide
slide_layout = prs.slide_layouts[0]  # Title Slide
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "Presentation Title"
subtitle.text = "Subtitle or date"

# Content slide
slide_layout = prs.slide_layouts[1]  # Title and Content
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
body = slide.placeholders[1]
title.text = "Slide Title"
tf = body.text_frame
tf.text = "First bullet point"
p = tf.add_paragraph()
p.text = "Second bullet point"
p.level = 0
p = tf.add_paragraph()
p.text = "Sub-point"
p.level = 1

prs.save(Path.home() / ".nanobot" / "workspace" / "output.pptx")
```

### Status Report Template

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN
from pathlib import Path
from datetime import datetime

prs = Presentation()

# Slide 1: Title
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Project Status Report"
slide.placeholders[1].text = datetime.now().strftime("%B %Y")

# Slide 2: Executive Summary
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Executive Summary"
body = slide.placeholders[1].text_frame
body.text = "Project is on track"
body.add_paragraph().text = "Key milestone achieved"
body.add_paragraph().text = "Budget within limits"

# Slide 3: Key Metrics
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank
slide.shapes.title.text = "Key Metrics"

# Add a table
x, y, w, h = Inches(1), Inches(2), Inches(8), Inches(2)
table = slide.shapes.add_table(3, 3, x, y, w, h).table
table.columns[0].width = Inches(3)
table.columns[1].width = Inches(2.5)
table.columns[2].width = Inches(2.5)

# Headers
table.cell(0, 0).text = "Metric"
table.cell(0, 1).text = "Target"
table.cell(0, 2).text = "Actual"

# Data
table.cell(1, 0).text = "Completion"
table.cell(1, 1).text = "75%"
table.cell(1, 2).text = "78%"
table.cell(2, 0).text = "Budget"
table.cell(2, 1).text = "Rs. 5M"
table.cell(2, 2).text = "Rs. 4.8M"

# Slide 4: Next Steps
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Next Steps"
body = slide.placeholders[1].text_frame
body.text = "Complete Phase 2 development"
body.add_paragraph().text = "User acceptance testing"
body.add_paragraph().text = "Deployment preparation"

# Slide 5: Thank You
slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank or minimal
left = Inches(2)
top = Inches(3)
width = Inches(6)
height = Inches(1.5)
txBox = slide.shapes.add_textbox(left, top, width, height)
tf = txBox.text_frame
p = tf.paragraphs[0]
p.text = "Thank You"
p.font.size = Pt(44)
p.font.bold = True
p.alignment = PP_ALIGN.CENTER

prs.save(Path.home() / ".nanobot" / "workspace" / "status_report.pptx")
```

### With Images

```python
from pptx import Presentation
from pptx.util import Inches
from pathlib import Path

prs = Presentation()
workspace = Path.home() / ".nanobot" / "workspace"

slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank

# Add image
image_path = workspace / "chart.png"
if image_path.exists():
    slide.shapes.add_picture(
        str(image_path),
        left=Inches(1),
        top=Inches(1.5),
        width=Inches(8)
    )

prs.save(workspace / "with_image.pptx")
```

## Slide Layouts

| Index | Layout Type |
|-------|-------------|
| 0 | Title Slide |
| 1 | Title and Content |
| 2 | Section Header |
| 3 | Two Content |
| 4 | Comparison |
| 5 | Title Only |
| 6 | Blank |
| 7 | Content with Caption |
| 8 | Picture with Caption |

## Common Operations

| Task | Code |
|------|------|
| Add shape | `slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)` |
| Shape color | `shape.fill.solid(); shape.fill.fore_color.rgb = RgbColor(0, 112, 192)` |
| Text color | `run.font.color.rgb = RgbColor(255, 0, 0)` |
| Center text | `paragraph.alignment = PP_ALIGN.CENTER` |
| Font size | `run.font.size = Pt(24)` |
| Bold | `run.font.bold = True` |

## Token Limits

- Max output: 1024 tokens
- Generate minimal, runnable code
- No explanations unless asked
