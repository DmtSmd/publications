import json
import os
from io import BytesIO
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
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
    }
    context.update(values)
    return templates.TemplateResponse(request=request, name="add.html", context=context)


@app.get("/publications", response_class=HTMLResponse)
def publications(request: Request, min_area: int | None = None, max_area: int | None = None):
    result = data
    if min_area is not None:
        result = [p for p in result if p["area"] >= min_area]
    if max_area is not None:
        result = [p for p in result if p["area"] <= max_area]
    return templates.TemplateResponse(
        request=request,
        name="publications.html",
        context={"publications": result, "min_area": min_area, "max_area": max_area},
    )


@app.get("/publications/{publication_id}", response_class=HTMLResponse)
def publication_detail(request: Request, publication_id: int):
    item = next((p for p in data if p["id"] == publication_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Публикация не найдена")

    index = data.index(item)
    next_item = data[(index + 1) % len(data)]
    descriptions = {
        1: "Стильная кухня в зелёных тонах с продуманным освещением.",
        2: "Светлые тона, натуральные материалы и большие окна создают атмосферу уюта.",
        3: "Удобное рабочее пространство для творчества и продуктивной работы.",
        4: "Современная гостиная в стиле лофт с лаконичной мебелью.",
    }
    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={
            "item": item,
            "description": item.get("content") or descriptions.get(item["id"], ""),
            "position": index + 1,
            "total": len(data),
            "next_id": next_item["id"],
        },
    )


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


@app.post("/new-publication", response_class=HTMLResponse)
async def create_publication(
    request: Request,
    title: str = Form(...),
    theme: str = Form(...),
    area: int = Form(...),
    content: str = Form(...),
    is_numeric: bool = Form(False),
    layer: int = Form(3),
    image: UploadFile = File(...),
):
    values = dict(title=title, theme=theme, area=area, content=content, is_numeric=is_numeric, layer=layer)

    def invalid(message):
        return add_context(request, error=message, **values)

    if not title.strip() or not content.strip():
        return invalid("Заполните название и содержимое элемента.")
    if area < 0:
        return invalid("Площадь не может быть отрицательной.")
    if not 1 <= layer <= 5:
        return invalid("Порядок наложения должен быть от 1 до 5.")
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

    try:
        minio_client.put_object(
            BUCKET,
            filename,
            BytesIO(image_bytes),
            length=len(image_bytes),
            content_type=mime,
        )
    except Exception:
        return invalid("Не удалось загрузить фотографию в MinIO. Проверьте, что контейнер запущен.")

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
            "image": f"/media/{filename}",
        }
        updated = data + [new_item]
        try:
            save_data(updated)
        except OSError:
            return invalid("Фото загружено, но не удалось сохранить данные публикации. Проверьте права на запись.")
        data.append(new_item)

    return RedirectResponse(url=f"/publications/{new_id}", status_code=303)


@app.get("/media/{filename}")
def get_media(filename: str):
    allowed_files = {f"{i}.png" for i in range(1, 7)}
    allowed_files.update(Path(item["image"]).name for item in data if item.get("image", "").startswith("/media/"))
    if filename not in allowed_files:
        raise HTTPException(status_code=404, detail="Файл не найден")

    try:
        url = minio_client.presigned_get_object(BUCKET, filename)
    except Exception:
        raise HTTPException(status_code=503, detail="MinIO недоступен")
    return RedirectResponse(url=url)
