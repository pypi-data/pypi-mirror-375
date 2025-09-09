from datetime import date, datetime
import os
import polars as pl

from bmsdna.table_rendering.table_rendering import create_excel
from pathlib import Path


def test_excel():
    fake_data = pl.DataFrame(
        data=[
            {
                "a": 1,
                "b": 2.0,
                "chf": 234,
                "chf2": 234.67,
                "date": date.fromisoformat("2022-01-01"),
                "datetime": datetime.fromisoformat("2022-01-01 12:00:00"),
            },
            {
                "a": 2,
                "b": 3.0,
                "chf": 2345,
                "chf2": 2343.67,
                "date": date.fromisoformat("2025-01-01"),
                "datetime": datetime.fromisoformat("2022-01-01 18:00:00"),
            },
        ],
        schema_overrides={"date": pl.Date, "datetime": pl.Datetime},
    )
    from bmsdna.table_rendering import TableRenderer

    rend = TableRenderer.from_df(fake_data).with_overwritten_configs(
        {
            "a": {"format": "int"},
            "b": {"format": "float", "header_title": "B is a great col"},
            "chf": {"format": "currency:chf"},
            "chf2": {"format": "currency:chf"},
        }
    )
    os.makedirs("tests/_data", exist_ok=True)
    create_excel({"sheet1": (rend, fake_data)}, Path("tests/_data/test_excel.xlsx"))
    import openpyxl

    workbook = openpyxl.load_workbook("tests/_data/test_excel.xlsx")

    # Get the first sheet
    sheet = workbook.active
    assert sheet is not None
    # Get the number format in the "chf" column
    column_letter = "D"  # Assuming "chf" is in column C
    column = sheet[column_letter]
    assert column[0].value == "chf2"
    assert column[1].value == 234.67
    assert "CHF" in column[1].number_format
