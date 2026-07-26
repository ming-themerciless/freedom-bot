from __future__ import annotations
import logging
from typing import List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import SERVICE_ACCOUNT_INFO, GUILD_SHEET_ID

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_service = None

def _get_service():
    global _service
    if _service is None:
        creds = service_account.Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO, scopes=_SCOPES
        )
        _service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    return _service

def get_values(a1_range: str, value_render_option: str = "UNFORMATTED_VALUE"):
    svc = _get_service()
    sheet = svc.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=GUILD_SHEET_ID,
        range=a1_range,
        valueRenderOption=value_render_option
    ).execute()
    return result.get("values", [])

def batch_update(updates: List[Dict[str, Any]], value_input_option: str = "USER_ENTERED"):
    if not updates:
        return
    svc = _get_service()
    body = {"valueInputOption": value_input_option, "data": updates}
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=GUILD_SHEET_ID,
        body=body
    ).execute()
