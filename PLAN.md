# PaperAssist - Project Plan

## 1. Overview

PaperAssist is a multi-component IoT system consisting of:

| Component | Tech Stack | Location |
|-----------|-----------|----------|
| **Firmware** | C / ESP-IDF / PlatformIO | ESP32 + SSD1681 e-paper |
| **API** | Python / FastAPI / uv / ruff | VPS (Docker) |
| **Web App** | Next.js / React / TypeScript / Tailwind / Prettier / ESLint | VPS (Docker + nginx) |
| **Mobile App** | React Native / Expo / NativeWind (Tailwind) | Expo build / app stores |

**Repo:** `git@github.com:TheDMNMachine/PaperAssist.git`
**VPS:** `bill210.mikrus.xyz` (SSH port `10210`, IPv6: `2a01:4f9:4a:1e1b::210`)
**Domain:** `paperassist.tojest.dev` → `[2a01:4f9:4a:1e1b::210]:80`

---

## 2. System Flow

```
┌─────────────┐      HTTP/REST       ┌─────────────┐      nginx       ┌─────────────┐
│   ESP32      │ ──────────────────►  │  FastAPI     │ ◄──────────────  │  Next.js     │
│  (e-paper)   │   co 5 min fetch     │  (API)       │                  │  (Web SPA)   │
│              │                      │              │                  │              │
│  SSD1681     │                      │  /api/v1/*   │                  │  SSR/SSG     │
│  WiFi+BLE    │                      │  PostgreSQL  │                  │  Tailwind    │
└──────┬───────┘                      └──────────────┘                  └──────────────┘
       │ BLE                               ▲
       │                                   │ HTTP/REST
       ▼                                   │
┌─────────────┐                            │
│  React      │ ───────────────────────────┘
│  Native App │
│  (Expo)     │
│  BLE + HTTP │
└─────────────┘
```

### Flow Details

1. **ESP32** budzi się co 5 minut, łączy się z API (`paperassist.tojest.dev/api/v1/screen`), pobiera dane ekranu i wyświetla je na e-paper. Na alarm — specjalne zachowanie (buzzer, LED, zmiana ekranu).
2. **API (FastAPI)** przechowuje stan ekranów, dane alarmów, konfigurację. Eksponuje REST endpointy dla wszystkich klientów.
3. **Web (Next.js)** wyświetla aktualny stan, pozwala edytować ekrany/alarmy. W przyszłości — push notifications.
4. **Mobile (React Native)** łączy się z ESP32 po BLE (konfiguracja, podgląd) + z API po HTTP (te same funkcje co web).

---

## 3. Monorepo Structure

