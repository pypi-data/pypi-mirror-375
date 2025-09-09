from typing import TYPE_CHECKING
from bmsdna.table_rendering.config import ColumnConfig

if TYPE_CHECKING:
    from pyspark.sql import DataFrame
    from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDataFrame


def configs_from_pyspark(df: "DataFrame|SparkConnectDataFrame"):
    from pyspark.sql.types import (
        DateType,
        TimestampType,
        IntegerType,
        FloatType,
        LongType,
        DoubleType,
        DecimalType,
    )

    configs = []
    for field in df.schema.fields:
        name = field.name
        dtype = field.dataType
        format_nr_decimals = None

        if name.startswith("_") or name.startswith("mail_"):
            continue
        if isinstance(dtype, DateType):
            format_type = "date"
        elif isinstance(dtype, TimestampType):
            format_type = "datetime"
        elif isinstance(dtype, IntegerType) or isinstance(dtype, LongType):
            format_type = "int"
        elif isinstance(dtype, DecimalType):
            format_type = "int" if dtype.scale == 0 else "float"
            format_nr_decimals = dtype.scale
        elif isinstance(dtype, FloatType) or isinstance(dtype, DoubleType):
            format_type = "float"
        else:
            format_type = None
        configs.append(
            ColumnConfig(
                header=name,
                field=name,
                format=format_type,
                format_nr_decimals=format_nr_decimals,
            )
        )
    return configs
