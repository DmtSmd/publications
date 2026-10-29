from database.database import SessionLocal
from database.models import Publication, PublicationLike, PublicationUser

db = SessionLocal()

try:
    # Пользователи
    user1 = PublicationUser(user_name="dmitry")
    user2 = PublicationUser(user_name="anna")

    db.add_all([user1, user2])
    db.flush()

    # Публикации
    publications = [
        Publication(
            publication_element="Текст",
            publication_content="Вечерняя прогулка по любимому маршруту",
            publication_is_numeric=False,
            publication_layer=5,
            publication_filtering=True,
            publication_status="published",
            publication_image="publication-text.jpg",
            publication_video=None,
            publication_creator_id=user1.user_id,
        ),
        Publication(
            publication_element="Локация",
            publication_content="Москва, Лужники",
            publication_is_numeric=False,
            publication_layer=2,
            publication_filtering=True,
            publication_status="published",
            publication_image="publication-location.jpg",
            publication_video=None,
            publication_creator_id=user1.user_id,
        ),
        Publication(
            publication_element="Упоминание",
            publication_content="@dmitry",
            publication_is_numeric=False,
            publication_layer=4,
            publication_filtering=False,
            publication_status="draft",
            publication_image="publication-mention.jpg",
            publication_video=None,
            publication_creator_id=user1.user_id,
        ),
        Publication(
            publication_element="Счётчик",
            publication_content="8",
            publication_is_numeric=True,
            publication_layer=3,
            publication_filtering=True,
            publication_status="published",
            publication_image="publication-number.jpg",
            publication_video=None,
            publication_creator_id=user2.user_id,
        ),
        Publication(
            publication_element="Номер дня",
            publication_content="24",
            publication_is_numeric=True,
            publication_layer=1,
            publication_filtering=False,
            publication_status="deleted",
            publication_image="publication-day.jpg",
            publication_video="publication-story.mp4",
            publication_creator_id=user2.user_id,
        ),
    ]

    db.add_all(publications)
    db.flush()

    # Лайки
    likes = [
        PublicationLike(
            publication_id=publications[0].publication_id,
            user_id=user1.user_id,
        ),
        PublicationLike(
            publication_id=publications[0].publication_id,
            user_id=user2.user_id,
        ),
        PublicationLike(
            publication_id=publications[1].publication_id,
            user_id=user2.user_id,
        ),
    ]

    db.add_all(likes)
    db.commit()

    print("Seed OK")

finally:
    db.close()