# Homebound

Every night, dinner was either ready too early and getting cold, or started too late because nobody knew exactly when my parents were actually leaving work. Texting "on my way" only works if someone remembers to send it — so I decided to make the car do the telling instead.

Homebound watches a Tesla's location and fires a notification the moment it leaves a saved place, like a workplace. No more guessing, no more reheated food, no more "leaving now" texts sent from the parking lot ten minutes after they'd actually left.

Under the hood, it's a real dive into OAuth2 authentication, background job scheduling, and working with a live third-party API that has real-world constraints — regional infrastructure, token expiry, key-based device trust — rather than a tidy textbook example.

## What it does

- Authenticates securely with Tesla's Fleet API via OAuth2 — no passwords ever touch this app
- Reads live vehicle location data (read-only — no remote commands)
- Detects when the vehicle exits a user-defined geofence
- Sends a push notification on exit
- Uses a two-tier adaptive polling schedule (infrequent baseline polling, more frequent polling during an expected departure window) to balance real-time accuracy against API usage

## Architecture

```
homebound/
├── main.py              # FastAPI app entry point, route registration
├── auth.py               # Tesla OAuth: login, callback, token refresh
├── vehicle.py             # Vehicle data API calls (list vehicles, location)
├── db.py                 # SQLite persistence (users, tokens, locations, events)
├── scripts/
│   └── partner_setup.py  # One-time app-level region registration with Tesla
├── requirements.txt
├── .env                   # Local secrets (gitignored)
└── .gitignore
```

**Why this structure:** OAuth logic, vehicle API calls, and persistence are kept in separate modules rather than one large file, using FastAPI's router pattern — makes each piece independently testable and keeps `main.py` as a thin entry point.

## Tech stack

| Piece | Tool | Why |
|---|---|---|
| Backend | Python + FastAPI | Fast to build, async support for external API calls |
| Vehicle data | [Tesla Fleet API](https://developer.tesla.com) | Official OAuth2-based API, no reverse-engineering required |
| Database | SQLite | Zero-setup persistence appropriate for a single-vehicle personal project |
| HTTP client | httpx | Async-compatible requests to Tesla's API |
| Key hosting | GitHub Pages | Free HTTPS hosting for the required public key file |

## Setup

### 1. Prerequisites
- Python 3.10+
- A Tesla account (does not need to own a vehicle to register the app)
- A verified Tesla Developer account with MFA enabled

### 2. Register a Tesla Developer application
1. Go to [developer.tesla.com](https://developer.tesla.com) and register an application
2. Request scopes: `vehicle_device_data`, `vehicle_location`
3. Save your Client ID and Client Secret (the secret is shown once)

### 3. Generate and host your key pair
```bash
openssl ecparam -name prime256v1 -genkey -noout -out private-key.pem
openssl ec -in private-key.pem -pubout -out public-key.pem
```
Publish `public-key.pem` (renamed) at:
```
https://<your-domain>/.well-known/appspecific/com.tesla.3p.public-key.pem
```
Keep `private-key.pem` local only — never commit it.

### 4. Environment variables
Create a `.env` file in the project root:
```
TESLA_CLIENT_ID=your_client_id
TESLA_CLIENT_SECRET=your_client_secret
TESLA_REDIRECT_URI=http://localhost:8000/callback
TESLA_API_BASE=https://fleet-api.prd.na.vn.cloud.tesla.com
```
(Use the Fleet API base URL matching your account's region.)

### 5. Install dependencies
```bash
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
```

### 6. One-time region registration
Your application must be registered with Tesla's regional API infrastructure before any user tokens will work:
```bash
python -c "
import asyncio
from scripts.partner_setup import register_domain
asyncio.run(register_domain())
"
```

### 7. Run the app
```bash
uvicorn main:app --reload
```
Visit `http://localhost:8000/login` to start the OAuth flow. After granting consent, tokens are stored in `homebound.db`.

### 8. Pair the virtual key
With the vehicle owner and the car physically present, complete virtual key pairing via the Tesla mobile app — this step cannot be done remotely.

## Security notes

- OAuth tokens are stored locally in SQLite; encryption at rest is planned before any production use
- The app requests read-only scopes only — no vehicle command access
- Private keys and `.env` are gitignored and never committed

## Roadmap

- [x] Tesla OAuth2 authentication (login, consent, token refresh)
- [x] Vehicle API access and region registration
- [ ] Geofence detection logic
- [ ] Adaptive two-tier polling scheduler
- [ ] Push notifications
- [ ] Deployment
- [ ] Multi-user support (stretch goal)
