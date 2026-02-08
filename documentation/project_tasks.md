# Task: Complete Authentication Module

- [x] Exploration and Planning <!-- id: 0 -->
    - [x] Explore existing code in `app/schemas/users_schema.py`, `app/routers/auth_router.py`, `app/models/database/users_collection.py` <!-- id: 1 -->
    - [x] Check for existing auth services or utils <!-- id: 2 -->
    - [x] Create Implementation Plan <!-- id: 3 -->
- [ ] Implementation <!-- id: 4 -->
    - [x] Update/Create User Database Model <!-- id: 5 -->
    - [x] Update/Create User Schemas (Register, Login, Token, UserResponse) <!-- id: 6 -->
    - [x] Implement Password Hashing and Verification Utils <!-- id: 7 -->
    - [x] Implement JWT Token Generation and Verification <!-- id: 8 -->
    - [x] Refactor Auth Logic to Controller <!-- id: 15 -->
    - [x] Implement Auth Router (Register, Login endpoints) <!-- id: 9 -->
    - [x] Implement `get_current_user` dependency <!-- id: 10 -->
- [x] Verification <!-- id: 11 -->
    - [x] Verify Register Flow <!-- id: 12 -->
    - [x] Verify Login Flow <!-- id: 13 -->
    - [x] Verify Protected Route Access <!-- id: 14 -->

# Task: Audio Streaming & Upload Implementation

- [x] Exploration and Planning <!-- id: 16 -->
    - [x] Explore `app/routers/recordings_router.py` and `app/controllers/recordings_ctrl.py` <!-- id: 17 -->
    - [x] Explore `app/services/audio_utils.py` <!-- id: 18 -->
    - [x] Create Implementation Plan <!-- id: 19 -->
- [x] Implementation <!-- id: 20 -->
    - [x] Implement Audio Conversion Service (AAC -> Opus) <!-- id: 21 -->
    - [x] Implement Streaming/Chunk Ingestion Endpoint <!-- id: 22 -->
    - [x] Implement Manual File Upload Endpoint <!-- id: 23 -->
- [x] Verification <!-- id: 24 -->
    - [x] Verify Chunk Appending & Conversion <!-- id: 25 -->
    - [x] Verify Manual Upload <!-- id: 26 -->

# Task: WebSocket Authentication & Handshake

- [x] Exploration and Planning <!-- id: 27 -->
    - [x] Check `app/security.py` for `decode_token` <!-- id: 28 -->
    - [x] Create Implementation Plan <!-- id: 29 -->
- [x] Implementation <!-- id: 30 -->
    - [x] Install `websockets` library for verification <!-- id: 31 -->
    - [x] Modify `app/routers/recordings_router.py` <!-- id: 32 -->
        - [x] Implement 10s timeout <!-- id: 33 -->
        - [x] Implement JSON handshake validation (`name`, `meeting_link`, `org_id`, `token`) <!-- id: 34 -->
        - [x] Implement JWT verification using `security.decode_token` <!-- id: 35 -->
        - [x] Send "ok" or error JSON response <!-- id: 36 -->
- [x] Verification <!-- id: 37 -->
    - [x] Create `verify_websocket_auth.py` <!-- id: 38 -->
    - [x] Verify successful handshake <!-- id: 39 -->
    - [x] Verify timeout and invalid token scenarios <!-- id: 40 -->

# Task: Refactoring & Standardization

- [x] Implementation <!-- id: 41 -->
    - [x] Move WebSocket logic to `app/controllers/recordings_ctrl.py` <!-- id: 42 -->
    - [x] Create reusable security components (e.g., token validation helper) <!-- id: 43 -->
    - [x] Refactor `app/routers/recordings_router.py` to use controller <!-- id: 44 -->
- [x] Verification <!-- id: 45 -->
    - [x] successful verification of `verify_websocket_auth.py` <!-- id: 46 -->