```
PaperAssist/
├── firmware/                   # ESP32 C code (obecny kod przeniesiony tu)
│   ├── src/
│   │   ├── main.c
│   │   ├── ssd1681.c / .h
│   │   ├── epd_gfx.c / .h
│   │   ├── epd_font.h
│   │   ├── wifi_manager.c / .h
│   │   ├── captive_portal.c / .h
│   │   ├── api_client.c / .h      # NEW: HTTP client do pobierania danych z API
│   │   └── screen_manager.c / .h  # NEW: logika rotacji ekranów co 5 min
│   ├── platformio.ini
│   ├── partitions.csv
│   ├── sdkconfig.defaults
│   └── CMakeLists.txt
│
├── api/                        # FastAPI backend (Hexagonal + Command Bus + Events)
│   ├── pyproject.toml          # uv project (dependencies, ruff config)
│   ├── uv.lock
│   ├── Dockerfile
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app, prepare() rejestruje subscribers
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   │
│   │   ├── domain/             # HEXAGON CORE — pure Python, zero deps
│   │   │   ├── models/         # Domain entities (dataclasses)
│   │   │   │   ├── screen.py   # Screen, ScreenType
│   │   │   │   ├── alarm.py    # Alarm, AlarmStatus
│   │   │   │   └── device.py   # DeviceStatus
│   │   │   ├── ports/          # Interfaces (ABC) — repository contracts
│   │   │   │   ├── screen_repository.py
│   │   │   │   ├── alarm_repository.py
│   │   │   │   └── device_repository.py
│   │   │   └── events/         # Domain events (frozen dataclasses)
│   │   │       ├── base.py     # Event base class
│   │   │       ├── screen.py   # ScreenCreated/Updated/Deleted
│   │   │       ├── alarm.py    # AlarmCreated/Triggered
│   │   │       └── device.py   # DeviceHeartbeatReceived
│   │   │
│   │   ├── infrastructure/     # ADAPTERS — framework-dependent code
│   │   │   ├── container.py    # IoC Container (DI, inject())
│   │   │   ├── command_bus.py  # CommandBus interface + SimpleCommandBus
│   │   │   ├── decorators.py   # @transactional (session + event dispatch)
│   │   │   ├── commands/       # BaseCommand, SubscriberCommand (ABC)
│   │   │   ├── events/         # EventBus, SyncSubscriber
│   │   │   │   ├── event_bus.py    # publish() + dispatch()
│   │   │   │   └── subscriber.py   # SyncSubscriber base class
│   │   │   └── persistence/    # OUTBOUND ADAPTER — SQLAlchemy
│   │   │       ├── database.py     # async engine, session factory, Base
│   │   │       ├── models/         # ORM models (ScreenORM, AlarmORM, ...)
│   │   │       └── repositories/   # Port implementations (SqlScreenRepo, ...)
│   │   │
│   │   ├── application/        # USE CASES — Commands + Subscribers
│   │   │   ├── commands/       # BaseCommand subclasses (@transactional)
│   │   │   │   ├── screen_commands.py   # Create/Update/Delete/List/GetCurrent
│   │   │   │   ├── alarm_commands.py
│   │   │   │   └── device_commands.py
│   │   │   └── subscribers/    # SubscriberCommand subclasses (NO @transactional)
│   │   │       ├── screen_subscribers.py
│   │   │       └── device_subscribers.py
│   │   │
│   │   └── adapters/           # INBOUND ADAPTER — FastAPI
│   │       └── inbound/api/
│   │           ├── dependencies.py  # get_command_bus()
│   │           ├── schemas/         # Pydantic DTOs (request/response)
│   │           └── routers/         # FastAPI routers (call CommandBus only)
│   │
│   ├── alembic/                # DB migrations
│   │   └── ...
│   ├── tests/
│   └── ruff.toml
│
├── web/                        # Next.js frontend
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── .eslintrc.json
│   ├── .prettierrc
│   ├── Dockerfile
│   ├── src/
│   │   ├── app/                # App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx        # Dashboard — aktualny stan ekranu
│   │   │   ├── screens/        # Zarządzanie ekranami
│   │   │   ├── alarms/         # Zarządzanie alarmami
│   │   │   └── settings/       # Ustawienia
│   │   ├── components/
│   │   ├── lib/
│   │   │   └── api.ts          # API client (fetch wrapper)
│   │   └── types/
│   └── public/
│
├── mobile/                     # React Native (Expo)
│   ├── package.json
│   ├── app.json / app.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts      # NativeWind
│   ├── src/
│   │   ├── app/                # Expo Router (file-based)
│   │   │   ├── _layout.tsx
│   │   │   ├── index.tsx       # Dashboard
│   │   │   ├── screens/
│   │   │   ├── alarms/
│   │   │   └── bluetooth/      # BLE connection to ESP32
│   │   ├── components/
│   │   ├── lib/
│   │   │   ├── api.ts          # API client
│   │   │   └── ble.ts          # BLE service (react-native-ble-plx)
│   │   └── types/
│   └── eas.json                # Expo EAS Build config
│
├── deployment/                 # Docker Compose + nginx
│   ├── docker-compose.yml
│   ├── nginx/
│   │   └── nginx.conf
│   └── .env.example
│
├── .github/
│   └── workflows/
│       ├── deploy.yml          # CI/CD: build + deploy API & Web to VPS
│       └── firmware.yml        # CI: build firmware (opcjonalnie)
│
├── PLAN.md                     # Ten plik
├── .gitignore
└── README.md
```

---

## 4. API Design (FastAPI)

### Base URL: `https://paperassist.tojest.dev/api/v1`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/screens` | Lista wszystkich ekranów |
| `GET` | `/screens/current` | Aktualny ekran (dla ESP32) |
| `POST` | `/screens` | Utwórz nowy ekran |
| `PUT` | `/screens/{id}` | Edytuj ekran |
| `DELETE` | `/screens/{id}` | Usuń ekran |
| `GET` | `/alarms` | Lista alarmów |
| `POST` | `/alarms` | Utwórz alarm |
| `PUT` | `/alarms/{id}` | Edytuj alarm |
| `DELETE` | `/alarms/{id}` | Usuń alarm |
| `GET` | `/device/status` | Status urządzenia (last seen, IP, etc.) |
| `POST` | `/device/heartbeat` | Heartbeat od ESP32 |

