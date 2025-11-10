import { createContext, useContext, useState, useEffect } from 'react';
import { getRankings, getMatches, calculateStats, getSessions, getActiveSession, createSession, lockInSession, createMatch, updateMatch, getPlayers, createPlayer } from '../services/api';

const DataContext = createContext();

export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

export const DataProvider = ({ children }) => {
  const [rankings, setRankings] = useState([]);
  const [matches, setMatches] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [allPlayerNames, setAllPlayerNames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  // Load both rankings and matches on mount
  useEffect(() => {
    loadAllData();
  }, []);

  const loadPlayers = async () => {
    try {
      const playersData = await getPlayers().catch(() => []);
      const playerNames = playersData.map(p => p.name).sort((a, b) => a.localeCompare(b));
      setAllPlayerNames(playerNames);
    } catch (error) {
      console.error('Error loading players:', error);
    }
  };

  const loadAllData = async () => {
    try {
      setLoading(true);
      const [rankingsData, matchesData, sessionsData, activeSessionData, playersData] = await Promise.all([
        getRankings().catch(() => []),
        getMatches().catch(() => []),
        getSessions().catch(() => []),
        getActiveSession().catch(() => null),
        getPlayers().catch(() => [])
      ]);
      
      setRankings(rankingsData);
      setMatches(matchesData);
      setSessions(sessionsData);
      setActiveSession(activeSessionData);
      
      // Set player names from database
      const playerNames = playersData.map(p => p.name).sort((a, b) => a.localeCompare(b));
      setAllPlayerNames(playerNames);
      
      if (rankingsData.length === 0 && matchesData.length === 0) {
        setMessage({
          type: 'error',
          text: 'No data found. Click "Recalculate Stats" to load data from Google Sheets.'
        });
      } else {
        setMessage(null);
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Error loading data: ${error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

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
        loadAllData();
      }, 1500);
    } catch (error) {
      setMessage({
        type: 'error',
        text: `❌ Error: ${error.response?.data?.detail || error.message}`
      });
    }
  };

  const handleCreatePlayer = async (name) => {
    try {
      await createPlayer(name);
      // Reload player names to include the new player
      await loadPlayers();
    } catch (error) {
      console.error('Error creating player:', error);
      throw error;
    }
  };

  const handleCreateSession = async () => {
    try {
      const result = await createSession();
      
      // Reload sessions and set as active
      const sessionsData = await getSessions();
      setSessions(sessionsData);
      setActiveSession(result.session);
      
      return result.session;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      
      // Check if it's a duplicate session error (400 status)
      if (error.response?.status === 400) {
        setMessage({
          type: 'error',
          text: `❌ ${errorMessage}`
        });
      } else {
        setMessage({
          type: 'error',
          text: `❌ Error creating session: ${errorMessage}`
        });
      }
      throw error;
    }
  };

  const handleEndSession = async (sessionId) => {
    try {
      await lockInSession(sessionId);
      setMessage({
        type: 'success',
        text: '✓ Scores submitted and stats recalculated!'
      });
      
      // Reload all data to reflect the recalculated stats
      const sessionsData = await getSessions();
      setSessions(sessionsData);
      setActiveSession(null);
      await loadAllData();
    } catch (error) {
      setMessage({
        type: 'error',
        text: `❌ Error submitting scores: ${error.response?.data?.detail || error.message}`
      });
      throw error;
    }
  };

  const handleCreateMatch = async (matchData) => {
    try {
      const result = await createMatch(matchData);
      setMessage({
        type: 'success',
        text: '✓ Match added successfully!'
      });
      
      // Reload matches and players to show the new match and any new players
      await Promise.all([loadMatches(), loadPlayers()]);
      
      return result;
    } catch (error) {
      setMessage({
        type: 'error',
        text: `❌ Error creating match: ${error.response?.data?.detail || error.message}`
      });
      throw error;
    }
  };

  const handleUpdateMatch = async (matchId, matchData) => {
    try {
      const result = await updateMatch(matchId, matchData);
      setMessage({
        type: 'success',
        text: '✓ Match updated successfully!'
      });
      
      // Reload matches and players to show the updated match and any new players
      await Promise.all([loadMatches(), loadPlayers()]);
      
      return result;
    } catch (error) {
      setMessage({
        type: 'error',
        text: `❌ Error updating match: ${error.response?.data?.detail || error.message}`
      });
      throw error;
    }
  };

  const value = {
    rankings,
    matches,
    sessions,
    activeSession,
    loading,
    message,
    setMessage,
    loadRankings,
    loadMatches,
    loadPlayers,
    loadAllData,
    handleRecalculate,
    handleCreateSession,
    handleEndSession,
    handleCreateMatch,
    handleUpdateMatch,
    handleCreatePlayer,
    allPlayerNames
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

