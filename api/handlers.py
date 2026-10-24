from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from data.collections import publications_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def publications_root():
    return RedirectResponse(url="/publications", status_code=302)


@router.get("/publications")
def publications_list(
    request: Request,
    publication_filtering: bool = Query(False),
):
    """Плитка элементов публикации и GET-фильтрация по галочке."""
    publications = publications_db
    if publication_filtering:
        publications = [
            publication
            for publication in publications_db
            if publication["publication_filtering"]
        ]

    return templates.TemplateResponse(
        request=request,
        name="publications/publications_list.html",
        context={
            "publications": publications,
            "publication_filtering": publication_filtering,
        },
    )


@router.get("/publications/new")
def publications_add(request: Request):
    """Экран добавления ЛР-1: только поля, без кнопок публикации/статусов ЛР-2."""
    publication_example = publications_db[0]
    return templates.TemplateResponse(
        request=request,
        name="publications/publications_add.html",
        context={"publication": publication_example},
    )


@router.get("/publications/{publication_id}")
def publications_feed(
    request: Request,
    publication_id: int,
    next_publication: bool = Query(False, alias="next"),
    like_publication: bool = Query(False, alias="like"),
):
    """Лента элемента публикации. Лайк и переход реализованы без JavaScript."""
    publication = next(
        (
            publication
            for publication in publications_db
            if publication["publication_id"] == publication_id
        ),
        None,
    )

    if publication is None:
        return RedirectResponse(url="/publications", status_code=302)

    if like_publication:
        publication["publication_likes"] += 1
        return RedirectResponse(
            url=f"/publications/{publication_id}",
            status_code=303,
        )

    if next_publication:
        current_index = publications_db.index(publication)
        following = publications_db[(current_index + 1) % len(publications_db)]
        return RedirectResponse(
            url=f"/publications/{following['publication_id']}",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="publications/publications_feed.html",
        context={
            "publication": publication,
            "publication_position": publications_db.index(publication) + 1,
            "publications_total": len(publications_db),
        },
    )
