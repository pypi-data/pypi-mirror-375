# Library for config-based rendering tables to html or excel

Allows to create a config based on pydantic BaseModel:

```python
from bmsdna.table_rendering import markdown_to_excel, ColumnConfig, TableRenderer

my_cols = [
    ColumnConfig(header_key="mail.date", field="start", format="datetime"),
    ColumnConfig(
        header="MyTool",
        align="left",
        field="customer_id",
        link=lambda _, c: some_tool_link(c.get("customer_id"), c.get("lng_code")),
    ),
    ColumnConfig(
        header="PDF",
        align="left",
        field="customer_id",
        link=lambda _, c: maybe_some_pdf_link(c.get("customer_id"), c.get("lng_code")),
    ),
    ColumnConfig(
        header_key="mail.subject",
        field="subject",
    ),
    ColumnConfig(
        header_key="customer.sales_l12m",
        field="sales_amount_l12m",
        format="float",
        format_nr_decimals=0,
    )
]
lng_code = "de"
lng_table_config = TableRenderer(
    my_cols,
    translator=lambda k, d: get_app_text(k, lng_code, d),
)
# we can make some html
html:str = lng_table_config.render_html(some_list_data)

# or also an excel
with xlsxwriter.Workbook() as wb:
    ws = ws.add_worksheet("sheet1")

    # we can also write some markdown to excel

    markdown_to_excel("# Ein Titel\nWir haben hier einen Text", ws, wb)

    # and add the table to it
    lng_table_config.render_into_sheet(some_list_data, ws, wb, offset_rows=10)

```

We use it internally to create Emails with Excel attachments
