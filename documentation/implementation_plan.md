# Implementation Plan - WebSocket Authentication & Handshake

The goal is to secure the WebSocket endpoint `/ws/record` with a strict JSON handshake that must occur within 10 seconds.

## User Review Required

> [!IMPORTANT]
> **Protocol Change**: Clients connecting to `/ws/record` MUST now send a JSON frame as the very first message within 10 seconds.
> **Format**:
> ```json
> {
>   "token": "AUTHORIZATION_TOKEN",
>   "name": "Meeting Name",
>   "meeting_link": "http://...",
>   "org_id": "optional_org_id"
> }
> ```
> If validation fails, the connection closes with code 4001 (or similar) or sends `{ "status": "error" }` then closes.
> If success, server sends `{ "status": "ok" }` and proceeds to receive binary audio chunks.

## Proposed Changes

### Router Implementation

#### [MODIFY] [recordings_router.py](file:///d:/Work/EATech/project-eazzmeetings/eazzmeetings/app/routers/recordings_router.py)
- Import `asyncio`, `WebSocketDisconnect`, `status` from `fastapi`.
- Import `decode_token` from `app.security`.
- **`websocket_endpoint` logic**:
    - `await websocket.accept()`
    - Start `asyncio.wait_for(..., timeout=10.0)` block.
    - Wait for `websocket.receive_json()`.
    - Validate fields: `token`, `name`, `meeting_link`.
    - Call `decode_token(token)`. If None/Invalid -> Close.
    - If valid, store `name`/metadata for the session filename.
    - Send `{"status": "ok"}`.
    - Enter streaming loop (receive bytes -> append).

## Verification Plan

### Automated Tests
#### [NEW] [verify_websocket_auth.py](file:///d:/Work/EATech/project-eazzmeetings/eazzmeetings/verify_websocket_auth.py)
- Use `websockets` library (install via `uv add websockets`).
- **Test 1: Valid Handshake**
    - Login (get token).
    - Connect WS.
    - Send valid JSON.
    - Expect "ok".
- **Test 2: Timeout**
    - Connect WS.
    - Wait 11s.
    - Assert connection closed.
- **Test 3: Invalid Token**
    - Connect WS.
    - Send garbage token.
    - Assert error/closure.

### Manual Verification
- Run `uv run verify_websocket_auth.py`.
