text = """# Ein Titel

Wir haben hier einen Text

[ - Ein link](https://google.com)

| Month    | Savings |
| -------- | ------- |
| January  | $250    |
| February | $80     |
| March    | $420    |

**Test 2**

|                      |     |        |
| -------------------- | --- | ------ |
| Table without header | 8   | visite |
| tester           | 8   | visite |
| Hello | 10  | visite |
| ojiwoejoiwe | 8   | visite |

You have **Test3** to do.
_tester_ is a cursive start test | asfd _t_ | testser ***est*** _er_.
"""


def test_markdown():
    from bmsdna.table_rendering.md2excel import markdown_to_excel
    import xlsxwriter

    with xlsxwriter.Workbook("tests/_data/test_md.xlsx") as wb:
        ws = wb.add_worksheet("tester")
        ws.write(0, 3, "tester title")
        markdown_to_excel(text, ws, wb, offset_rows=2)
