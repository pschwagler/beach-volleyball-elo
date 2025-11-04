import { useState, useEffect } from 'react';
import './App.css';
import ControlPanel from './components/ControlPanel';
import RankingsTable from './components/RankingsTable';
import MatchesTable from './components/MatchesTable';
import PlayerDetails from './components/PlayerDetails';
import { Alert, Tabs } from './components/UI';
import { calculateStats, getRankings, getPlayerStats, getMatches, getPlayerMatchHistory } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('matches'); // 'matches' or 'rankings'
  const [rankings, setRankings] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerStats, setPlayerStats] = useState(null);
  const [playerMatchHistory, setPlayerMatchHistory] = useState(null);

  // Check if URL contains ?skyball query parameter
  const urlParams = new URLSearchParams(window.location.search);
  const showControls = urlParams.has('skyball');

  // Load matches on mount (since it's the default tab)
  useEffect(() => {
    loadMatches();
  }, []);

  const loadRankings = async () => {
    try {
      setLoading(true);
      const data = await getRankings();
      setRankings(data);
      setMessage(null);
    } catch (error) {
      if (error.response?.status === 404) {
        setMessage({
          type: 'error',
          text: 'Rankings not found. Click "Recalculate Stats" to load data from Google Sheets.'
        });
        setRankings([]);
      } else {
        setMessage({
          type: 'error',
          text: `Error loading rankings: ${error.message}`
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const loadMatches = async () => {
    try {
      setLoading(true);
      const data = await getMatches();
      setMatches(data);
      setMessage(null);
    } catch (error) {
      if (error.response?.status === 404) {
        setMessage({
          type: 'error',
          text: 'Matches not found. Click "Recalculate Stats" to load data from Google Sheets.'
        });
        setMatches([]);
      } else {
        setMessage({
          type: 'error',
          text: `Error loading matches: ${error.message}`
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    try {
      setMessage({ type: 'loading', text: 'Recalculating statistics from Google Sheets...' });
      const result = await calculateStats();
      setMessage({
        type: 'success',
        text: `✓ Success! Calculated stats for ${result.player_count} players from ${result.match_count} matches.`
      });
      
      // Auto-refresh data after calculation
      setTimeout(() => {
        loadRankings();
        loadMatches();
        setMessage(null);
      }, 1500);
    } catch (error) {
      setMessage({
        type: 'error',
        text: `❌ Error: ${error.response?.data?.detail || error.message}`
      });
    }
  };

  const handlePlayerClick = async (playerName) => {
    try {
      setSelectedPlayer(playerName);
      setPlayerStats(null); // Clear previous data
      setPlayerMatchHistory(null);
      
      // Load both stats and match history
      const [stats, matchHistory] = await Promise.all([
        getPlayerStats(playerName),
        getPlayerMatchHistory(playerName)
      ]);
      
      setPlayerStats(stats);
      setPlayerMatchHistory(matchHistory);
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Error loading player details: ${error.message}`
      });
    }
  };

  const handleClosePlayer = () => {
    setSelectedPlayer(null);
    setPlayerStats(null);
    setPlayerMatchHistory(null);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'rankings' && rankings.length === 0) {
      loadRankings();
    }
  };

  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const images = [
    '/beach-kings.png',
    '/side-out-movie-cover.png',
    '/top-gun-vball.png'
  ];

  // Rotate background image every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % images.length);
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <div className="hero-header" style={{ backgroundImage: `url(${images[currentImageIndex]})` }}>
        <div className="hero-overlay">
          <h1>QBK Beach Volleyball Standings</h1>
        </div>
      </div>

      {showControls && <ControlPanel onRecalculate={handleRecalculate} />}

      <Alert type={message?.type}>
        {message?.text}
      </Alert>

      <Tabs activeTab={activeTab} onTabChange={handleTabChange} />

      {/* Content Area */}
      <div className="content-area">
        {activeTab === 'matches' && (
          <div>
            {loading ? (
              <div className="loading">Loading matches...</div>
            ) : (
              <MatchesTable matches={matches} onPlayerClick={handlePlayerClick} />
            )}
          </div>
        )}

        {activeTab === 'rankings' && (
          <div>
            {loading ? (
              <div className="loading">Loading rankings...</div>
            ) : (
              <RankingsTable rankings={rankings} onPlayerClick={handlePlayerClick} />
            )}
          </div>
        )}
      </div>

      {selectedPlayer && playerStats && (
        <PlayerDetails
          playerName={selectedPlayer}
          stats={playerStats}
          matchHistory={playerMatchHistory}
          onClose={handleClosePlayer}
        />
      )}
    </div>
  );
}

export default App;
