import requests
import asyncio
import datetime
import pytz
import re
from datetime import date, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

SCHEDULE_URL = "https://nvpk-mephi.ru/%d0%b3%d0%bb%d0%b0%d0%b2%d0%bd%d0%b0%d1%8f/%d1%81%d1%82%d1%83%d0%b4%d0%b5%d0%bd%d1%82%d1%83/%d0%b8%d0%b7%d0%bc%d0%b5%d0%bd%d0%b5%d0%bd%d0%b8%d1%8f-%d0%b2-%d0%be%d1%81%d0%bd%d0%be%d0%b2%d0%bd%d0%be%d0%bc-%d1%80%d0%b0%d1%81%d0%bf%d0%b8%d1%81%d0%b0%d0%bd%d0%b8%d0%b8/"

last_content = ""
moscow_tz = pytz.timezone('Europe/Moscow')
now = datetime.now(moscow_tz)

async def check_schedule(value, method_id):
    from main import send_photo, send_legacy_schedule_photo, send_schedule_to_all


    global last_content
    try:
        response = requests.get(SCHEDULE_URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        elements = soup.select('div.wp-block-column > *')

        h5_groups = []
        tables = []

        current_h5_group = []

        for element in elements:
            if element.name == 'h5':
                strong_element = element.find('strong')
                if strong_element and strong_element.text.strip():
                    current_h5_group.append(element)
            elif element.name == 'table':
                if current_h5_group:
                    h5_groups.append(current_h5_group)
                    current_h5_group = []
                tables.append(element)

        if current_h5_group:
            h5_groups.append(current_h5_group)

        if len(h5_groups) != len(tables):
            print("Ошибка: количество групп h5 не совпадает с количеством таблиц.")
            return

        for idx, (h5_group, table) in enumerate(zip(h5_groups, tables)):
            relevant_h5_elements = h5_group[:4][-2:]

            texts = []
            for h5 in relevant_h5_elements:
                strong_element = h5.find('strong')
                if strong_element:
                    texts.append(strong_element.text.strip())
                else:
                    texts.append("")

            if len(texts) == 2:
                result_text = " / ".join(texts)

                match = re.search(r"«(\d+)»", result_text)
                if match:
                    day_number = int(match.group(1))
                    if day_number == now.day+1:
                        schedule_text = f"| | | {result_text} | | |\n"
                        schedule_text += "| Группа | Пара | Предмет | Преподаватель | Аудитория |\n"

                        rows = table.find_all('tr')
                        if len(rows) > 1:
                            group = None
                            seen_entries = set()

                            for row in rows[1:]:
                                cols = row.find_all('td')
                                if len(cols) < 4:
                                    continue

                                if len(cols) >= 5:
                                    new_group = cols[0].get_text(strip=True)
                                    pair = cols[1].get_text(strip=True)
                                    subject = cols[2].get_text(strip=True).replace('\n', '').strip()
                                    teacher = cols[3].get_text(strip=True)
                                    audience = cols[4].get_text(strip=True)

                                    entry_key = (new_group, pair, subject, teacher, audience)
                                    if entry_key in seen_entries:
                                        continue
                                    seen_entries.add(entry_key)

                                    if group != new_group:
                                        group = new_group
                                        schedule_text += f"| {group} | {pair} | {subject} | {teacher} | {audience} |\n"
                                    else:
                                        schedule_text += f"| | {pair} | {subject} | {teacher} | {audience} |\n"

                                elif len(cols) == 4:
                                    pair = cols[0].get_text(strip=True)
                                    subject = cols[1].get_text(strip=True).replace('\n', '').strip()
                                    teacher = cols[2].get_text(strip=True)
                                    audience = cols[3].get_text(strip=True)

                                    entry_key = (group, pair, subject, teacher, audience)
                                    if entry_key in seen_entries:
                                        continue
                                    seen_entries.add(entry_key)

                                    schedule_text += f"| | {pair} | {subject} | {teacher} | {audience} |\n"

                        if schedule_text != last_content:
                            last_content = schedule_text
                            from get_image import process_markdown_and_draw_image
                            await process_markdown_and_draw_image(schedule_text)

                            if method_id == 1:
                                await send_photo(value.from_user.id)
                            else:
                                await send_schedule_to_all(message=None)

                        else:
                            print(f"Нет изменений для группы {idx + 1}.")      
                    else:
                        if method_id == 1:
                                await send_legacy_schedule_photo(value.from_user.id)
                        else:
                            return
                        
                else:
                    print("Число не найдено")
            else:
                result_text = "Недостаточно данных для заголовка."
    except Exception as e:
        print(f"Ошибка при проверке расписания: {e}")

async def check_schedule_to_all():
    if 17 <= now.hour < 24:
        print("Начал проверку расписания:")
        image_path = Path(f"img/{date.today()}.png")
        while True:
            if image_path.is_file():
                print(f"Файл найден: {image_path}")
                return
            else:
                print(f"Изображение не найдено по указанному пути: {image_path}")
                await check_schedule('', 2)
    else:
        return
