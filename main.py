import json
import os
from io import BytesIO
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from minio import Minio

app = FastAPI()

minio_client = Minio(
    "localhost:9000",
    access_key=os.environ["MINIO_ACCESS_KEY"],
    secret_key=os.environ["MINIO_SECRET_KEY"],
    secure=False,
)
BUCKET = "publications"
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 МБ
MAX_VIDEO_SIZE = 30 * 1024 * 1024  # 30 МБ
DATA_FILE = Path(__file__).resolve().parent / "publications_data.json"
data_lock = Lock()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

INITIAL_DATA = [
    {"id": 1, "title": "Зелёная кухня", "area": 55, "theme": "Кухня", "image": "/media/4.png"},
    {"id": 2, "title": "Уютная гостиная", "area": 23, "theme": "Гостиная", "image": "/media/1.png"},
    {"id": 3, "title": "Рабочее пространство", "area": 31, "theme": "Кабинет", "image": "/media/3.png"},
    {"id": 4, "title": "Лофт гостиная", "area": 22, "theme": "Гостиная", "image": "/media/2.png"},
]


def load_data():
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return [dict(item) for item in INITIAL_DATA]


def save_data(items):
    temporary = DATA_FILE.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    temporary.replace(DATA_FILE)


data = load_data()


def add_context(request, **values):
    context = {
        "preview": None,
        "error": None,
        "title": "",
        "theme": "Гостиная",
        "content": "",
        "area": "",
        "is_numeric": False,
        "layer": 3,
        "status": "published",
    }
    context.update(values)
    return templates.TemplateResponse(request=request, name="add.html", context=context)



@app.get("/publications", response_class=HTMLResponse)
def publications(
    request: Request,
    min_area: str = "",
    max_area: str = "",
    numeric_only: bool = False,
):
    try:
        min_value = int(min_area) if min_area.strip() else None
        max_value = int(max_area) if max_area.strip() else None
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Площадь должна быть целым числом"
        )

    result = [p for p in data if p.get("status", "published") == "published"]

    if min_value is not None:
        result = [
            p for p in result
            if p["area"] >= min_value
        ]

    if max_value is not None:
        result = [
            p for p in result
            if p["area"] <= max_value
        ]

    if numeric_only:
        result = [
            p for p in result
            if p.get("is_numeric", False)
        ]

    return templates.TemplateResponse(
        request=request,
        name="publications.html",
        context={
            "publications": result,
            "min_area": min_area,
            "max_area": max_area,
            "numeric_only": numeric_only,
        },
    )



@app.get("/publications/{publication_id}", response_class=HTMLResponse)
def publication_detail(request: Request, publication_id: int, go_next: bool = Query(False, alias="next")):
    item = next((p for p in data if p["id"] == publication_id), None)
    if item is None or item.get("status", "published") == "deleted":
        raise HTTPException(status_code=404, detail="Публикация не найдена")

    published = [p for p in data if p.get("status", "published") == "published"]
    if go_next:
        if not published:
            return RedirectResponse(url="/publications", status_code=303)
        current_index = next((i for i, p in enumerate(published) if p["id"] == publication_id), -1)
        following = published[(current_index + 1) % len(published)]
        return RedirectResponse(url=f"/publications/{following['id']}", status_code=303)

    descriptions = {
        1: "Стильная кухня в зелёных тонах с продуманным освещением.",
        2: "Светлые тона, натуральные материалы и большие окна создают атмосферу уюта.",
        3: "Удобное рабочее пространство для творчества и продуктивной работы.",
        4: "Современная гостиная в стиле лофт с лаконичной мебелью.",
    }
    position = next((i + 1 for i, p in enumerate(published) if p["id"] == publication_id), 0)
    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={
            "item": item,
            "description": item.get("content") or descriptions.get(item["id"], ""),
            "position": position,
            "total": len(published),
        },
    )


@app.post("/publications/{publication_id}/like")
def like_publication(publication_id: int):
    with data_lock:
        item = next((p for p in data if p["id"] == publication_id), None)
        if item is None or item.get("status", "published") != "published":
            raise HTTPException(status_code=404, detail="Публикация не найдена")
        updated = [dict(p) for p in data]
        for p in updated:
            if p["id"] == publication_id:
                p["likes"] = max(0, int(p.get("likes", 0))) + 1
                break
        try:
            save_data(updated)
        except OSError:
            raise HTTPException(status_code=500, detail="Не удалось сохранить лайк")
        item["likes"] = next(p["likes"] for p in updated if p["id"] == publication_id)
    return RedirectResponse(url=f"/publications/{publication_id}", status_code=303)


@app.get("/new-publication", response_class=HTMLResponse)
def new_publication(request: Request):
    return add_context(request)


