"""Коллекция данных ЛР-1.

В первой лабораторной база данных не используется: данные хранятся в Python-коллекции.
Каждая карточка — элемент публикации-истории.
"""

MINIO_BASE_URL = "http://localhost:9000/publications"

publications_db = [
    {
        "publication_id": 1,
        "publication_element": "Текст",
        "publication_content": "Вечерняя прогулка по любимому маршруту",
        "publication_is_numeric": False,
        "publication_layer": 5,
        "publication_filtering": True,
        "publication_image_url": f"{MINIO_BASE_URL}/publication-text.jpg",
        "publication_video_url": f"{MINIO_BASE_URL}/publication-story.mp4",
        "publication_likes": 124,
    },
    {
        "publication_id": 2,
        "publication_element": "Локация",
        "publication_content": "Москва, Лужники",
        "publication_is_numeric": False,
        "publication_layer": 2,
        "publication_filtering": True,
        "publication_image_url": f"{MINIO_BASE_URL}/publication-location.jpg",
        "publication_video_url": f"{MINIO_BASE_URL}/publication-story.mp4",
        "publication_likes": 86,
    },
    {
        "publication_id": 3,
        "publication_element": "Упоминание",
        "publication_content": "@dmitry",
        "publication_is_numeric": False,
        "publication_layer": 4,
        "publication_filtering": False,
        "publication_image_url": f"{MINIO_BASE_URL}/publication-mention.jpg",
        "publication_video_url": f"{MINIO_BASE_URL}/publication-story.mp4",
        "publication_likes": 53,
    },
    {
        "publication_id": 4,
        "publication_element": "Счётчик",
        "publication_content": "8",
        "publication_is_numeric": True,
        "publication_layer": 3,
        "publication_filtering": True,
        "publication_image_url": f"{MINIO_BASE_URL}/publication-number.jpg",
        "publication_video_url": f"{MINIO_BASE_URL}/publication-story.mp4",
        "publication_likes": 41,
    },
    {
        "publication_id": 5,
        "publication_element": "Номер дня",
        "publication_content": "24",
        "publication_is_numeric": True,
        "publication_layer": 1,
        "publication_filtering": False,
        "publication_image_url": f"{MINIO_BASE_URL}/publication-day.jpg",
        "publication_video_url": f"{MINIO_BASE_URL}/publication-story.mp4",
        "publication_likes": 29,
    },
]
