import { useState, useEffect } from 'react';
import './App.css';
import ControlPanel from './components/ControlPanel';
import RankingsTable from './components/RankingsTable';
import MatchesTable from './components/MatchesTable';
import PlayerDetails from './components/PlayerDetails';
import PlayerDetailsSideTab from './components/PlayerDetailsSideTab';
import { Alert, Tabs } from './components/UI';
import { getPlayerStats, getPlayerMatchHistory } from './services/api';
import { useData } from './contexts/DataContext';

function App() {
  // Get global data from context
  const { rankings, matches, loading, message, setMessage, handleRecalculate, allPlayerNames } = useData();
  
  const [activeTab, setActiveTab] = useState('matches'); // 'matches' or 'rankings'
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerStats, setPlayerStats] = useState(null);
  const [playerMatchHistory, setPlayerMatchHistory] = useState(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [lastViewedPlayer, setLastViewedPlayer] = useState(null);

  // Check if URL contains ?skyball query parameter
  const urlParams = new URLSearchParams(window.location.search);
  const showControls = urlParams.has('skyball');

  const handlePlayerClick = async (playerName, shouldOpenPanel = true) => {
    try {
      setSelectedPlayer(playerName);
      setLastViewedPlayer(playerName);
      setPlayerStats(null); // Clear previous data
      setPlayerMatchHistory(null);
      
      // Load both stats and match history
      const [stats, matchHistory] = await Promise.all([
        getPlayerStats(playerName),
        getPlayerMatchHistory(playerName)
      ]);
      
      setPlayerStats(stats);
      setPlayerMatchHistory(matchHistory);
      
      // Open the panel after data is loaded
      if (shouldOpenPanel) {
        // Small delay to ensure the element is rendered before animating
        setTimeout(() => setIsPanelOpen(true), 10);
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Error loading player details: ${error.message}`
      });
    }
  };

  const handleSideTabClick = () => {
    // If player data is already loaded, just open the panel
    if (selectedPlayer && playerStats) {
      console.log('selectedPlayer', selectedPlayer);
      setIsPanelOpen(true);
    } else if (lastViewedPlayer) {
      // Load the last viewed player
      console.log('lastViewedPlayer', lastViewedPlayer);
      handlePlayerClick(lastViewedPlayer);
    } else {
      // Find the first place player by points with tie-breakers
      const firstPlacePlayer = rankings.length > 0 ? [...rankings].sort((a, b) => {
        if (a.Points !== b.Points) return b.Points - a.Points;
        if (a['Avg Pt Diff'] !== b['Avg Pt Diff']) return b['Avg Pt Diff'] - a['Avg Pt Diff'];
        if (a['Win Rate'] !== b['Win Rate']) return b['Win Rate'] - a['Win Rate'];
        return b.ELO - a.ELO;
      })[0] : null;
      console.log('firstPlacePlayer', firstPlacePlayer, rankings);
      if (firstPlacePlayer) {
        handlePlayerClick(firstPlacePlayer.Name);
      } else if (allPlayerNames.length > 0) {
        handlePlayerClick(allPlayerNames[0]);
      }
    }
  };

  const handleClosePlayer = () => {
    setIsPanelOpen(false);
    // Keep player data in state - don't clear it
  };

  // Auto-load #1 ranked player when rankings data loads
  useEffect(() => {
    if (rankings.length > 0 && !selectedPlayer) {
      // Find the first place player by points with tie-breakers
      const firstPlacePlayer = [...rankings].sort((a, b) => {
        if (a.Points !== b.Points) return b.Points - a.Points;
        if (a['Avg Pt Diff'] !== b['Avg Pt Diff']) return b['Avg Pt Diff'] - a['Avg Pt Diff'];
        if (a['Win Rate'] !== b['Win Rate']) return b['Win Rate'] - a['Win Rate'];
        return b.ELO - a.ELO;
      })[0];
      
      if (firstPlacePlayer) {
        // Load player data but don't open the panel
        handlePlayerClick(firstPlacePlayer.Name, false);
      }
    }
  }, [rankings]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
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
    <>
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
      </div>

      {selectedPlayer && playerStats && (
        <>
          <div 
            className={`player-details-backdrop ${isPanelOpen ? 'open' : ''}`}
            onClick={handleClosePlayer}
          />
          <PlayerDetails
            playerName={selectedPlayer}
            stats={playerStats}
            matchHistory={playerMatchHistory}
            onClose={handleClosePlayer}
            isOpen={isPanelOpen}
            allPlayers={allPlayerNames}
            onPlayerChange={handlePlayerClick}
          />
        </>
      )}

      {/* Side Tab - visible when panel is closed */}
      <PlayerDetailsSideTab
        onClick={handleSideTabClick}
        isVisible={!isPanelOpen}
      />
    </>
  );
}

export default App;