def detect_image_type(content: bytes):
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png", "image/png"
    if content.startswith(b"\xff\xd8\xff"):
        return "jpg", "image/jpeg"
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return "webp", "image/webp"
    return None


def detect_video_type(content: bytes):
    if len(content) >= 12 and content[4:8] == b"ftyp":
        return "mp4", "video/mp4"
    if content.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm", "video/webm"
    return None


@app.post("/new-publication", response_class=HTMLResponse)
async def create_publication(
    request: Request,
    title: str = Form(...),
    theme: str = Form(...),
    area: int = Form(...),
    content: str = Form(...),
    is_numeric: bool = Form(False),
    layer: int = Form(3),
    status: str = Form("published"),
    image: UploadFile = File(...),
    video: UploadFile | None = File(None),
):
    values = dict(title=title, theme=theme, area=area, content=content, is_numeric=is_numeric, layer=layer, status=status)

    def invalid(message):
        return add_context(request, error=message, **values)

    if not title.strip() or not content.strip():
        return invalid("Заполните название и содержимое элемента.")
    if area < 0:
        return invalid("Площадь не может быть отрицательной.")
    if not 1 <= layer <= 5:
        return invalid("Порядок наложения должен быть от 1 до 5.")
    if status not in {"draft", "published", "deleted"}:
        return invalid("Неизвестный статус публикации.")
    if is_numeric:
        try:
            float(content.replace(",", "."))
        except ValueError:
            return invalid("Для числового элемента введите число.")

    image_bytes = await image.read(MAX_IMAGE_SIZE + 1)
    await image.close()
    if not image_bytes:
        return invalid("Выберите фотографию.")
    if len(image_bytes) > MAX_IMAGE_SIZE:
        return invalid("Размер фотографии не должен превышать 10 МБ.")

    detected = detect_image_type(image_bytes)
    if detected is None:
        return invalid("Допустимы только фотографии PNG, JPG или WEBP.")
    extension, mime = detected
    filename = f"{uuid4().hex}.{extension}"

    video_bytes = b""
    video_filename = None
    video_mime = None
    if video is not None and video.filename:
        video_bytes = await video.read(MAX_VIDEO_SIZE + 1)
        await video.close()
        if len(video_bytes) > MAX_VIDEO_SIZE:
            return invalid("Размер видео не должен превышать 30 МБ.")
        detected_video = detect_video_type(video_bytes)
        if not video_bytes or detected_video is None:
            return invalid("Допустимы только видео MP4 или WEBM.")
        video_extension, video_mime = detected_video
        video_filename = f"{uuid4().hex}.{video_extension}"

    uploaded = []
    try:
        minio_client.put_object(
            BUCKET,
            filename,
            BytesIO(image_bytes),
            length=len(image_bytes),
            content_type=mime,
        )
        uploaded.append(filename)
        if video_filename:
            minio_client.put_object(
                BUCKET,
                video_filename,
                BytesIO(video_bytes),
                length=len(video_bytes),
                content_type=video_mime,
            )
            uploaded.append(video_filename)
    except Exception:
        for uploaded_name in uploaded:
            try:
                minio_client.remove_object(BUCKET, uploaded_name)
            except Exception:
                pass
        return invalid("Не удалось загрузить медиафайлы в MinIO. Проверьте, что контейнер запущен.")

    with data_lock:
        new_id = max((p["id"] for p in data), default=0) + 1
        new_item = {
            "id": new_id,
            "title": title.strip(),
            "theme": theme,
            "area": area,
            "content": content.strip(),
            "is_numeric": is_numeric,
            "layer": layer,
            "status": status,
            "likes": 0,
            "image": f"/media/{filename}",
            "video": f"/media/{video_filename}" if video_filename else None,
        }
        updated = data + [new_item]
        try:
            save_data(updated)
        except OSError:
            for uploaded_name in uploaded:
                try:
                    minio_client.remove_object(BUCKET, uploaded_name)
                except Exception:
                    pass
            return invalid("Не удалось сохранить данные публикации. Проверьте права на запись.")
        data.append(new_item)

    destination = "/publications" if status == "deleted" else f"/publications/{new_id}"
    return RedirectResponse(url=destination, status_code=303)


@app.get("/media/{filename}")
def get_media(filename: str):
    allowed_files = {f"{i}.png" for i in range(1, 7)}
    for item in data:
        for field in ("image", "video"):
            media_path = item.get(field) or ""
            if media_path.startswith("/media/"):
                allowed_files.add(Path(media_path).name)
    if filename not in allowed_files:
        raise HTTPException(status_code=404, detail="Файл не найден")

    try:
        url = minio_client.presigned_get_object(BUCKET, filename)
    except Exception:
        raise HTTPException(status_code=503, detail="MinIO недоступен")
    return RedirectResponse(url=url)
