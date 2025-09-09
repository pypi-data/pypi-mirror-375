from typing import Any, Iterable, Literal, Sequence, Callable, Mapping
from typing_extensions import TypedDict, NotRequired, TypeAlias
from pydantic import BaseModel

try:
    from xlsxwriter.worksheet import Worksheet
except ImportError:
    Worksheet = Any


def _is_pydantic_2() -> bool:
    import pydantic

    try:
        # __version__ was added with Pydantic 2 so we know if this errors the version is < 2.
        # Still check the version as a fail safe incase __version__ gets added to verion 1.
        if int(pydantic.__version__[:1]) >= 2:  # type: ignore[attr-defined]
            return True

        # Raise an AttributeError to match the AttributeError on __version__ because in either
        # case we need to get to the same place.
        raise AttributeError  # pragma: no cover
    except AttributeError:  # pragma: no cover
        return False


is_pydantic_2 = _is_pydantic_2()

if is_pydantic_2:
    from pydantic import ConfigDict


class ValueContext(BaseModel):
    row: dict[str, Any]
    column_config: "ColumnConfig"

    def __getitem__(self, key: str) -> Any:
        return self.row[key]

    def get(self, key: str) -> Any:
        return self.row.get(key)


class ExcelValueContext(ValueContext):
    if is_pydantic_2:
        model_config = ConfigDict(arbitrary_types_allowed=True)  # type: ignore
    if not is_pydantic_2:

        class Config:
            arbitrary_types_allowed = True

    format: Any


FORMAT_TYPE = Literal[
    "date", "datetime", "int", "float", "percentage", "currency:chf", "currency:eur"
]


class ColumnConfig(BaseModel):
    """Config for columns"""

    """
        The translation key of apptexts.toml
        If a 2-tuple is provided, the first one is the key and the 2nd one the default value
    """
    header: str | None = None

    header_key: str | tuple[str, str] | None = None
    """
    Tooltip for header"""
    header_title: str | None = None

    """
    Tooltip for header"""
    header_title_key: str | tuple[str, str] | None = None

    link: Callable[[Any, ValueContext], str | None] | None = None
    field: str | None = None
    value_receiver: Callable[[Any, ValueContext], Any] | None = None
    format: FORMAT_TYPE | None = None
    format_nr_decimals: int | None = None
    align: Literal["left", "center", "right"] | None = None
    text_wrap: bool = False

    searchable: bool = True
    search_field: str | Sequence[str] | None = None

    hide: bool | Literal["mobile"] = False

    sortable: bool = False
    filterable: bool = True

    width: int | None = None  # in px. currently nicegui only

    flex: int | None = None
    html: bool | None = None  # defaults to true if there is a renderer
    renderer: Callable[[Any, ValueContext], str] | None = None
    autoHeight: bool = False

    excel_writer: "Callable[[Any, Worksheet, tuple[int, int], ExcelValueContext], None] | None" = None  # type: ignore

    def get_header(self, _translator: Callable[[str, str], str] | None = None) -> str:
        if self.header:
            return self.header
        if self.header_key is None:
            assert self.field is not None, "Must provider header or header_key or field"
            return self.field
        assert _translator is not None, "No translator provided"
        if isinstance(self.header_key, str):
            return _translator(self.header_key, self.header_key)
        return _translator(*self.header_key)

    def get_header_title(
        self, _translator: Callable[[str, str], str] | None = None
    ) -> str | None:
        if self.header_title:
            return self.header_title
        if self.header_title_key is None:
            return None
        assert _translator is not None, "No translator provided"
        if isinstance(self.header_title_key, str):
            return _translator(self.header_title_key, self.header_title_key)
        return _translator(*self.header_title_key)


class OverwrittenConfigDict(TypedDict):
    header: NotRequired[str]

    """Title / Tooltip of header
    """
    header_title: NotRequired[str]

    header_key: NotRequired[str | tuple[str, str]]
    link: NotRequired[Callable[[Any, ValueContext], str | None]]
    field: NotRequired[str]
    value_receiver: NotRequired[Callable[[Any, ValueContext], Any]]
    format: NotRequired[FORMAT_TYPE]
    format_nr_decimals: NotRequired[int]
    align: NotRequired[Literal["left", "center", "right"]]
    text_wrap: NotRequired[bool]


