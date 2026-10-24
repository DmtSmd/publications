# Чек-лист ЛР-1 — Publications

## Код — готово

- [x] FastAPI.
- [x] `main.py` — только сборка приложения.
- [x] Контроллеры вынесены в `api/handlers.py`.
- [x] Данные вынесены в `data/collections.py`.
- [x] Карточки — элементы публикации, не интерьерные публикации.
- [x] Удалены `area`, `min_area`, `max_area`, `theme`, статусы ЛР-2.
- [x] Поле `publication_is_numeric` — текстовое/числовое.
- [x] Поле `publication_layer` — порядок наложения 1–5.
- [x] Поле `publication_filtering` — отдельная галочка фильтрации.
- [x] Фильтр = галочка + кнопка `Применить`.
- [x] URL: `/publications`, `/publications/{publication_id}`, `/publications/new`.
- [x] Все шаблоны находятся в `templates/publications` и называются `publications_*`.
- [x] CSS находится в `static/publications/publications.css`.
- [x] Цвета Instagram перечислены в CSS точными кодами.
- [x] Лента: только 2 параметра по теме.
- [x] Лента: лайк и следующий справа одной колонкой.
- [x] Добавление: без статусов и кнопок ЛР-2.
- [x] JavaScript отсутствует.
- [x] MinIO URL находятся прямо в коллекции.
- [x] MinIO URL используются на всех трёх страницах.
- [x] Автоматический тест `python check_lab1.py` — 17/17.
- [x] Локально создана ветка `lab1-publications`.

## Перед отправкой — 5–10 минут вручную

- [ ] В своём GitHub-репозитории создать/запушить ветку `lab1-publications`.
- [ ] Загрузить файлы из `minio_upload/publications/` в публичный bucket `publications`.
- [ ] Проверить `http://127.0.0.1:8000/publications`.
- [ ] В файле «Скриншоты» заменить красные заглушки на реальные скрины Figma.
- [ ] Сделать 3 скрина DevTools → Network для трёх GET.
- [ ] Сделать Response-скрин с URL `http://localhost:9000/publications/...`.
- [ ] Сделать скрин Instagram Web как источника дизайна.
- [ ] Показать конспекты лекций.

## Команды Git

```bash
git checkout main
git pull
git checkout -b lab1-publications
# скопировать исправленные файлы
git add .
git commit -m "Fix lab1 publications by review checklist"
git push -u origin lab1-publications
```

## Проверка

```bash
python check_lab1.py
python -m uvicorn main:app --reload
```
