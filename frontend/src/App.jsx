import { useState } from 'react';
import './App.css';
import NavBar from './components/layout/NavBar';
import HeroHeader from './components/layout/HeroHeader';
import ControlPanel from './components/control/ControlPanel';
import RankingsTable from './components/rankings/RankingsTable';
import MatchesTable from './components/match/MatchesTable';
import PlayerDetailsPanel from './components/player/PlayerDetailsPanel';
import { Alert, Tabs } from './components/ui/UI';
import { useData } from './contexts/DataContext';
import { usePlayerDetails } from './hooks/usePlayerDetails';

function App() {
  // Simple login state - can be replaced with proper auth context later
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const { 
    rankings, 
    matches, 
    activeSession,
    loading, 
    message, 
    setMessage, 
    handleLoadFromSheets,
    handleCreateSession,
    handleEndSession,
    handleDeleteSession,
    handleCreateMatch,
    handleUpdateMatch,
    handleDeleteMatch,
    handleCreatePlayer,
    allPlayerNames 
  } = useData();
  const [activeTab, setActiveTab] = useState('rankings');

  // Check if URL contains ?skyball query parameter
  const urlParams = new URLSearchParams(window.location.search);
  const showControls = urlParams.has('skyball');

  // Player details management
  const {
    selectedPlayer,
    playerStats,
    playerMatchHistory,
    isPanelOpen,
    handlePlayerClick,
    handleSideTabClick,
    handleClosePlayer
  } = usePlayerDetails(rankings, allPlayerNames, setMessage, matches);

  const handleSignOut = () => {
    setIsLoggedIn(false);
    // Add any additional sign out logic here
  };

  // Mock user leagues - replace with actual data later
  const userLeagues = isLoggedIn ? [
    { id: 1, name: 'Summer League 2024' },
    { id: 2, name: 'Weekend Warriors' },
  ] : [];

  return (
    <>
      <NavBar isLoggedIn={isLoggedIn} onSignOut={handleSignOut} userLeagues={userLeagues} />
      <div className="container">
        <HeroHeader />
        {showControls && <ControlPanel onLoadFromSheets={handleLoadFromSheets} />}
        <Alert type={message?.type}>
          {message?.text}
        </Alert>
        <Tabs activeTab={activeTab} onTabChange={setActiveTab} />
        <div className="content-area">
          {activeTab === 'matches' && (
            <MatchesTable 
              matches={matches} 
              onPlayerClick={handlePlayerClick}
              loading={loading}
              activeSession={activeSession}
              onCreateSession={handleCreateSession}
              onEndSession={handleEndSession}
              onDeleteSession={handleDeleteSession}
              onCreateMatch={handleCreateMatch}
              onUpdateMatch={handleUpdateMatch}
              onDeleteMatch={handleDeleteMatch}
              onCreatePlayer={handleCreatePlayer}
              allPlayerNames={allPlayerNames}
            />
          )}
          {activeTab === 'rankings' && (
            <RankingsTable 
              rankings={rankings} 
              onPlayerClick={handlePlayerClick}
              loading={loading}
            />
          )}
        </div>
      </div>
      <PlayerDetailsPanel
        selectedPlayer={selectedPlayer}
        playerStats={playerStats}
        playerMatchHistory={playerMatchHistory}
        isPanelOpen={isPanelOpen}
        allPlayerNames={allPlayerNames}
        onPlayerChange={handlePlayerClick}
        onClose={handleClosePlayer}
        onSideTabClick={handleSideTabClick}
      />
    </>
  );
}

export default App;
