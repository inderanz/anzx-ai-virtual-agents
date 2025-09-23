# ANZx.ai Simulation Session Summary (2025-09-20)

This document summarizes the steps taken, challenges encountered, and resolutions reached during the simulation of the "Sarah, the E-commerce Entrepreneur" persona journey. 

## Objective

To perform and document an end-to-end simulation of a new customer (Sarah) onboarding onto the ANZx.ai platform. This includes:
1. Registering a new user and organization.
2. Uploading a custom knowledge base (product CSV, FAQ, policy document).
3. Simulating an end-user interacting with the newly trained AI assistant.

## Chronological Log of Actions & Debugging

### 1. Initial Setup
- **Action**: Created dummy data files for Sarah's business: `products.csv`, `faq.txt`, and `shipping_policy.txt`.
- **Goal**: Prepare realistic knowledge base sources for upload.

### 2. Blocker 1: Authentication Flow
- **Attempt**: Tried to register a user via a standard email/password endpoint (`POST /api/v1/auth/register`).
- **Error**: `404 Not Found`.
- **Investigation**: Read `services/core-api/app/routers/auth.py`.
- **Finding**: The API does not use email/password registration. It relies exclusively on Google Sign-In and requires a `firebase_token`.
- **Resolution**: Decided to ask the user to perform the browser-based Google Sign-In to generate a real `firebase_token`.

### 3. Blocker 2: Firebase Frontend Configuration
- **Attempt**: The user accessed the live frontend at `https://extreme-gecko-466211-t1.web.app` to sign in.
- **Error**: `Firebase: Error (auth/configuration-not-found)`.
- **Investigation**: 
    1. Read `services/auth-frontend/.firebaserc` to confirm the project ID.
    2. Read `services/auth-frontend/src/firebase-config.js` to verify the frontend configuration.
- **Finding**: The frontend configuration was correct. The error indicated a backend configuration issue within the Firebase project console itself.
- **Resolution**: Provided the user with step-by-step instructions to:
    1. Enable "Google" as a sign-in provider in the Firebase console.
    2. Add `extreme-gecko-466211-t1.web.app` to the list of "Authorized domains".

### 4. Blocker 3: API Endpoint Not Found
- **Success**: The user successfully resolved the Firebase configuration issue and provided a valid `firebase_token`.
- **Attempt**: Tried to call `POST /api/v1/auth/register` with the valid token.
- **Error**: `404 Not Found` from the `core-api` server.
- **Investigation & Root Cause Analysis**:
    1. Confirmed the endpoint was defined in `auth.py` and included in `main.py`.
    2. Hypothesized the running Docker container was using stale code. Asked the user to rebuild.
    3. The user correctly challenged this assumption.
    4. Re-investigated and discovered the true root cause: The `services/core-api/Dockerfile` was installing dependencies from `requirements-simple.txt` instead of the full `requirements.txt`.
    5. Compared the two files and confirmed that `requirements-simple.txt` was missing the necessary libraries for the authentication service to load correctly.
- **Resolution**: Modified the `services/core-api/Dockerfile` to use `requirements.txt` for dependency installation.

## Current Status & Next Steps

**Status**: 
- The root cause of the `404 Not Found` error has been identified and fixed in the `Dockerfile`.
- The fix has been applied to the file system.

**Action Required from User**:
- The user needs to rebuild the `core-api` Docker image with the corrected `Dockerfile` and restart the services. The commands to run are:
  ```bash
  make build
  make down && make up
  ```

**Next Step for LLM**:
- Once the user confirms the services have been rebuilt and restarted, the immediate next step is to execute the following `curl` command again. It is expected to succeed this time.
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/register" -H "Content-Type: application/json" -d '{
    "firebase_token": "<USER_PROVIDED_FIREBASE_TOKEN>",
    "organization_name": "Sarahs Leather Goods"
  }'
  ```
- After successful registration, proceed with uploading the knowledge base files using the `access_token` from the registration response.
