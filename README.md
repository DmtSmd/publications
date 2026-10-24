# Publications — лабораторная работа № 1

Тема: **«Публикация-история»**.  
FastAPI + Jinja2 + HTML/CSS + MinIO.

## Что исправлено по замечаниям преподавателя

- Карточки — **элементы публикации**, а не интерьерные публикации.
- Поля по теме: `publication_is_numeric` и `publication_layer`.
- Фильтрация: отдельная галочка `publication_filtering` + кнопка «Применить».
- В коде, URL, шаблонах и CSS используется предметное имя `publications`.
- `main.py` содержит только сборку приложения; контроллеры находятся в `api/handlers.py`, данные — в `data/collections.py`.
- Лента: два параметра по теме, лайк и «Следующий» справа одной колонкой.
- Добавление ЛР-1: без статусов и кнопок ЛР-2.
- JavaScript не используется.

## Структура

```text
main.py
api/handlers.py
data/collections.py
templates/publications/
  publications_list.html
  publications_feed.html
  publications_add.html
static/publications/publications.css
minio_upload/publications/
```

## MinIO

Создайте публичный бакет `publications` на `localhost:9000` и загрузите содержимое папки:

`minio_upload/publications/`

В коллекции используются прямые URL вида:

`http://localhost:9000/publications/publication-text.jpg`

Это сделано специально для демонстрации URL MinIO в HTML Response на защите ЛР-1.

## Запуск

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Открыть:

- `http://127.0.0.1:8000/publications` — плитка + GET-фильтр;
- `http://127.0.0.1:8000/publications/1` — лента;
- `http://127.0.0.1:8000/publications/new` — добавление.

## Три GET-контроллера

1. `GET /publications` — список и фильтрация по `publication_filtering`.
2. `GET /publications/{publication_id}` — лента, `?next=true`, `?like=true`.
3. `GET /publications/new` — экран добавления.

## Git: отдельная ветка ЛР-1

В существующем репозитории:

```bash
git checkout main
git pull
git checkout -b lab1-publications
# заменить файлы содержимым этого проекта
git add .
git commit -m "Fix lab1 publications by review checklist"
git push -u origin lab1-publications
```

## Дизайн-референс

Instagram. В `static/publications/publications.css` перечислены скопированные характеристики:

- кнопка/акцент `#0095F6`;
- фон `#FAFAFA`;
- текст `#262626`;
- карточка `#FFFFFF`;
- header/navigation `#FFFFFF`;
- граница `#DBDBDB`.
