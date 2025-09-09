from datetime import datetime
import os
from pathlib import Path
from typing import (
    Callable,
    Any,
    TYPE_CHECKING,
    Iterable,
    Literal,
    Mapping,
    Sequence,
    cast,
)
from typing_extensions import NotRequired, TypedDict
from uuid import uuid4
import json
from pydantic import BaseModel
from .config import (
    ExcelValueContext,
    OverwrittenConfigDict,
    ColumnConfig,
    ValueContext,
    get_excel_format,
)

if TYPE_CHECKING:
    from xlsxwriter.worksheet import Worksheet
    from xlsxwriter.workbook import Workbook
    import polars as pl
    from pyspark.sql import DataFrame as SparkDataFrame
    from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDataFrame


class SheetOptions(TypedDict):
    freeze_panes: NotRequired[tuple[int, int]]
    max_col_width: NotRequired[int]


def render_into_sheet(
    configs: Sequence[ColumnConfig],
    data: "Iterable[dict] | pl.DataFrame| SparkDataFrame|SparkConnectDataFrame",
    ws: "Worksheet",
    wb: "Workbook",
    sheet_options: SheetOptions = {},
    *,
    translator: Callable[[str, str], str] | None = None,
    offset_rows=0,
    autofit=True,
    table_name: str | None = None,
) -> "Worksheet":
    data_iter: Iterable[dict] | None = None
    if data is None:
        data_iter = []
    if data_iter is None:
        try:
            from pyspark.sql import DataFrame as SparkDataFrame

            if isinstance(data, SparkDataFrame):
                data_iter = (d.asDict(True) for d in data.collect())
        except ImportError:
            pass
        try:
            from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDataFrame

            if isinstance(data, SparkConnectDataFrame):
                data_iter = (d.asDict(True) for d in data.collect())
        except ImportError:
            pass
    if data_iter is None:
        try:
            import polars as pl

            if isinstance(data, pl.DataFrame):
                data_iter = data.iter_rows(named=True)
            else:
                data_iter = cast(Sequence[dict], data)
        except ImportError:
            data_iter = data  # type: ignore
    assert data_iter is not None, f"Unknown data type for data: {type(data)}"
    import xlsxwriter

    ws.write_row(
        offset_rows,
        0,
        [config.get_header(translator) for config in configs],
    )
    col_ind = -1
    for c in configs:
        col_ind += 1
        if c.header_title or c.header_title_key:
            ws.write_comment(offset_rows, col_ind, c.get_header_title(translator))
    row_ind = offset_rows
    formats = []
    for i, config in enumerate(configs):
        format_dict = {
            "align": config.align if config.align else None,
            "num_format": (
                get_excel_format(config.format or "float", config.format_nr_decimals)
                if config.format or config.format_nr_decimals is not None
                else None
            ),
            "hyperlink": True if config.link else None,
            "text_wrap": config.text_wrap,
        }
        formats.append(
            wb.add_format({f: v for f, v in format_dict.items() if v is not None})
        )
    for row in data_iter:
        row_ind += 1
        for i, config in enumerate(configs):
            value = (
                config.value_receiver(
                    row if not config.field else row[config.field],
                    ValueContext(row=row, column_config=config),
                )
                if config.value_receiver
                else row[config.field]
                if config.field
                else None
            )
            link = (
                config.link(value, ValueContext(row=row, column_config=config))
                if config.link and value is not None and value != ""
                else None
            )
            if config.excel_writer:
                config.excel_writer(
                    value,
                    ws,
                    (row_ind, i),
                    ExcelValueContext(row=row, column_config=config, format=formats[i]),
                )
            elif link:
                ws.write_url(
                    row_ind,
                    i,
                    link,
                    string=str(value) if value is not None else None,
                    cell_format=formats[i],
                )
            elif config.format in ["percentage", "int", "float"] and isinstance(
                value, str
            ):
                ws.write(row_ind, i, float(value), formats[i])
            elif isinstance(value, (list, dict)):
                ws.write(row_ind, i, json.dumps(value, default=str), formats[i])
            else:
                ws.write(row_ind, i, value, formats[i])

    assert ws.name is not None
    if table_name is None:
        t_name = ws.name.replace(" ", "_")
        existing_names = set(t["name"].lower() for t in ws.tables if t.get("name"))
        cnt = 2
        while t_name.lower() in existing_names:
            t_name = ws.name.replace(" ", "_") + "_" + str(cnt)
            cnt += 1
        table_name = t_name
    ws.add_table(
        offset_rows,
        0,
        row_ind,
        len(configs) - 1,
        {
            "name": table_name,
            "style": "Table Style Medium 2",
            "columns": [
                {"header": config.get_header(translator)} for config in configs
            ],
        },
    )
    if autofit:
        ws.autofit()

    fp = sheet_options.get("freeze_panes", None)
    if fp:
        ws.freeze_panes(*fp)
    max_col_width = sheet_options.get("max_col_width", None)
    if max_col_width:
        for _, value in ws.col_info.items():
            if value[0] > max_col_width:
                value[0] = max_col_width
    for i, config in enumerate(configs):
        if config.hide == True:
            ws.set_column(i, i, None, None, {"hidden": True})
    return ws
