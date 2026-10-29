from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from database.database import SessionLocal
from database.models import Publication
from services.minio_service import get_media_url


router = APIRouter()
templates = Jinja2Templates(directory="templates")


def prepare_publication(publication: Publication) -> dict:
    """Преобразуем ORM-объект в данные для Jinja-шаблона."""

    image_url = None
    video_url = None

    # Если имя файла нормальное — получаем ссылку из MinIO.
    # Если имя начинается с invalid-, оставляем None,
    # чтобы шаблон показал default photo / default video.
    if (
        publication.publication_image
        and not publication.publication_image.startswith("invalid-")
    ):
        image_url = get_media_url(
            publication.publication_image
        )

    if (
        publication.publication_video
        and not publication.publication_video.startswith("invalid-")
    ):
        video_url = get_media_url(
            publication.publication_video
        )

    return {
        "publication_id": publication.publication_id,
        "publication_element": publication.publication_element,
        "publication_content": publication.publication_content,
        "publication_is_numeric": publication.publication_is_numeric,
        "publication_layer": publication.publication_layer,
        "publication_filtering": publication.publication_filtering,
        "publication_status": publication.publication_status,
        "publication_image": publication.publication_image,
        "publication_video": publication.publication_video,
        "publication_image_url": image_url,
        "publication_video_url": video_url,
        "publication_likes": len(publication.likes),
        "publication_creator_id": publication.publication_creator_id,
    }


@router.get("/")
def publications_root():
    return RedirectResponse(
        url="/publications",
        status_code=302,
    )


# =========================================================
# СПИСОК ПУБЛИКАЦИЙ
# =========================================================

@router.get("/publications")
def publications_list(
    request: Request,
    publication_filtering: bool = Query(False),
):
    with SessionLocal() as db:

        statement = (
            select(Publication)
            .options(selectinload(Publication.likes))
            .where(
                Publication.publication_status == "published"
            )
            .order_by(Publication.publication_id)
        )

        if publication_filtering:
            statement = statement.where(
                Publication.publication_filtering.is_(True)
            )

        publications = db.scalars(statement).all()

        prepared_publications = [
            prepare_publication(publication)
            for publication in publications
        ]

    return templates.TemplateResponse(
        request=request,
        name="publications/publications_list.html",
        context={
            "publications": prepared_publications,
            "publication_filtering": publication_filtering,
        },
    )


# =========================================================
# ФОРМА ДОБАВЛЕНИЯ / ЧЕРНОВИК
# =========================================================

@router.get("/publications/new")
def publications_add(request: Request):
    with SessionLocal() as db:

        statement = (
            select(Publication)
            .options(selectinload(Publication.likes))
            .where(
                Publication.publication_status == "draft"
            )
            .order_by(Publication.publication_id)
        )

        publication = db.scalars(statement).first()

        if publication is not None:
            publication = prepare_publication(publication)

    return templates.TemplateResponse(
        request=request,
        name="publications/publications_add.html",
        context={
            "publication": publication,
        },
    )


# =========================================================
# СОЗДАНИЕ ЧЕРНОВИКА
# =========================================================

@router.post("/publications/new")
def publication_create_draft(
    publication_element: str = Form(...),
    publication_content: str = Form(...),
    publication_layer: int = Form(...),
    publication_is_numeric: bool = Form(False),
    publication_filtering: bool = Form(False),
):
    with SessionLocal() as db:

        existing_draft = db.scalars(
            select(Publication).where(
                Publication.publication_status == "draft"
            )
        ).first()

        # Одновременно может существовать только один черновик.
        if existing_draft is not None:
            return RedirectResponse(
                url="/publications/new",
                status_code=303,
            )

        publication = Publication(
            publication_element=publication_element,
            publication_content=publication_content,
            publication_is_numeric=publication_is_numeric,
            publication_layer=publication_layer,
            publication_filtering=publication_filtering,
            publication_status="draft",

            # Специально неверные имена файлов.
            # Это демонстрирует default media с SSR-сервера.
            publication_image="invalid-publication-image.jpg",
            publication_video="invalid-publication-video.mp4",

            publication_creator_id=1,
        )

        db.add(publication)
        db.commit()

    return RedirectResponse(
        url="/publications/new",
        status_code=303,
    )


