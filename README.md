# 🧭 DSiB — Laboratorium Geologia i Doradztwo

System zarządzania firmą geotechniczną (desktop-first), budowany w oparciu o **Flask + Bootstrap**, z modularną architekturą i roadmapą rozwoju.

## 📦 Dokumentacja projektowa
- 📜 [Context Pack](docs/CONTEXT_PACK.md) – fundament strategii i zasad pracy
- 📅 Roadmapa (w przygotowaniu)
- 📝 Backlog (w przygotowaniu)

## 🧱 Stos technologiczny
- Flask (factory pattern)
- SQLite (docelowo PostgreSQL)
- Alembic migrations
- Bootstrap 5
- Modularne blueprinty (`auth`, `staff`, `client` itd.)

## 🧭 Workflow
- Strategia i zadania zarządzane przez ChatGPT + repo GitHub.
- Każdy task posiada numerację `XX-Task` i własny wątek roboczy.
- Diffy generowane w formacie `git apply`.

## 🪜 Przykładowy przebieg zadania
1. Przygotowanie briefu i akceptacja (strategia)  
2. Weryfikacja DoR  
3. Wygenerowanie patcha (diff)  
4. `git apply patch.diff`  
5. Test + commit + push

## 📥 Szybki start (dev)
```bash
git clone <repo-url>
cd DSiB
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask run
```

---

© 2025 DSiB – Laboratorium Geologia i Doradztwo
