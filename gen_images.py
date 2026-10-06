#!/usr/bin/env python3
"""Генерация vision-тестов. Эталоны — в vision_tasks.json."""
import json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "images")
os.makedirs(IMG, exist_ok=True)

FD = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f_title = ImageFont.truetype(FB, 36)
f_body = ImageFont.truetype(FD, 28)
f_small = ImageFont.truetype(FD, 16)
f_ui = ImageFont.truetype(FD, 24)
f_ui_b = ImageFont.truetype(FB, 24)

# V1: русский текст с мелкой строкой
im = Image.new("RGB", (800, 600), "white")
d = ImageDraw.Draw(im)
d.text((40, 30), "Объявление", font=f_title, fill="black")
d.text((40, 100), "Собрание жильцов дома 12", font=f_body, fill="black")
d.text((40, 150), "состоится 15 марта в 18:00", font=f_body, fill="black")
d.text((40, 200), "в актовом зале на втором этаже.", font=f_body, fill="black")
d.text((40, 300), "Контакт: 8 (495) 123-45-67", font=f_small, fill="black")
d.text((40, 330), "Код домофона: 4821", font=f_small, fill="black")
im.save(os.path.join(IMG, "v1_text.png"))

# V2: фигуры — 3 красных круга, 2 синих квадрата, 1 зелёный треугольник
im = Image.new("RGB", (600, 600), "white")
d = ImageDraw.Draw(im)
d.ellipse([50, 50, 150, 150], fill="red")
d.ellipse([200, 50, 300, 150], fill="red")
d.ellipse([350, 50, 450, 150], fill="red")
d.rectangle([50, 250, 150, 350], fill="blue")
d.rectangle([200, 250, 300, 350], fill="blue")
d.polygon([(400, 350), (500, 350), (450, 250)], fill="green")
im.save(os.path.join(IMG, "v2_shapes.png"))

# V3: мок диалога — кнопка Отмена справа внизу
im = Image.new("RGB", (800, 600), "white")
d = ImageDraw.Draw(im)
d.rectangle([100, 80, 700, 520], outline="black", width=3)          # окно
d.rectangle([100, 80, 700, 140], fill=(30, 90, 160))                # заголовок
d.text((120, 92), "Настройки", font=f_ui_b, fill="white")
d.text((140, 200), "☐ Уведомления", font=f_ui, fill="black")
d.text((140, 260), "☑ Тёмная тема", font=f_ui, fill="black")
d.rectangle([140, 420, 320, 470], outline="black", width=2)         # Сохранить
d.text((165, 430), "Сохранить", font=f_ui, fill="black")
d.rectangle([480, 420, 660, 470], outline="black", width=2)         # Отмена
d.text((525, 430), "Отмена", font=f_ui, fill="black")
im.save(os.path.join(IMG, "v3_ui.png"))

tasks = {
    "models": [
        "qwen3.5-32k:latest",
        "hf.co/mradermacher/KV-Ground-8B-BaseGuiOwl1.5-0315-GGUF:Q4_K_M",
        "llava:latest"
    ],
    "options": {"temperature": 0, "num_ctx": 8192},
    "tasks": [
        {"id": "V1", "image": "images/v1_text.png",
         "prompt": "Транскрибируй ВЕСЬ текст с картинки построчно, точно, без пересказа.",
         "ref": "Объявление / Собрание жильцов дома 12 / состоится 15 марта в 18:00 / в актовом зале на втором этаже. / 8 (495) 123-45-67 / Код домофона: 4821"},
        {"id": "V2", "image": "images/v2_shapes.png",
         "prompt": "Перечисли все фигуры на картинке по цветам и формам и посчитай количество каждого вида.",
         "ref": "3 красных круга, 2 синих квадрата, 1 зелёный треугольник"},
        {"id": "V3", "image": "images/v3_ui.png",
         "prompt": "Где находится кнопка «Отмена» в окне «Настройки»? Опиши её положение и дай примерные координаты центра в шкале 0-1000.",
         "ref": "справа внизу окна, рядом с «Сохранить»; центр ~ x=710, y=740"}
    ]
}
with open(os.path.join(HERE, "vision_tasks.json"), "w", encoding="utf-8") as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)
print("images + vision_tasks.json ready")
