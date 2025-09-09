import os
import re

from ..utils.misc import save_image


def escape_markdown_special_chars(text):
    special_chars = r"([`*{}[\]()#+!~|-])"
    return re.sub(special_chars, r"\\\1", text)


def paragraph_to_md(paragraph, ignore_line_break):
    contents = escape_markdown_special_chars(paragraph.contents)

    if ignore_line_break:
        contents = contents.replace("\n", "")
    else:
        contents = contents.replace("\n", "<br>")

    if paragraph.role == "section_headings":
        contents = "# " + contents

    return {
        "order": paragraph.order,
        "box": paragraph.box,
        "md": contents + "\n",
    }


def table_to_md(table, ignore_line_break):
    num_rows = table.n_row
    num_cols = table.n_col

    table_array = [["" for _ in range(num_cols)] for _ in range(num_rows)]

    for cell in table.cells:
        row = cell.row - 1
        col = cell.col - 1
        row_span = cell.row_span
        col_span = cell.col_span
        contents = cell.contents

        for i in range(row, row + row_span):
            for j in range(col, col + col_span):
                contents = escape_markdown_special_chars(contents)
                if ignore_line_break:
                    contents = contents.replace("\n", "")
                else:
                    contents = contents.replace("\n", "<br>")

                if i == row and j == col:
                    table_array[i][j] = contents

    table_md = ""
    for i in range(num_rows):
        row = "|".join(table_array[i])
        table_md += f"|{row}|\n"

        if i == 0:
            header = "|".join(["-" for _ in range(num_cols)])
            table_md += f"|{header}|\n"

    return {
        "order": table.order,
        "box": table.box,
        "md": table_md,
    }


def figure_to_md(
    figures,
    img,
    out_path,
    export_figure_letter=False,
    ignore_line_break=False,
    width=200,
    figure_dir="figures",
):
    assert img is not None, "img is required for saving figures"

    elements = []
    for i, figure in enumerate(figures):
        x1, y1, x2, y2 = map(int, figure.box)
        figure_img = img[y1:y2, x1:x2, :]
        save_dir = os.path.dirname(out_path)
        save_dir = os.path.join(save_dir, figure_dir)
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.splitext(os.path.basename(out_path))[0]
        figure_name = f"{filename}_figure_{i}.png"
        figure_path = os.path.join(save_dir, figure_name)
        save_image(figure_img, figure_path)

        elements.append(
            {
                "order": figure.order,
                "md": f'<img src="{figure_dir}/{figure_name}" width="{width}px"><br>',
            }
        )

        if export_figure_letter:
            paragraphs = sorted(figure.paragraphs, key=lambda x: x.order)
            for paragraph in paragraphs:
                element = paragraph_to_md(paragraph, ignore_line_break)
                element = {
                    "order": figure.order,
                    "md": element["md"],
                }
                elements.append(element)

    return elements


def convert_markdown(
    inputs,
    out_path,
    ignore_line_break=False,
    img=None,
    export_figure_letter=False,
    export_figure=True,
    figure_width=200,
    figure_dir="figures",
):
    elements = []
    for table in inputs.tables:
        elements.append(table_to_md(table, ignore_line_break))

    for paragraph in inputs.paragraphs:
        elements.append(paragraph_to_md(paragraph, ignore_line_break))

    if export_figure:
        elements.extend(
            figure_to_md(
                inputs.figures,
                img,
                out_path,
                export_figure_letter,
                ignore_line_break,
                figure_width,
                figure_dir=figure_dir,
            )
        )

    elements = sorted(elements, key=lambda x: x["order"])
    markdown = "\n".join([element["md"] for element in elements])
    return markdown, elements


def export_markdown(
    inputs,
    out_path: str,
    ignore_line_break: bool = False,
    img=None,
    export_figure_letter=False,
    export_figure=True,
    figure_width=200,
    figure_dir="figures",
    encoding: str = "utf-8",
):
    markdown, elements = convert_markdown(
        inputs,
        out_path,
        ignore_line_break,
        img,
        export_figure_letter,
        export_figure,
        figure_width,
        figure_dir,
    )

    save_markdown(markdown, out_path, encoding)
    return markdown


def save_markdown(
    markdown,
    out_path,
    encoding,
):
    with open(out_path, "w", encoding=encoding, errors="ignore") as f:
        f.write(markdown)
