# 📦 DSiB — Context Pack (v2)

## 1. 🧭 Kontekst strategiczny
- **Projekt:** DSiB – Laboratorium Geologia i Doradztwo  
- **Cel nadrzędny:** budowa kompletnego systemu zarządzania firmą obejmującego moduły: klienci, inwestycje, zadania, notatki, protokoły, próbki, raporty i integracje.  
- **Architektura:**  
  - Backend: Flask (factory `create_app`)  
  - Baza danych: SQLite + Alembic (docelowo PostgreSQL)  
  - UI: Bootstrap 5, kanoniczny mockup „DashboardLaptop_accepted”  
  - Modułowa struktura aplikacji przez `blueprinty` (`auth`, `public`, `staff`, `client` itd.)

## 2. 🧱 Zasady strategiczne projektu
- Dwa poziomy pracy:
  - 🧭 **Wątek strategiczny** – planowanie, roadmapa, backlog.
  - 🛠️ **Wątki robocze** – każdy dotyczy jednego zadania (`XX-Task`).
- Numeracja zadań: `XX-Task` oraz `XX.Y-Task` (podzadania).
- Jeśli **Definition of Ready (DoR)** nie jest spełnione — task nie startuje.
- Krokowy przebieg prac, problemy poboczne trafiają do backlogu.

## 3. 🧭 Kanoniczne założenia techniczne
| Element                        | Wartość / Status                                  | Uwagi                                                                                   |
|---------------------------------|---------------------------------------------------|------------------------------------------------------------------------------------------|
| Model logowania (01.1)         | `pracownicy`                                      | konsolidacja z `users` w osobnym tasku                                                   |
| Redirecty po logowaniu         | `staff.dashboard` / `client.home`                 | zgodne z endpointami aplikacji                                                           |
| Login Manager                  | `login_manager.init_app(app)` przed bp            | `user_loader` → `Pracownik`                                                              |
| Blueprint convention           | `bp = Blueprint(...)` + `from . import routes`    | zero cross-importów blueprintów                                                          |
| UI                             | `DashboardLaptop_accepted`                        | desktop-first, szaro-pomarańczowa paleta                                                 |
| Mobile                         | oddzielny etap                                    | poza zakresem bieżącej roadmapy                                                          |

## 4. 🧰 Schemat delegowania zadań roboczych
Każdy brief zadania zawiera:
- 🎯 Cel  
- 📦 Zakres  
- ⚡ Assumptions & Constraints  
- 🧾 Artefakty wejściowe (DoR)  
- 🧭 Definition of Done (DoD)  
- 🪜 Gates — punkty kontrolne  
- 🔗 Powiązania z innymi taskami  
- 📜 Start-Diff spec (patrz pkt 5)

## 5. 📜 START-DIFF (kanon)
- Multi-file unified diff w jednym bloku (zgodny z `git apply`).  
- PRECHECK:
  - `git status` czysty  
  - `git rev-parse --short HEAD` = deklarowany hash  
  - `git apply --check patch.diff`  
- POSTCHECK:
  - `git diff --name-only`  
  - `flask routes` / `app.url_map`  
  - smoke-test (np. POST /login)  
- ROLLBACK:
  - `git restore --staged -A`  
  - `git restore -W -S .` lub `git reset --hard HEAD`

## 6. ✅ Definition of Ready (DoR) – Checklista
- [ ] Określony komponent/model działania  
- [ ] Potwierdzony HEAD hash repo  
- [ ] Zrzut `flask routes` lub `app.url_map`  
- [ ] Lista dotykanych plików  
- [ ] Akceptacja zależności między taskami  
- [ ] Ustalony plan testu końcowego i punkty Gates

## 7. 🧭 Definition of Done (DoD) – Checklista
- [ ] Patch zastosowany bez błędów (`git apply`)  
- [ ] Aplikacja startuje poprawnie (`flask run`)  
- [ ] Smoke-test końcowy zaliczony  
- [ ] `flask routes` zgodne z założeniami  
- [ ] Commit i push lub PR w repo  
- [ ] Raport ukończenia wątku do strategii

## 8. 🪜 Przykład przepływu taska
1. 📋 Brief + akceptacja (strategia)  
2. 🧾 Sprawdzenie DoR  
3. 🧰 Przygotowanie start-diffu (multi-file)  
4. 🧪 Gate 1 — PRECHECK  
5. 🧰 Git apply + test  
6. 🧪 Gate 2 — POSTCHECK  
7. ✅ Commit, push, raport

## 9. ⚡ Repo & Connectors – zasady współpracy
- Model nie ma natywnego dostępu do repo.  
- Wszystkie operacje `git` wykonuje użytkownik lokalnie lub przez Connectors.  
- Connectors mogą być używane do:
  - pobierania plików, commitów, gałęzi, PR-ów,  
  - wgrywania patcha jako PR lub commit,  
  - synchronizacji repo przed rozpoczęciem zadania.  
- Każde zadanie:
  - zaczyna się od czystego `git status` i potwierdzenia HEAD,  
  - kończy się commitem i pushem (lub PR-em),  
  - jest powiązane z historią repozytorium.

## 10. 🪝 Zasady wersjonowania i numeracji
- `XX-Task` — główny task (np. 01-Task)  
- `XX.Y-Task` — podtask (np. 01.1-Task)  
- Backlog przechowuje: pomysły, poboczne błędy i funkcje do przyszłego wdrożenia.  
- Wszystkie taski powiązane z roadmapą.

---
📌 Ten Context Pack stanowi **fundament organizacyjny projektu DSiB**.
Każdy nowy wątek roboczy powinien odnosić się do tego dokumentu.
