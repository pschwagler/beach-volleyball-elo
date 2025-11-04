import { createContext, useContext, useState, useEffect } from 'react';
import { getRankings, getMatches, calculateStats } from '../services/api';

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
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  // Load both rankings and matches on mount
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    try {
      setLoading(true);
      const [rankingsData, matchesData] = await Promise.all([
        getRankings().catch(() => []),
        getMatches().catch(() => [])
      ]);
      
      setRankings(rankingsData);
      setMatches(matchesData);
      
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

  // Extract all unique player names from rankings and matches
  const allPlayerNames = (() => {
    const playerSet = new Set();
    
    // Add from rankings
    rankings.forEach(player => {
      if (player.Name) playerSet.add(player.Name);
    });
    
    // Add from matches
    matches.forEach(match => {
      if (match.Team1Player1) playerSet.add(match.Team1Player1);
      if (match.Team1Player2) playerSet.add(match.Team1Player2);
      if (match.Team2Player1) playerSet.add(match.Team2Player1);
      if (match.Team2Player2) playerSet.add(match.Team2Player2);
    });
    
    return Array.from(playerSet).sort((a, b) => a.localeCompare(b));
  })();

  const value = {
    rankings,
    matches,
    loading,
    message,
    setMessage,
    loadRankings,
    loadMatches,
    loadAllData,
    handleRecalculate,
    allPlayerNames
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

