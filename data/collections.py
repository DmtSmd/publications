"""Коллекция данных ЛР-1.

В первой лабораторной база данных не используется:
данные хранятся в Python-коллекции.

Каждая карточка — элемент публикации-истории.
"""

publications_db = [
    {
        "publication_id": 1,
        "publication_element": "Текст",
        "publication_content": "Вечерняя прогулка по любимому маршруту",
        "publication_is_numeric": False,
        "publication_layer": 5,
        "publication_filtering": True,
        "publication_image": "publication-text.jpg",
        "publication_video": None,
        "publication_likes": 124,
    },
    {
        "publication_id": 2,
        "publication_element": "Локация",
        "publication_content": "Москва, Лужники",
        "publication_is_numeric": False,
        "publication_layer": 2,
        "publication_filtering": True,
        "publication_image": "publication-location.jpg",
        "publication_video": None,
        "publication_likes": 86,
    },
    {
        "publication_id": 3,
        "publication_element": "Упоминание",
        "publication_content": "@dmitry",
        "publication_is_numeric": False,
        "publication_layer": 4,
        "publication_filtering": False,
        "publication_image": "publication-mention.jpg",
        "publication_video": None,
        "publication_likes": 53,
    },
    {
        "publication_id": 4,
        "publication_element": "Счётчик",
        "publication_content": "8",
        "publication_is_numeric": True,
        "publication_layer": 3,
        "publication_filtering": True,
        "publication_image": "publication-number.jpg",
        "publication_video": None,
        "publication_likes": 41,
    },
    {
        "publication_id": 5,
        "publication_element": "Номер дня",
        "publication_content": "24",
        "publication_is_numeric": True,
        "publication_layer": 1,
        "publication_filtering": False,
        "publication_image": "publication-day.jpg",
        "publication_video": "publication-story.mp4",
        "publication_likes": 29,
    },
]