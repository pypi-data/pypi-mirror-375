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
    overload,
)
from typing_extensions import NotRequired, TypedDict
from uuid import uuid4
from pydantic import BaseModel

from bmsdna.table_rendering.excel import SheetOptions
from .config import (
    OverwrittenConfigDict,
    ColumnConfig,
    ValueContext,
    format_value,
    get_excel_format,
)

if TYPE_CHECKING:
    from xlsxwriter.worksheet import Worksheet
    from xlsxwriter.workbook import Workbook
    import polars as pl
    from pyspark.sql import DataFrame as SparkDataFrame
    from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDataFrame


class TableRenderer:
    def __init__(
        self,
        configs: Sequence[ColumnConfig],
        translator: Callable[[str, str], str] | None = None,
    ):
        self.configs = configs
        self.translator = translator

    @classmethod
    def from_spark(
        cls,
        data: "SparkDataFrame|SparkConnectDataFrame",
        translator: Callable[[str, str], str] | None = None,
    ):
        from .spark import configs_from_pyspark

        return cls(configs_from_pyspark(data), translator=translator)

    @classmethod
    def from_df(
        cls, data: "pl.DataFrame", translator: Callable[[str, str], str] | None = None
    ):
        from .polars import configs_from_polars

        return cls(configs_from_polars(data), translator=translator)

    def _translate(self, key: str, default: str | None = None) -> str:
        if self.translator:
            return self.translator(key, default or key)
        raise ValueError("No translator provided")

    def with_overwritten_configs(
        self,
        overwritten_configs: Mapping[
            str, ColumnConfig | OverwrittenConfigDict | Literal["remove"]
        ],
    ):
        """Returns a new instance with overwritten column configs. If a column is not present in the overwritten_configs, the original config is used.
        If the overwritten config is an instance of ColumnConfig, the whole config is replaced. If it is a dict, only the specified fields are replaced.
        """
        from .config import overwrite_configs

        return TableRenderer(
            overwrite_configs(self.configs, overwritten_configs),
        )

    def with_merged_fields(self, new_name: str, *field_names: str):
        """Returns a new instance with a new column that is a concatenation of the specified fields.

        Args:
            new_name: The name of the new column
        """

        def value_receiver(f: str, ctx: ValueContext) -> Any:
            concat_str = ""
            for c in self.configs:
                if c.field in field_names:
                    if c.value_receiver:
                        value = c.value_receiver(
                            ctx.row if not c.field else ctx.row[c.field],
                            ctx,
                        )
                        concat_str += value + " "
                    else:
                        concat_str += str(ctx.row[c.field]) + " "
            return concat_str.removesuffix(" ")

        new_cfgs = list(self.configs)

        index = 0
        for c in self.configs:
            if c.field in field_names:
                index = new_cfgs.index(c)
                new_cfgs.remove(c)
            if c.field is None and c.header is not None and c.header in field_names:
                new_cfgs.remove(c)
        new_cfgs.insert(
            index, ColumnConfig(header=new_name, value_receiver=value_receiver)
        )

        return TableRenderer(new_cfgs)

    def with_translator(self, translator: Callable[[str, str], str]):
        return TableRenderer(self.configs, translator)

    def render_html(
        self,
        data: "Iterable[dict] | pl.DataFrame | SparkDataFrame|SparkConnectDataFrame",
        *,
        add_classes: Sequence[str] | None = None,
        styles: str | dict[str, str] = "",
        tr_styles: str | dict[str, str] = "",
        td_styles: str | dict[str, str] = "",
    ):
        from .html import render_html

        return render_html(
            self.configs,
            data,
            translator=self.translator,
            add_classes=add_classes,
            styles=styles,
            tr_styles=tr_styles,
            td_styles=td_styles,
        )

    def render_into_sheet(
        self,
        ws: "Worksheet",
        wb: "Workbook",
        data: "Iterable[dict] | pl.DataFrame | SparkDataFrame|SparkConnectDataFrame",
        sheet_options: SheetOptions = {},
        *,
        offset_rows: int = 0,
    ):
        from .excel import render_into_sheet

        return render_into_sheet(
            self.configs,
            data,
            ws,
            wb,
            sheet_options,
            translator=self.translator,
            offset_rows=offset_rows,
        )


@overload
def create_excel(
    sheets: "Mapping[str, tuple[TableRenderer, Sequence[dict]| pl.DataFrame | SparkDataFrame]|tuple[TableRenderer, Sequence[dict]| pl.DataFrame| SparkDataFrame, SheetOptions]]",
    excel: Path | None,
    *,
    workbook_options: dict | None = None,
) -> Path: ...


@overload
def create_excel(
    sheets: "Mapping[str, tuple[TableRenderer, Sequence[dict]| pl.DataFrame| SparkDataFrame]|tuple[TableRenderer, Sequence[dict]| pl.DataFrame| SparkDataFrame, SheetOptions]]",
    *,
    workbook_options: dict | None = None,
) -> Path: ...


@overload
def create_excel(
    sheets: "Mapping[str, tuple[TableRenderer, Sequence[dict]| pl.DataFrame| SparkDataFrame]|tuple[TableRenderer, Sequence[dict]| pl.DataFrame| SparkDataFrame, SheetOptions]]",
    excel: "Workbook",
) -> None: ...


def create_excel(
    sheets: "Mapping[str, tuple[TableRenderer, Sequence[dict]| pl.DataFrame| SparkDataFrame]|tuple[TableRenderer, Sequence[dict]| pl.DataFrame| SparkDataFrame, SheetOptions]]",
    excel: "Path | Workbook | None" = None,
    *,
    workbook_options: dict | None = None,
) -> Path | None:
    if excel is None:
        excel = Path(os.getenv("TEMP", "/tmp")) / f"{str(uuid4())}.xlsx"
    import xlsxwriter
    from xlsxwriter.workbook import Workbook

    wb = None
    owns_excel = True
    try:
        if isinstance(excel, Workbook):
            owns_excel = False
            wb = excel
            path = None
        else:
            wb = Workbook(
                excel,
                workbook_options
                or {
                    "remove_timezone": True,
                },
            )
            path = excel

        for sheet_name, tpl in sheets.items():
            (renderer, data) = tpl if len(tpl) == 2 else tpl[:2]
            options = tpl[2] if len(tpl) == 3 else SheetOptions()

            ws = wb.add_worksheet(name=sheet_name)
            renderer.render_into_sheet(ws, wb, data, options)
    finally:
        if wb is not None and owns_excel:
            wb.close()
    return path