def format_value(value: Any, format_type: FORMAT_TYPE, format_nr_decimals: int | None):
    if value is None:
        return ""
    if format_type == "date":
        return value.strftime("%d.%m.%Y")
    if format_type == "datetime":
        return value.strftime("%d.%m.%Y %H:%M")
    if format_type == "int" and (format_nr_decimals is None or format_nr_decimals == 0):
        return format(int(value), ",").replace(",", "'")
    if format_type == "float":
        nr_dec = format_nr_decimals if format_nr_decimals is not None else 2
        return format(value, f",.{nr_dec}f").replace(",", "'")
    if format_type == "percentage":
        nr_dec = format_nr_decimals if format_nr_decimals is not None else 2
        return format(value, f",.{nr_dec}%").replace(",", "'")
    if format_type.startswith("currency:"):
        currency_symbol = format_type.split(":")[1].upper()
        return f"{currency_symbol} {format_value(value, 'float' if format_nr_decimals and format_nr_decimals > 0 else 'int', format_nr_decimals)}"
    return str(value)


def get_excel_format(FORMAT_TYPE: str, format_nr_decimals: int | None):
    decimal_format = None
    if format_nr_decimals is not None:
        if format_nr_decimals == 0:
            decimal_format = ""
        else:
            decimal_format = "." + ("0" * format_nr_decimals)
    if FORMAT_TYPE == "date":
        return "dd.mm.yyyy"
    if FORMAT_TYPE == "datetime":
        return "dd.mm.yyyy hh:mm:ss"
    if FORMAT_TYPE == "int":
        decimal_format = decimal_format or ""
        return "#,##0" + decimal_format
    if FORMAT_TYPE == "float":
        decimal_format = decimal_format or ".00"
        return "#,##0" + decimal_format
    if FORMAT_TYPE == "percentage":
        return (
            "0" + ("." + "0" * format_nr_decimals if format_nr_decimals else "") + "%"
        )
    if FORMAT_TYPE.startswith("currency:"):
        currency_symbol = FORMAT_TYPE.split(":")[1].upper()
        decimal_format = decimal_format or ""
        acc = f'_ "{currency_symbol}"\\ * #,##0{decimal_format}_ ;_ "{currency_symbol}"\\ * \\-#,##0{decimal_format}_ ;_ "{currency_symbol}"\\ * "-"??_ ;_ @_ '
        return acc
    return "General"


def overwrite_configs(
    configs: Iterable[ColumnConfig],
    overwritten_configs: Mapping[
        str, ColumnConfig | OverwrittenConfigDict | Literal["remove"]
    ],
):
    """Returns a new instance with overwritten column configs. If a column is not present in the overwritten_configs, the original config is used.
    If the overwritten config is an instance of ColumnConfig, the whole config is replaced. If it is a dict, only the specified fields are replaced.
    """

    def _merge(
        config: ColumnConfig, overwrite: ColumnConfig | OverwrittenConfigDict | None
    ) -> ColumnConfig:
        if overwrite is None:
            return config
        if isinstance(overwrite, ColumnConfig):
            return overwrite
        if not is_pydantic_2:
            return config.copy(update=overwrite)  # type: ignore
        return config.model_copy(update=overwrite)  # type: ignore

    tuples = [
        (
            c,
            overwritten_configs.get(
                c.field
                or (
                    c.header_key
                    if isinstance(c.header_key, str)
                    else c.header_key[0]
                    if c.header_key
                    else None
                )
                or c.header
                or "_____"
            ),
        )
        for c in configs
    ]
    return [
        _merge(
            c,
            o,  # type: ignore
        )
        for c, o in tuples
        if o != "remove"
    ]


if not is_pydantic_2:
    ValueContext.update_forward_refs()
