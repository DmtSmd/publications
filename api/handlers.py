from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from data.collections import publications_db
from services.minio_service import get_media_url


router = APIRouter()
templates = Jinja2Templates(directory="templates")


def prepare_publication(publication: dict) -> dict:
    """
    Подготавливает элемент публикации для передачи в HTML-шаблон.

    В коллекции хранятся только имена файлов MinIO.
    Здесь для них формируются временные подписанные ссылки.
    """
    prepared = publication.copy()

    prepared["publication_image_url"] = get_media_url(
        publication.get("publication_image")
    )

    prepared["publication_video_url"] = get_media_url(
        publication.get("publication_video")
    )

    return prepared


@router.get("/")
def publications_root():
    return RedirectResponse(
        url="/publications",
        status_code=302,
    )


@router.get("/publications")
def publications_list(
    request: Request,
    publication_filtering: bool = Query(False),
):
    """
    Плитка элементов публикации.

    Если включена галочка "Фильтрация",
    показываются только элементы,
    у которых publication_filtering = True.
    """

    publications = publications_db

    if publication_filtering:
        publications = [
            publication
            for publication in publications_db
            if publication["publication_filtering"]
        ]

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


@router.get("/publications/new")
def publications_add(request: Request):
    """
    Экран добавления ЛР-1.

    Для первой лабораторной здесь только поля элемента,
    без статусов и кнопок из ЛР-2.
    """

    publication_example = prepare_publication(
        publications_db[0]
    )

    return templates.TemplateResponse(
        request=request,
        name="publications/publications_add.html",
        context={
            "publication": publication_example,
        },
    )


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
    """
    Лента элемента публикации.

    Лайк:
    /publications/1?like=true

    Следующий элемент:
    /publications/1?next=true

    JavaScript не используется.
    """

    publication = next(
        (
            publication
            for publication in publications_db
            if publication["publication_id"] == publication_id
        ),
        None,
    )

    if publication is None:
        return RedirectResponse(
            url="/publications",
            status_code=302,
        )

    if like_publication:
        publication["publication_likes"] += 1

        return RedirectResponse(
            url=f"/publications/{publication_id}",
            status_code=303,
        )

    if next_publication:
        current_index = publications_db.index(publication)

        following = publications_db[
            (current_index + 1) % len(publications_db)
        ]

        return RedirectResponse(
            url=f"/publications/{following['publication_id']}",
            status_code=303,
        )

    prepared_publication = prepare_publication(
        publication
    )

    return templates.TemplateResponse(
        request=request,
        name="publications/publications_feed.html",
        context={
            "publication": prepared_publication,
            "publication_position": (
                publications_db.index(publication) + 1
            ),
            "publications_total": len(publications_db),
        },
    )