# =========================================================
# ЛОГИЧЕСКОЕ УДАЛЕНИЕ
# Чистый SQL UPDATE
# =========================================================

@router.post("/publications/{publication_id}/delete")
def publication_delete(publication_id: int):
    with SessionLocal() as db:

        db.execute(
            text(
                """
                UPDATE publications
                SET publication_status = 'deleted'
                WHERE publication_id = :publication_id
                """
            ),
            {
                "publication_id": publication_id,
            },
        )

        db.commit()

    return RedirectResponse(
        url="/publications",
        status_code=303,
    )


# =========================================================
# ПУБЛИКАЦИЯ ЧЕРНОВИКА
# =========================================================

@router.post("/publications/{publication_id}/publish")
def publication_publish(publication_id: int):
    with SessionLocal() as db:

        publication = db.get(
            Publication,
            publication_id,
        )

        if publication is None:
            return RedirectResponse(
                url="/publications",
                status_code=303,
            )

        if publication.publication_status != "draft":
            return RedirectResponse(
                url="/publications",
                status_code=303,
            )

        publication.publication_status = "published"

        db.commit()

    return RedirectResponse(
        url=f"/publications/{publication_id}",
        status_code=303,
    )


# =========================================================
# ЛЕНТА ПУБЛИКАЦИЙ
# =========================================================

@router.get("/publications/{publication_id}")
def publications_feed(
    request: Request,
    publication_id: int,
    next_publication: bool = Query(
        False,
        alias="next",
    ),
    like_publication: bool = Query(
        False,
        alias="like",
    ),
):
    with SessionLocal() as db:

        # Получаем только опубликованную запись.
        statement = (
            select(Publication)
            .options(
                selectinload(Publication.likes)
            )
            .where(
                Publication.publication_id == publication_id,
                Publication.publication_status == "published",
            )
        )

        publication = db.scalars(
            statement
        ).first()

        # draft и deleted напрямую открывать нельзя.
        if publication is None:
            return RedirectResponse(
                url="/publications",
                status_code=302,
            )

        # Во второй ЛР новые лайки через приложение
        # пока не создаём.
        # Отображается количество строк из БД.
        if like_publication:
            return RedirectResponse(
                url=f"/publications/{publication_id}",
                status_code=303,
            )

        # -------------------------------------------------
        # Переход к следующей публикации
        # -------------------------------------------------

        if next_publication:

            statement = (
                select(Publication)
                .options(
                    selectinload(Publication.likes)
                )
                .where(
                    Publication.publication_status
                    == "published"
                )
                .order_by(
                    Publication.publication_id
                )
            )

            publications = db.scalars(
                statement
            ).all()

            current_index = next(
                index
                for index, item in enumerate(publications)
                if item.publication_id == publication_id
            )

            following = publications[
                (current_index + 1) % len(publications)
            ]

            return RedirectResponse(
                url=f"/publications/{following.publication_id}",
                status_code=303,
            )

        # -------------------------------------------------
        # Определяем позицию публикации в ленте
        # -------------------------------------------------

        statement = (
            select(Publication)
            .options(
                selectinload(Publication.likes)
            )
            .where(
                Publication.publication_status
                == "published"
            )
            .order_by(
                Publication.publication_id
            )
        )

        publications = db.scalars(
            statement
        ).all()

        publication_position = next(
            index + 1
            for index, item in enumerate(publications)
            if item.publication_id == publication_id
        )

        publications_total = len(publications)

        prepared_publication = prepare_publication(
            publication
        )

    return templates.TemplateResponse(
        request=request,
        name="publications/publications_feed.html",
        context={
            "publication": prepared_publication,
            "publication_position": publication_position,
            "publications_total": publications_total,
        },
    )