---
name: office-excel
description: Generate Excel files using openpyxl (workspace only)
homepage: https://openpyxl.readthedocs.io/
metadata: {"nanobot":{"emoji":"📊","requires":{"bins":["python3"]}}}
---

# Excel Generation with openpyxl

Create and manipulate Excel files using Python's openpyxl library.

## Requirements

```bash
pip install openpyxl
```

## Usage

Ask to create Excel files:
```
Create an Excel file with sales data for January
```

Or:
```
Generate a spreadsheet with employee attendance
```

## Output Rules

1. **Workspace only**: Files saved to workspace directory
2. **Minimal code**: No unnecessary comments or explanations
3. **Direct execution**: Code should run without modification

## Basic Templates

### Simple Data Table

```python
from openpyxl import Workbook
from pathlib import Path

wb = Workbook()
ws = wb.active
ws.title = "Data"

# Headers
headers = ["Name", "Amount", "Date"]
for col, header in enumerate(headers, 1):
    ws.cell(row=1, column=col, value=header)

# Data
data = [
    ["Item A", 1000, "2024-01-15"],
    ["Item B", 2500, "2024-01-16"],
]
for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        ws.cell(row=row_idx, column=col_idx, value=value)

# Save to workspace
wb.save(Path.home() / ".nanobot" / "workspace" / "output.xlsx")
```

### With Formatting

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from pathlib import Path

wb = Workbook()
ws = wb.active

# Style definitions
header_font = Font(bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)

# Headers with formatting
headers = ["Product", "Quantity", "Unit Price", "Total"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")
    cell.border = border

wb.save(Path.home() / ".nanobot" / "workspace" / "formatted.xlsx")
```

### With Formulas

```python
from openpyxl import Workbook
from pathlib import Path

wb = Workbook()
ws = wb.active

# Data with formula
ws["A1"] = "Quantity"
ws["B1"] = "Price"
ws["C1"] = "Total"

ws["A2"] = 10
ws["B2"] = 250
ws["C2"] = "=A2*B2"  # Formula

ws["A3"] = 5
ws["B3"] = 500
ws["C3"] = "=A3*B3"

# Sum formula
ws["C4"] = "=SUM(C2:C3)"

wb.save(Path.home() / ".nanobot" / "workspace" / "with_formulas.xlsx")
```

### Multiple Sheets

```python
from openpyxl import Workbook
from pathlib import Path

wb = Workbook()

# Sheet 1: Summary
ws1 = wb.active
ws1.title = "Summary"
ws1["A1"] = "Monthly Report"

# Sheet 2: Details
ws2 = wb.create_sheet("Details")
ws2["A1"] = "Transaction ID"
ws2["B1"] = "Amount"

# Sheet 3: Charts data
ws3 = wb.create_sheet("Chart Data")
ws3["A1"] = "Month"
ws3["B1"] = "Revenue"

wb.save(Path.home() / ".nanobot" / "workspace" / "multi_sheet.xlsx")
```

## Common Operations

| Task | Code |
|------|------|
| Set column width | `ws.column_dimensions['A'].width = 20` |
| Set row height | `ws.row_dimensions[1].height = 30` |
| Merge cells | `ws.merge_cells('A1:C1')` |
| Auto-filter | `ws.auto_filter.ref = "A1:D10"` |
| Freeze panes | `ws.freeze_panes = "A2"` |
| Number format | `cell.number_format = '#,##0.00'` |
| Date format | `cell.number_format = 'YYYY-MM-DD'` |
| Currency (LKR) | `cell.number_format = 'Rs. #,##0.00'` |

## Token Limits

- Max output: 1024 tokens
- Generate minimal, runnable code
- No explanations unless asked
