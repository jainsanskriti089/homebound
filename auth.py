import os
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse

from db import get_or_create_default_user, save_tokens

router = APIRouter()

CLIENT_ID = os.getenv("TESLA_CLIENT_ID")
CLIENT_SECRET = os.getenv("TESLA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TESLA_REDIRECT_URI")

AUTH_URL = "https://auth.tesla.com/oauth2/v3/authorize"
TOKEN_URL = "https://auth.tesla.com/oauth2/v3/token"
SCOPES = "openid offline_access vehicle_device_data vehicle_location"

pending_states = set()
token_store = {}

@router.get('/login')
def login():
    state = secrets.token_urlsafe(16)
    pending_states.add(state)

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
    }

    url = f"{AUTH_URL}?{urlencode(params)}"
    print("LOGIN URL: ", url)
    return RedirectResponse(url)

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        return JSONResponse({"error": "no code returned"}, status_code = 400)

    if state not in pending_states:
        return JSONResponse({"error": "invalid or missing state"}, status_code=400)
    pending_states.discard(state)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL, 
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code, 
                "redirect_uri": REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    if response.status_code != 200:
        return JSONResponse(
            {"error": "token exchange failed", "detail": response.text},
            status_code=400,
        )

    tokens = response.json()
    user_id = get_or_create_default_user()
    save_tokens(user_id, tokens)

    return {"status": "authorized", "tokens_received": list(tokens.keys())}