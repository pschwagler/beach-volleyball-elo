import { useState } from 'react';
import './App.css';
import HeroHeader from './components/HeroHeader';
import ControlPanel from './components/ControlPanel';
import RankingsTable from './components/RankingsTable';
import MatchesTable from './components/MatchesTable';
import PlayerDetailsPanel from './components/PlayerDetailsPanel';
import { Alert, Tabs } from './components/UI';
import { useData } from './contexts/DataContext';
import { usePlayerDetails } from './hooks/usePlayerDetails';

function App() {
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
  const [activeTab, setActiveTab] = useState('matches');

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

  return (
    <>
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
