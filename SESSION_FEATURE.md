# Session Management Feature

This document describes the new session management feature that allows users to create gaming sessions and add matches in real-time.

## Overview

The session management feature enables users to:
- Create new gaming sessions with automatic date-based naming
- Add matches to active sessions
- End sessions when gaming is complete
- Prevent adding matches to ended sessions

## Usage

### Activating Game Mode

To use the session management features, add the `?gameon` query parameter to the URL:

```
http://localhost:5173/?gameon
```

### Creating a Session

1. Navigate to the app with `?gameon` parameter
2. Click the "Start New Session" button
3. A new session will be created with the current date
4. If a session already exists for that date, it will be numbered (e.g., "11/7/2025 #2")

### Adding Matches

1. With an active session, click "Add Match"
2. Fill in the player names (autocomplete available from existing players)
3. Enter the scores for each team
4. Click "Add Match" to save

### Ending a Session

1. Click "End Session" button
2. Confirm in the modal dialog
3. The session will be marked as inactive
4. No more matches can be added to that session

## Technical Details

### Database Schema Changes

#### New Tables

**sessions**
- `id`: Primary key
- `date`: Date of the session (format: M/D/YYYY)
- `name`: Display name (e.g., "11/7/2025" or "11/7/2025 #2")
- `is_active`: Boolean flag (1 = active, 0 = ended)
- `created_at`: Timestamp of creation

**matches** (updated)
- Added `session_id`: Foreign key to sessions table (nullable for legacy matches)

### API Endpoints

#### GET /api/sessions
Get all sessions ordered by date (most recent first)

**Response:**
```json
[
  {
    "id": 1,
    "date": "11/7/2025",
    "name": "11/7/2025",
    "is_active": true,
    "created_at": "2025-11-07T14:30:00"
  }
]
```

#### GET /api/sessions/active
Get the currently active session, if any

**Response:**
```json
{
  "id": 1,
  "date": "11/7/2025",
  "name": "11/7/2025",
  "is_active": true,
  "created_at": "2025-11-07T14:30:00"
}
```

#### POST /api/sessions
Create a new session

**Request:**
```json
{
  "date": "11/7/2025"  // Optional, defaults to current date
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Session created successfully",
  "session": {
    "id": 1,
    "date": "11/7/2025",
    "name": "11/7/2025",
    "is_active": true,
    "created_at": ""
  }
}
```

#### POST /api/sessions/{session_id}/end
End a session (mark as inactive)

**Response:**
```json
{
  "status": "success",
  "message": "Session 1 ended successfully"
}
```

#### POST /api/matches/create
Create a new match in a session

**Request:**
```json
{
  "session_id": 1,
  "team1_player1": "Alice",
  "team1_player2": "Bob",
  "team2_player1": "Charlie",
  "team2_player2": "Dave",
  "team1_score": 21,
  "team2_score": 19
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Match created successfully",
  "match_id": 42,
  "session_id": 1
}
```

### Frontend Components

#### New Components

1. **AddMatchModal** (`frontend/src/components/AddMatchModal.jsx`)
   - Modal form for adding new matches
   - Includes player autocomplete using datalist
   - Validates all fields before submission

2. **ConfirmationModal** (`frontend/src/components/ConfirmationModal.jsx`)
   - Reusable confirmation dialog
   - Used for ending sessions

#### Updated Components

1. **MatchesTable** (`frontend/src/components/MatchesTable.jsx`)
   - Now shows session controls when `?gameon` is active
   - Displays "Start New Session" button when no active session
   - Shows active session info with "Add Match" and "End Session" buttons

2. **DataContext** (`frontend/src/contexts/DataContext.jsx`)
   - Added session state management
   - New methods: `handleCreateSession`, `handleEndSession`, `handleCreateMatch`
   - Loads sessions and active session on mount

3. **App.jsx** (`frontend/src/App.jsx`)
   - Passes session-related props to MatchesTable

### Styling

All new components follow the existing vintage Malibu beach volleyball theme:
- Retro color palette (sunset orange, ocean blue, sand, etc.)
- Bold borders and box shadows
- Responsive design for mobile devices
- Smooth animations and transitions

## Migration

For existing databases, run the migration script to add the new tables and columns:

```bash
cd backend/database
python migrate_add_sessions.py
```

Or from the project root:

```bash
python backend/database/migrate_add_sessions.py
```

The migration script:
- Creates the `sessions` table with indexes
- Adds `session_id` column to `matches` table
- Is idempotent (safe to run multiple times)

## Notes

- Legacy matches (created before this feature) will have `session_id = NULL`
- ELO changes for newly added matches are currently set to 0
- To recalculate ELO for all matches including new ones, use the "Recalculate Stats" button
- New players can be created on-the-fly when adding matches
- Session names are automatically incremented if multiple sessions are created on the same date

## Future Enhancements

Possible future improvements:
- Live ELO calculation during active sessions
- Session statistics and summaries
- Edit/delete matches within a session
- Session templates or presets
- Multi-day tournament support


