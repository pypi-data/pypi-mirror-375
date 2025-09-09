from typing import Sequence, TYPE_CHECKING, Iterable, Callable, cast
import json
from bmsdna.table_rendering.config import ColumnConfig, ValueContext, format_value

if TYPE_CHECKING:
    import polars as pl
    from pyspark.sql import DataFrame as SparkDataFrame
    from pyspark.sql.connect.dataframe import DataFrame as SparkConnectDataFrame


def render_html(
    configs: Sequence[ColumnConfig],
    data: "Iterable[dict] | pl.DataFrame | SparkDataFrame|SparkConnectDataFrame",
    *,
    translator: Callable[[str, str], str] | None = None,
    add_classes: Sequence[str] | None = None,
    styles: str | dict[str, str] = "",
    tr_styles: str | dict[str, str] = "",
    td_styles: str | dict[str, str] = "",
):
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
    from dominate.tags import table, thead, tr, td, th, a, tbody

    tbl = table()
    with tbl.add(thead()).add(tr()):  # type: ignore
        for config in configs:
            if config.hide == True:
                continue
            h = th(config.get_header(translator))
            if config.header_title or config.header_title_key:
                h.set_attribute("title", config.get_header_title(translator))  # type: ignore

    with tbl.add(tbody()) as tbody:  # type: ignore
        for row in data_iter:
            with tbody.add(tr()) as tr_:
                if tr_styles:
                    tr_.attributes["style"] = (
                        tr_styles
                        if isinstance(tr_styles, str)
                        else "; ".join((k + ": " + v for k, v in tr_styles.items()))
                    )
                for config in configs:
                    if config.hide == True:
                        continue
                    if config.renderer:
                        value = config.renderer(
                            row if not config.field else row[config.field],
                            ValueContext(row=row, column_config=config),
                        )
                        if config.html is not False:
                            td_ = td(
                                align=(
                                    config.align
                                    if config.align
                                    else (
                                        "right"
                                        if config.format
                                        in ["int", "percentage", "float"]
                                        else None
                                    )
                                )
                            )
                            td_.add_raw_string(value)  # type: ignore
                            if td_styles:
                                td_["style"] = (  # type: ignore
                                    td_styles
                                    if isinstance(td_styles, str)
                                    else "; ".join(
                                        (k + ": " + v for k, v in td_styles.items())
                                    )
                                )

                            tr_.add(td_)  # type: ignore
                            continue

                    elif config.value_receiver:
                        value = config.value_receiver(
                            row if not config.field else row[config.field],
                            ValueContext(row=row, column_config=config),
                        )
                    elif config.field:
                        value = row[config.field]
                    else:
                        value = None
                    if value is not None and config.format is not None:
                        value = format_value(
                            value, config.format, config.format_nr_decimals
                        )
                    elif isinstance(value, (list, dict)):
                        value = json.dumps(value, default=str)
                    link = (
                        config.link(value, ValueContext(row=row, column_config=config))
                        if config.link
                        else None
                    )
                    td_ = td(
                        (
                            a(
                                value or "",
                                href=link,
                            )
                            if link
                            else value or ""
                        ),
                        align=(
                            config.align
                            if config.align
                            else (
                                "right"
                                if config.format in ["int", "percentage", "float"]
                                else None
                            )
                        ),
                    )
                    if td_styles:
                        td_["style"] = (  # type: ignore
                            td_styles
                            if isinstance(td_styles, str)
                            else "; ".join((k + ": " + v for k, v in td_styles.items()))
                        )
                    tr_.add(td_)
    if add_classes:
        existing_cls = tbl.attributes.get("class", "").split(" ")  # type: ignore
        tbl.attributes["class"] = " ".join(set(existing_cls + list(add_classes)))  # type: ignore
    if styles:
        tbl.attributes["style"] = (  # type: ignore
            styles
            if isinstance(styles, str)
            else "; ".join((k + ": " + v for k, v in styles.items()))
        )  # type: ignore
    return tbl.render(pretty=True)  # type: ignore
