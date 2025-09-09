from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import xlsxwriter
    from xlsxwriter.format import Format
    from xlsxwriter.worksheet import Worksheet
    from xlsxwriter.workbook import Workbook
import re

re_markdown_link = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
re_markdown_image = re.compile(r"\!\[([^\]]+)\]\(([^)]+)\)")

re_formatted = [
    re.compile(r"([\*]{1,3}[^\*]+[\*]{1,3})"),
    re.compile(r"([_]{1,3}[^_]+[_]{1,3})"),
]


def markdown_to_excel(
    md: str | Path, ws: "Worksheet", wb: "Workbook", *, offset_rows=0
):
    if isinstance(md, Path):
        md = md.read_text(encoding="utf-8-sig")
    lines = md.split("\n")
    from xlsxwriter.format import Format

    heading_formats: dict[int, Format] = {}

    row = 0
    table_start = None
    is_table = False
    table_headers = None
    table_col_count = None
    format_italic = None
    format_bold = None
    format_italic_bold = None
    for line in lines:
        col_ind = 0
        if line.startswith("|") and line.endswith("|"):
            line = line[1:-1]
            table_headers = (
                [c.strip() for c in line.split("|")]
                if not table_headers
                else table_headers
            )

            table_start = row if not table_start else table_start
        else:
            if is_table and table_start is not None:
                end_row = row - 1
                if table_headers is not None and all((not t for t in table_headers)):
                    table_headers = None
                if table_headers:
                    opts = {
                        "header_row": True,
                        "columns": [{"header": h} for h in table_headers],
                    }
                else:
                    opts = {
                        "header_row": False,
                    }
                ws.add_table(
                    table_start + offset_rows,
                    0,
                    end_row + offset_rows,
                    (table_col_count or 0) - 1,
                    opts,
                )
            table_start = None
            table_headers = None
        if (
            all(char == "-" or char == "|" or char == " " for char in line)
            and len(line) > 5
        ):
            table_col_count = len(line.split("|"))
            is_table = True
            continue  # markdown table thing
        cols = line.split(" | ")
        for col in cols:
            col = col.strip()
            if m := re_markdown_image.match(col):
                ws.insert_image(offset_rows + row, col_ind, m.group(2))
            elif m := re_markdown_link.match(col):
                url = m.group(2)
                text = m.group(1)
                if "://" in text and "://" not in url:
                    text, url = url, text

                ws.write_url(offset_rows + row, col_ind, url, string=text)
            elif (
                col.startswith("# ")
                or col.startswith("## ")
                or col.startswith("### ")
                or col.startswith("#### ")
            ):
                heading_index = len(col.split(" ")[0])
                format = heading_formats.get(heading_index)
                if not format:
                    sizes = {1: 18, 2: 16, 3: 14, 4: 12}
                    heading_formats[heading_index] = wb.add_format(
                        {"font_size": sizes[heading_index], "bold": True}
                    )
                    format = heading_formats[heading_index]
                val = col[heading_index + 1 :].strip()
                ws.write(offset_rows + row, col_ind, val, format)
            elif (col.startswith("***") and col.endswith("***")) or (
                col.startswith("___") and col.endswith("___")
            ):
                if not format_italic_bold:
                    format_italic_bold = wb.add_format({"italic": True, "bold": True})
                ws.write(offset_rows + row, col_ind, col[3:-3], format_italic_bold)
            elif (col.startswith("**") and col.endswith("**")) or (
                col.startswith("__") and col.endswith("__")
            ):
                if not format_bold:
                    format_bold = wb.add_format({"bold": True})
                ws.write(offset_rows + row, col_ind, col[2:-2], format_bold)
            elif (col.startswith("*") and col.endswith("*")) or (
                col.startswith("_") and col.endswith("_")
            ):
                if not format_italic:
                    format_italic = wb.add_format({"italic": True})
                ws.write(offset_rows + row, col_ind, col[1:-1], format_italic)
            elif "*" in col or "_" in col:
                matches: list[re.Match[str]] = []
                for r in re_formatted:
                    matches += list(r.finditer(col))
                if not matches:
                    ws.write(offset_rows + row, col_ind, col)
                else:
                    matches = sorted(matches, key=lambda m: m.start())
                    start = 0
                    result = []
                    std_format = wb.add_format()

                    for m in matches:
                        before_txt = col[start : m.start()]
                        if before_txt:
                            result.append(before_txt)
                        match_txt = m.group(1)
                        if (
                            match_txt.startswith("___") and match_txt.endswith("___")
                        ) or (
                            match_txt.startswith("***") and match_txt.endswith("***")
                        ):
                            if not format_italic_bold:
                                format_italic_bold = wb.add_format(
                                    {"italic": True, "bold": True}
                                )
                            format = format_italic_bold
                            real_txt = match_txt[3:-3]
                        elif (
                            match_txt.startswith("**") and match_txt.endswith("**")
                        ) or (match_txt.startswith("__") and match_txt.endswith("__")):
                            if not format_bold:
                                format_bold = wb.add_format({"bold": True})
                            format = format_bold
                            real_txt = match_txt[2:-2]
                        elif (
                            match_txt.startswith("*") and match_txt.endswith("*")
                        ) or (match_txt.startswith("_") and match_txt.endswith("_")):
                            if not format_italic:
                                format_italic = wb.add_format({"italic": True})
                            format = format_italic
                            real_txt = match_txt[1:-1]
                        else:
                            format = std_format
                            real_txt = match_txt

                        result.append(format)
                        result.append(real_txt)

                        start = m.end()
                    if start < len(col):
                        result.append(col[start:])
                    ws.write_rich_string(offset_rows + row, col_ind, *result)

            else:
                ws.write(offset_rows + row, col_ind, col)
            col_ind += 1
        row += 1

    return row + offset_rows - 1
