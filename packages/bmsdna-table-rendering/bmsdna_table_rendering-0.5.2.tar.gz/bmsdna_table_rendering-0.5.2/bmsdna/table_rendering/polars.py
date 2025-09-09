from typing import TYPE_CHECKING
from bmsdna.table_rendering.config import ColumnConfig

if TYPE_CHECKING:
    import polars as pl


def configs_from_polars(df: "pl.DataFrame"):
    import polars as pl

    configs = []
    for name, dtype in df.schema.items():
        if name.startswith("_") or name.startswith("mail_"):
            continue
        if dtype == pl.Date:
            format_type = "date"
        elif dtype == pl.Datetime:
            format_type = "datetime"
        elif dtype == pl.Int64:
            format_type = "int"
        elif dtype == pl.Float64:
            format_type = "float"
        else:
            format_type = None
        configs.append(ColumnConfig(header=name, field=name, format=format_type))
    return configs
