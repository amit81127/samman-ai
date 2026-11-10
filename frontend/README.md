# SAMAAN AI — Frontend

AI-powered Augmentative and Alternative Communication (AAC) web platform built with React, TypeScript, Tailwind CSS, and Vite.

## Architecture

- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS v3 with SAMAAN AI Healthcare Design System
- **Icons**: Lucide React
- **Audio & TTS**: Gnani Timbre TTS (`/api/v1/messages/{id}/speech`) with fallback to browser Web Speech API
- **State & Stores**:
  - `useAuth`: Authentication, session persistence, and instant demo mode
  - `useSettings`: Accessibility preferences (speech rate, voice, tile size, text size, contrast, reduced motion) with automatic backend sync (`/api/v1/profile`)
  - `usePhrases`: Saved phrases library with favorites, category tagging, search, and communication board loading

## Integrated Backend Endpoints (/api/v1)

| Route / Module | Backend Endpoint | Functionality |
| :--- | :--- | :--- |
| **Auth** | `POST /auth/register` | Create account |
| **Auth** | `POST /auth/login` | Login and receive HttpOnly cookie + JWT |
| **Auth** | `POST /auth/logout` | Clear session |
| **Auth** | `GET /auth/me` | Fetch active user identity |
| **Profile** | `GET /profile` | Fetch user accessibility settings |
| **Profile** | `PATCH /profile` | Update accessibility preferences |
| **Messages** | `POST /messages/compose` | Compose symbol concepts, get literal + AI candidates |
| **Messages** | `GET /messages` | List recent approved messages |
| **Approvals** | `POST /messages/{id}/approve` | User approval invariant before speech playback |
| **Approvals** | `DELETE /messages/{id}/approval` | Invalidate approval for re-editing |
| **Speech** | `POST /messages/{id}/speech` | Synthesize audio wav using Gnani TTS |
| **Phrases** | `GET /phrases` | List user's saved phrases |
| **Phrases** | `POST /phrases` | Save new phrase to library |
| **Phrases** | `PATCH /phrases/{id}` | Update existing phrase |
| **Phrases** | `DELETE /phrases/{id}` | Delete phrase |
| **Boards** | `GET /boards` | List user's vocabulary boards |
| **Boards** | `POST /boards` | Create custom vocabulary board |
| **Boards** | `PATCH /boards/{id}` | Edit board |
| **Boards** | `DELETE /boards/{id}` | Delete board |
| **Vocabulary** | `GET /boards/{id}/vocabulary` | List symbol tiles on board |
| **Vocabulary** | `POST /boards/{id}/vocabulary` | Add custom symbol tile |
| **Vocabulary** | `DELETE /vocabulary/{item_id}` | Remove symbol tile |
| **Partners** | `GET /partners` | List active partner permissions |
| **Partners** | `POST /partners` | Grant access permissions to a caregiver/partner |
| **Partners** | `DELETE /partners/{id}` | Revoke partner access |

## Running the Application

### 1. Start the Backend (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start the Frontend (Vite)
```bash
cd frontend
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) in your browser.