### Tech Stack Details
- **uv** — package manager (zamiast pip/poetry)
- **ruff** — linter + formatter
- **pydantic v2** — walidacja danych
- **SQLAlchemy 2.0** — async ORM
- **PostgreSQL** — baza danych (Docker)
- **Alembic** — migracje

### Architecture: Hexagonal + Command Bus + Events

Architektura backendowa wzorowana na ARCHITECTURE_PLAN.md:

```
HTTP Request
  │
  ▼
Router (inbound adapter)
  │  command_bus.execute(CreateScreenCommand, params={...})
  ▼
SimpleCommandBus
  │  tworzy instancję komendy, wstrzykuje zależności (inject)
  ▼
CreateScreenCommand.handle()     ← @transactional
  │
  │  ┌─ @transactional otwiera transakcję ─────────────────┐
  │  │                                                      │
  │  │  1. screen_repository.create(screen)                 │
  │  │  2. event_bus.publish(ScreenCreatedEvent(...))       │
  │  │     → event trafia do kolejki                        │
  │  │                                                      │
  │  │  3. session.flush()       ← sprawdzenie constraints  │
  │  │  4. event_bus.dispatch()  ← wykonanie subscribers    │
  │  │     │                                                │
  │  │     └─ LogScreenCreatedSubscriber                    │
  │  │        → LogScreenCreatedCommand.handle()            │
  │  │          (SubscriberCommand — BEZ @transactional)    │
  │  │                                                      │
  │  │  5. session.commit()      ← WSZYSTKO zapisane        │
  │  └─ session.close() ──────────────────────────────────┘
  │
  ▼
Response
```

**Kluczowe zasady:**

| Zasada | Szczegół |
|--------|----------|
| `@transactional` | TYLKO na `BaseCommand.handle()` |
| `SubscriberCommand` | NIGDY z `@transactional` — działa w istniejącej transakcji |
| Router | TYLKO woła `CommandBus` — nigdy repo/service bezpośrednio |
| Domain models | Pure Python dataclasses — zero zależności od frameworka |
| Domain ports | ABC interfaces — kontrakt definiowany przez domenę |
| Events | Frozen dataclasses — immutable, `publish()` → kolejka, `dispatch()` w `@transactional` |
| Container | IoC — `inject()` wstrzykuje repo + event_bus do command instance |

---

## 5. Infrastructure & Deployment

### 5.1 VPS Setup (bill210.mikrus.xyz)

```
Docker Engine
├── nginx (port 80, reverse proxy)
│   ├── paperassist.tojest.dev/           → web:3000 (Next.js)
│   ├── paperassist.tojest.dev/api/       → api:8000 (FastAPI)
│   └── SSL: Let's Encrypt (certbot, jeśli dostępne)
├── api (FastAPI, port 8000)
├── web (Next.js, port 3000)
└── db  (PostgreSQL, port 5432, internal only)
```

### 5.2 Docker Compose (`deployment/docker-compose.yml`)

Serwisy:
- **db** — `postgres:16-alpine` — persistent volume
- **api** — `ghcr.io/thedmnmachine/paperassist-api:latest`
- **web** — `ghcr.io/thedmnmachine/paperassist-web:latest`
- **nginx** — `nginx:alpine` — reverse proxy, port 80

