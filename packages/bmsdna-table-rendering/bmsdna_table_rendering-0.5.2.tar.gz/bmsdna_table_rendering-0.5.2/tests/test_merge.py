from datetime import date, datetime, timezone
import os
import polars as pl

from bmsdna.table_rendering.table_rendering import create_excel
from pathlib import Path


def test_excel():
    fake_data = pl.DataFrame(
        data=[
            {
                "first_name": "hans",
                "last_name": "muster",
                "age": 30,
                "dt": datetime.now(tz=timezone.utc),
            },
            {
                "first_name": "max",
                "last_name": "mustermann",
                "age": 40,
                "dt": datetime.now(tz=timezone.utc),
            },
        ]
    )
    from bmsdna.table_rendering import TableRenderer

    rend = TableRenderer.from_df(fake_data).with_merged_fields(
        "name", "first_name", "last_name"
    )
    os.makedirs("tests/_data", exist_ok=True)
    create_excel(
        {"sheet1": (rend, fake_data)}, Path("tests/_data/test_excel_merge.xlsx")
    )
    rend_html = rend.render_html(
        fake_data,
        add_classes=["table", "table-striped"],
        styles="width: 100%",
        tr_styles={"background-color": "red"},
        td_styles={"border": "1px solid black", "padding": "2px"},
    )
    assert "table-striped" in rend_html
    with open("tests/_data/test_merge.html", "w", encoding="utf-8") as f:
        f.write(rend_html)
    import openpyxl

    workbook = openpyxl.load_workbook("tests/_data/test_excel_merge.xlsx")

    # Get the first sheet
    sheet = workbook.active
    assert sheet is not None
    column = sheet["A"]
    assert column[0].value == "name"
    assert column[1].value == "hans muster"

    column = sheet["B"]
    assert column[0].value == "age"
    assert column[1].value == 30
