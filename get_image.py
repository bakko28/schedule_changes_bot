import markdown
import asyncio
from datetime import date
from PIL import Image, ImageDraw, ImageFont

async def markdown_to_table(md_text):
    rows = md_text.strip().split("\n")
    
    table = [row.split("|")[1:-1] for row in rows if "|" in row]
    return table

async def draw_table_image(table, output_file=f"img/{date.today()}.png"):
    font_path = "fonts/Roboto_Condensed-Regular.ttf"
    font_size = 18
    font = ImageFont.truetype(font_path, font_size)
    padding = 8
    kerning = 0.8

    cell_widths = [
        max(font.getlength(cell.strip()) + kerning * len(cell.strip()) for cell in col) + 2 * padding
        for col in zip(*table)
    ]
    cell_height = font.getbbox("A")[3] + 2 * padding

    img_width = int(sum(cell_widths))
    img_height = int(cell_height * len(table))

    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)

    y = 0
    for row in table:
        x = 0
        for i, cell in enumerate(row):
            cell_x1 = int(x)
            cell_y1 = int(y)
            cell_x2 = int(x + cell_widths[i])
            cell_y2 = int(y + cell_height)
            
            draw.rectangle([cell_x1, cell_y1, cell_x2, cell_y2], outline="black", width=1)

            text = cell.strip()
            text_width = int(font.getlength(text) + kerning * len(text))
            text_x = int(x + (cell_widths[i] - text_width) // 2)
            text_y = int(y + (cell_height - font.getbbox(text)[3]) // 2)

            cursor_x = text_x
            for char in text:
                draw.text((cursor_x, text_y), char, font=font, fill="black")
                cursor_x += int(font.getlength(char) + kerning)

            x += cell_widths[i]
        y += cell_height

    image.save(output_file)
    print(f"Изображение таблицы сохранено как {output_file}")

async def process_markdown_and_draw_image(markdown_text):
    table_data = await markdown_to_table(markdown_text)
    await draw_table_image(table_data)