### 5.3 Nginx Config

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name paperassist.tojest.dev;

    # API proxy
    location /api/ {
        proxy_pass http://api:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Next.js frontend
    location / {
        proxy_pass http://web:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5.4 GitHub Secrets (wymagane)

| Secret | Value |
|--------|-------|
| `VPS_HOST_ADDRESS` | `bill210.mikrus.xyz` |
| `VPS_HOST_PORT` | `10210` |
| `VPS_HOST_PASSWORD` | `(hasło do VPS)` |
| `POSTGRES_USER` | `paperassist` |
| `POSTGRES_PASSWORD` | `(wygenerowane)` |
| `POSTGRES_DB` | `paperassist` |

---

## 6. CI/CD Pipeline (`.github/workflows/deploy.yml`)

### Trigger: push to `main`

### Steps:
1. **Checkout** repo
2. **Build** Docker images (api + web)
3. **Push** to GitHub Container Registry (`ghcr.io`)
4. **SSH** to VPS:
   - Upload `deployment/` folder
   - Create `.env` with secrets
   - `docker compose pull`
   - `docker compose down`
   - `docker compose up -d`

### Opcjonalnie: `firmware.yml`
- Build firmware z PlatformIO w CI
- Artefakty `.bin` do GitHub Releases

---

## 7. Firmware Enhancements (ESP32)

### Nowe moduły do dodania:

1. **`api_client.c/h`** — HTTP client (esp_http_client)
   - `GET /api/v1/screens/current` — pobieranie aktualnego ekranu
   - `POST /api/v1/device/heartbeat` — raportowanie statusu
   - JSON parsing (cJSON, wbudowany w ESP-IDF)

2. **`screen_manager.c/h`** — logika wyświetlania
   - Timer 5 min → fetch nowego ekranu
   - Parsowanie danych → renderowanie na e-paper
   - Obsługa alarmów (specjalne ekrany, buzzer)

3. **BLE Service** (przyszłość)
   - GATT server do komunikacji z apką mobilną
   - Komendy: podgląd statusu, wymuś odświeżenie, zmień config

### API URL Configuration
- Domyślnie: `http://paperassist.tojest.dev/api/v1`
- Konfigurowalne przez captive portal lub BLE

---

## 8. Implementation Order (Priorities)

### Phase 1: Infrastructure (TERAZ)
- [x] Istniejący kod ESP32 (WiFi, captive portal, e-paper driver)
- [ ] **Git repo setup** — push istniejącego kodu
- [ ] **VPS setup** — Docker, nginx
- [ ] **CI/CD pipeline** — GitHub Actions
- [ ] **Scaffold API** — FastAPI + Docker + basic health endpoint
- [ ] **Scaffold Web** — Next.js + Docker + basic page
- [ ] **Deploy** — pierwsza wersja na VPS

### Phase 2: Core API + Web
- [ ] Database schema (screens, alarms, device)
- [ ] CRUD endpoints (screens, alarms)
- [ ] Web dashboard (wyświetlanie stanu)
- [ ] Web editor (edycja ekranów/alarmów)

### Phase 3: ESP32 Integration
- [ ] HTTP client w firmware
- [ ] Screen manager (rotacja co 5 min)
- [ ] Heartbeat reporting
- [ ] Alarm handling

### Phase 4: Mobile App
- [ ] Expo project scaffold
- [ ] API client (shared types with web)
- [ ] BLE connection (react-native-ble-plx)
- [ ] Dashboard + editor screens

### Phase 5: Polish
- [ ] SSL/TLS na VPS (certbot)
- [ ] Push notifications (web + mobile)
- [ ] Auth (jeśli potrzebne)
- [ ] OTA updates dla ESP32

---

## 9. Best Practices Applied

### General
- **Monorepo** z czystym podziałem na komponenty
- **Conventional commits** (feat:, fix:, chore:, docs:)
- **.env** nigdy w repo — `.env.example` jako template
- **Docker multi-stage builds** — mniejsze obrazy

### API (Python / Hexagonal Architecture)
- **uv** zamiast pip — szybsze, lockfile
- **ruff** zamiast black+isort+flake8 — all-in-one
- **Pydantic v2** — szybsza walidacja
- **Async** SQLAlchemy — lepszy performance
- **Alembic** — kontrolowane migracje
- **Hexagonal Architecture** — domain core niezależny od frameworka
- **Command Bus** — oddziela wywołanie operacji od implementacji
- **Domain Events + Subscribers** — loosely coupled side-effects
- **@transactional** — automatyczny session management + event dispatch
- **IoC Container** — dependency injection bez zewnętrznych bibliotek

### Web (Next.js)
- **App Router** (Next.js 14+)
- **TypeScript strict** mode
- **ESLint + Prettier** — spójny styl
- **Tailwind CSS** — utility-first
- **Server Components** gdzie możliwe

### Mobile (React Native)
- **Expo Router** — file-based routing
- **NativeWind** — Tailwind w React Native
- **EAS Build** — cloud builds
- **TypeScript strict**

### Firmware (C / ESP-IDF)
- Modularny kod (osobne .c/.h per feature)
- NVS dla konfiguracji
- Deep sleep między odświeżeniami (oszczędzanie baterii)
- Error handling z ESP_ERROR_CHECK / graceful fallback

### CI/CD
- Docker images w GHCR (darmowe dla public repos)
- Automatyczny deploy na push do main
- Secrets w GitHub — nigdy w kodzie
- Health checks w docker-compose

---

## 10. Quick Reference

| What | Where |
|------|-------|
| VPS SSH | `ssh -p 10210 root@bill210.mikrus.xyz` |
| API URL | `https://paperassist.tojest.dev/api/v1` |
| Web URL | `https://paperassist.tojest.dev` |
| GHCR API | `ghcr.io/thedmnmachine/paperassist-api` |
| GHCR Web | `ghcr.io/thedmnmachine/paperassist-web` |
| GitHub Repo | `github.com/TheDMNMachine/PaperAssist` |
