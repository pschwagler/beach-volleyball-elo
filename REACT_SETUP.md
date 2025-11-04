# React Frontend Setup Guide

## ✅ What Was Built

Your Beach Volleyball ELO app now has a modern React frontend with:

- **React 18** with Vite for fast development
- **Separated CSS** in `App.css` for easy styling
- **Component-based architecture** for maintainability
- **Axios** for clean API calls
- **Production builds** optimized for Railway deployment

## File Structure

```
beach-volleyball-elo/
├── frontend/                    # React app (NEW)
│   ├── src/
│   │   ├── App.jsx             # Main app component
│   │   ├── App.css             # All styles (separated!)
│   │   ├── main.jsx            # React entry point
│   │   ├── index.css           # Global styles
│   │   ├── components/
│   │   │   ├── ControlPanel.jsx      # Buttons and controls
│   │   │   ├── RankingsTable.jsx     # Sortable rankings table
│   │   │   └── PlayerDetails.jsx     # Player stats modal
│   │   └── services/
│   │       └── api.js          # API client with axios
│   ├── dist/                   # Production build (generated)
│   ├── package.json
│   ├── vite.config.js          # Vite configuration
│   └── index.html
├── api.py                       # FastAPI backend (UPDATED to serve React)
├── elo_calculator.py            # Core logic
├── build.sh                     # Build script (NEW)
└── ...
```

## Components Overview

### `ControlPanel.jsx`
- Recalculate Stats button
- Link to Google Sheets
- Manages loading states

### `RankingsTable.jsx`
- Displays sortable rankings
- Click column headers to sort
- Click player names to view details
- Formats point differentials with +/-

### `PlayerDetails.jsx`
- Shows overall player stats
- Partnership statistics
- Opponent statistics
- Close button to dismiss

### `services/api.js`
- Axios-based API client
- All API endpoints wrapped in functions
- Handles errors gracefully

## Local Development

### Option 1: Production Build (What Users Will See)

```bash
# Build the React app
cd frontend
npm run build
cd ..

# Or use the build script
bash build.sh

# Start the API server
uvicorn api:app --reload

# Visit http://localhost:8000
```

### Option 2: Development Mode (With Hot Reload)

**Terminal 1 - Backend:**
```bash
cd /Users/patrick/repos/beach-volleyball-elo
source venv/bin/activate
uvicorn api:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd /Users/patrick/repos/beach-volleyball-elo/frontend
npm run dev
```

Then visit **http://localhost:3000** for hot-reload React development.

The Vite config proxies `/api` requests to the backend at `localhost:8000`.

## Testing Locally

1. **Start the backend** (Terminal 1):
   ```bash
   cd /Users/patrick/repos/beach-volleyball-elo
   source venv/bin/activate
   uvicorn api:app --reload
   ```

2. **Build frontend** (if not in dev mode):
   ```bash
   cd frontend && npm run build && cd ..
   ```

3. **Visit** http://localhost:8000
   - Should see React app with purple gradient background
   - Click "Recalculate Stats" to pull from Google Sheets
   - View rankings and click players for details

## Modifying Styles

All styles are now in **`frontend/src/App.css`**!

To change colors, spacing, fonts, etc.:
1. Edit `frontend/src/App.css`
2. Rebuild: `cd frontend && npm run build`
3. Refresh browser

In development mode, changes are instant (no rebuild needed).

## Adding Features

### To modify the UI:

1. **Edit components** in `frontend/src/components/`
2. **Update styles** in `frontend/src/App.css`
3. **Rebuild** with `npm run build` (or use `npm run dev` for hot reload)

### To add new API endpoints:

1. **Add endpoint** in `api.py`
2. **Add client function** in `frontend/src/services/api.js`
3. **Use in components** via import

## Railway Deployment

The updated `railway.json` now includes frontend build step:

```json
{
  "deploy": {
    "startCommand": "cd frontend && npm install && npm run build && cd .. && uvicorn api:app --host 0.0.0.0 --port $PORT"
  }
}
```

Railway will:
1. Install Node.js dependencies
2. Build React app
3. Install Python dependencies
4. Start FastAPI server
5. Serve React from `/`

## Benefits of React Version

✅ **Separated CSS** - Easy to modify styles
✅ **Component-based** - Reusable UI pieces
✅ **State management** - Clean data flow
✅ **Modern tooling** - Vite for fast builds
✅ **Developer experience** - Hot reload during development
✅ **Production optimized** - Minified, tree-shaken builds

## Troubleshooting

### React app not loading

1. Make sure you built it: `cd frontend && npm run build`
2. Check `frontend/dist/` exists
3. Restart API server

### API calls failing in development

1. Make sure backend is running on port 8000
2. Check `vite.config.js` proxy settings
3. Check browser console for errors

### Styles not updating

1. Rebuild frontend: `npm run build`
2. Hard refresh browser (Cmd+Shift+R)
3. Or use dev mode for instant updates

## Next Steps

- ✅ React frontend created
- ✅ CSS separated into App.css
- ✅ Components built
- ✅ Production build working
- ⏳ Ready to deploy to Railway

**Deploy to Railway** following the updated `RAILWAY_DEPLOYMENT.md` guide!

