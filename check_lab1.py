from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from data.collections import publications_db

ROOT = Path(__file__).resolve().parent
client = TestClient(app)
checks = []

def check(name, condition):
    checks.append((name, bool(condition)))

# Предметная область
check("Нет интерьерных полей area/theme/status", not any(k in p for p in publications_db for k in ("area", "theme", "status")))
check("Есть publication_is_numeric", all("publication_is_numeric" in p for p in publications_db))
check("Есть publication_layer 1..5", all(1 <= p["publication_layer"] <= 5 for p in publications_db))
check("Есть publication_filtering", all("publication_filtering" in p for p in publications_db))

# URL / контроллеры
for url in ("/publications", "/publications/1", "/publications/new"):
    check(f"GET {url} = 200", client.get(url).status_code == 200)

filtered = client.get("/publications?publication_filtering=true")
check("GET-фильтр по галочке работает", filtered.status_code == 200 and "Упоминание" not in filtered.text and "Текст" in filtered.text)
next_response = client.get("/publications/1?next=true", follow_redirects=False)
check("Следующий -> /publications/2", next_response.status_code == 303 and next_response.headers.get("location") == "/publications/2")
like_response = client.get("/publications/1?like=true", follow_redirects=False)
check("Лайк работает без JS", like_response.status_code == 303)

# MinIO
for url in ("/publications", "/publications/1", "/publications/new"):
    check(f"MinIO URL виден в HTML {url}", "http://localhost:9000/publications/" in client.get(url).text)

# Структура / названия
main_text = (ROOT / "main.py").read_text(encoding="utf-8")
handlers = (ROOT / "api/handlers.py").read_text(encoding="utf-8")
templates = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "templates/publications").glob("*.html"))
check("main.py минимальный", len(main_text.splitlines()) <= 15)
check("Нет JavaScript в шаблонах", "<script" not in templates.lower())
check("Нет /new-publication", "/new-publication" not in handlers + templates)
check("Шаблоны лежат в templates/publications", len(list((ROOT / "templates/publications").glob("publications_*.html"))) == 3)

print("ПРОВЕРКА ЛР-1")
print("=" * 60)
for name, ok in checks:
    print(("✅" if ok else "❌"), name)
print("=" * 60)
failed = [name for name, ok in checks if not ok]
if failed:
    print(f"НЕ ПРОЙДЕНО: {len(failed)}")
    raise SystemExit(1)
print(f"ВСЕ АВТОМАТИЧЕСКИЕ ПРОВЕРКИ ПРОЙДЕНЫ: {len(checks)}")
