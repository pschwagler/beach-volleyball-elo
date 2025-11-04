# Beach Volleyball ELO API - Complete Guide

## 🎉 What You Have Now

A modern web application with:
- ✅ **React frontend** with separated CSS
- ✅ **FastAPI backend** with REST endpoints  
- ✅ **Google Sheets integration** for data input
- ✅ **JSON file storage** for calculated results
- ✅ **Railway-ready** deployment configuration

## 🚀 Quick Start (Local Testing)

### Start the Backend:

Stop any running server (Ctrl+C in terminal where uvicorn is running), then:

```bash
cd /Users/patrick/repos/beach-volleyball-elo
source venv/bin/activate

# Build the React frontend first
cd frontend && npm run build && cd ..

# Start the API server
uvicorn api:app --reload
```

### Visit the App:

Open your browser to **http://localhost:8000**

You should see:
- Purple gradient background
- "Beach Volleyball ELO Rankings" header
- Two buttons: "🔄 Recalculate Stats" and "📊 View Input Data"
- Rankings table (after clicking recalculate)

## 📱 Using the Application

### 1. First Time Setup

Click **"🔄 Recalculate Stats"**
- Reads data from your Google Sheets
- Calculates all ELO ratings and statistics
- Saves to JSON files in `output/` directory
- Displays results in the table

### 2. View Rankings

The table shows all players sorted by Points:
- **Name** - Click to see player details
- **Points** - Total points (3 per win, 1 per loss)
- **Games, Win Rate, Wins, Losses** - Performance stats
- **Avg Pt Diff** - Average point differential (with +/- sign)
- **ELO** - Current ELO rating

Click any **column header** to sort by that column.

### 3. View Player Details

Click any **player name** to see:
- **OVERALL** - Total stats for that player
- **WITH PARTNERS** - Stats with each partner (sorted by games played)
- **VS OPPONENTS** - Stats against each opponent (sorted by games played)

Each section shows: Points, Games, Wins, Losses, Win Rate, Avg Pt Diff

### 4. Update Data

When you add new matches to Google Sheets:
1. Click **"🔄 Recalculate Stats"**
2. Wait for success message
3. Rankings automatically refresh

## 🛠️ Development

### Frontend Development (with Hot Reload)

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

Visit **http://localhost:3000** - Changes to React code will instantly reload!

### Modifying Styles

Edit **`frontend/src/App.css`** to change:
- Colors
- Fonts  
- Spacing
- Layout
- Responsive breakpoints

In dev mode (`npm run dev`), changes appear instantly.
In production, rebuild with `npm run build`.

### Project Structure

```
Components:
- ControlPanel.jsx   → Buttons at top
- RankingsTable.jsx  → Main rankings table
- PlayerDetails.jsx  → Player stats modal

Styles:
- App.css           → All application styles
- index.css         → Global/reset styles

Services:
- api.js            → API client (axios)
```

## 🌐 API Endpoints

### POST `/api/calculate`
Recalculate stats from Google Sheets
```bash
curl -X POST http://localhost:8000/api/calculate
```

### GET `/api/rankings`
Get current rankings
```bash
curl http://localhost:8000/api/rankings
```

### GET `/api/players/{name}`
Get player details
```bash
curl http://localhost:8000/api/players/Patrick
```

### GET `/api/elo-timeline`
Get ELO history over time
```bash
curl http://localhost:8000/api/elo-timeline
```

### GET `/api/health`
Health check
```bash
curl http://localhost:8000/api/health
```

### GET `/docs`
Interactive API documentation
Visit: http://localhost:8000/docs

## 📦 Deployment to Railway

### Before Deploying:

1. **Commit all changes:**
   ```bash
   git add .
   git commit -m "Add React frontend and FastAPI backend"
   git push
   ```

2. **Prepare credentials:**
   - Copy contents of `credentials.json`
   - You'll paste this in Railway environment variables

### Deploy:

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose `beach-volleyball-elo` repository
5. Railway auto-detects and deploys

### Configure Environment:

1. In Railway dashboard → Variables tab
2. Add variable `CREDENTIALS_JSON`:
   ```json
   {
     "type": "service_account",
     "project_id": "...",
     ... (paste entire credentials.json)
   }
   ```
3. Save - Railway will auto-redeploy

### Get Your URL:

1. Settings → Domains
2. Click "Generate Domain"
3. Your app: `https://your-app.railway.app`

## 📊 Data Flow

```
Google Sheets (Input)
    ↓
POST /api/calculate
    ↓
elo_calculator.py (Process)
    ↓
JSON files (output/)
    ↓
GET /api/rankings
    ↓
React Frontend (Display)
```

## 🎨 Customization

### Change Colors

Edit `frontend/src/App.css`:

```css
/* Background gradient */
body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Primary button color */
button {
  background: #667eea;
}

/* Table header */
th {
  background: #667eea;
}
```

### Change Google Sheets Link

Edit `frontend/src/components/ControlPanel.jsx`:

```javascript
const GOOGLE_SHEETS_URL = 'https://docs.google.com/your-sheet-url';
```

### Modify Point System

Edit `elo_calculator.py`:

```python
@property
def points(self):
    """Calculate points: +3 for each win, +1 for each loss."""
    losses = self.game_count - self.win_count
    return (self.win_count * 3) + (losses * 1)  # Modify formula here
```

## 🔧 Useful Commands

```bash
# Build React app
cd frontend && npm run build && cd ..

# Or use script
bash build.sh

# Run API locally
uvicorn api:app --reload

# Run frontend in dev mode (with hot reload)
cd frontend && npm run dev

# Install new npm package
cd frontend && npm install package-name

# Install new Python package
pip install package-name
```

## 📈 Future Enhancements

Easy additions you could make:

1. **Charts/Graphs** - Add ELO timeline chart
   ```bash
   cd frontend && npm install recharts
   ```

2. **Search/Filter** - Filter rankings by name

3. **Dark Mode** - Toggle theme

4. **Authentication** - Protect recalculate endpoint

5. **Real-time Updates** - WebSocket for live stats

6. **Export** - Download rankings as CSV/PDF

## 🆘 Troubleshooting

### "React app not showing"
```bash
cd frontend && npm run build && cd ..
# Restart uvicorn
```

### "API calls failing"
- Check backend is running on port 8000
- Check browser console (F12) for errors
- Visit /docs to test endpoints

### "Can't install dependencies"
```bash
# Node issues
cd frontend && rm -rf node_modules package-lock.json
npm install

# Python issues
pip install --upgrade pip
pip install -r requirements.txt
```

## ✨ Success!

You now have a modern, production-ready web application that:
- Integrates with Google Sheets
- Calculates sophisticated ELO ratings
- Displays beautiful, sortable rankings
- Shows detailed player analytics
- Is ready to deploy to Railway

**Time invested: ~3-4 hours**
**Result: Professional-grade web app!**

---

**Next:** Follow `RAILWAY_DEPLOYMENT.md` to deploy to production!

