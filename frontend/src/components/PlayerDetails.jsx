import { useState, useEffect } from 'react';
import { X, User, History, BarChart3, ChevronDown, Trophy, Target, TrendingUp } from 'lucide-react';
import { Button } from './UI';

export default function PlayerDetails({ playerName, stats, matchHistory, onClose, isOpen, allPlayers, onPlayerChange }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Reset search when player changes
  useEffect(() => {
    setSearchTerm('');
    setIsDropdownOpen(false);
  }, [playerName]);

  if (!stats || !stats.stats || stats.stats.length === 0) {
    return null;
  }

  const overview = stats.overview || {};
  const playerStats = stats.stats || [];

  const filteredPlayers = allPlayers
    ? allPlayers
        .filter(player => player.toLowerCase().includes(searchTerm.toLowerCase()))
        .sort((a, b) => a.localeCompare(b))
    : [];


  const handlePlayerSelect = (player) => {
    if (onPlayerChange) {
      onPlayerChange(player);
    }
    setSearchTerm('');
    setIsDropdownOpen(false);
  };

  const formatPtDiff = (value) => {
    if (value === '' || value === null || value === undefined) return '';
    return value >= 0 ? `+${value}` : `${value}`;
  };

  const formatRatingChange = (value) => {
    if (value === '' || value === null || value === undefined) return '';
    return value >= 0 ? `+${value}` : `${value}`;
  };

  const formatNewRating = (eloAfter, eloChange) => {
    if (eloAfter === '' || eloAfter === null || eloAfter === undefined) return null;
    if (eloChange === '' || eloChange === null || eloChange === undefined) {
      return <span>{Math.round(eloAfter)}</span>;
    }
    const changeStr = eloChange >= 0 ? `+${Math.round(eloChange)}` : `${Math.round(eloChange)}`;
    const className = eloChange >= 0 ? 'rating-positive' : 'rating-negative';
    return (
      <span>
        {Math.round(eloAfter)} <span className={className}>({changeStr})</span>
      </span>
    );
  };

  const formatWinRate = (value) => {
    if (value === '' || value === null || value === undefined) return '';
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className={`player-details ${isOpen ? 'open' : ''}`}>
      <Button variant="close" onClick={onClose}>
        <X size={16} />
        Close
      </Button>
      
      {/* Player Selector */}
      <div className="player-selector-container">
        <User size={28} />
        <div className="player-selector-wrapper">
          <div className="player-selector-current" onClick={() => setIsDropdownOpen(!isDropdownOpen)}>
            <span className="player-selector-name">{playerName}</span>
            <ChevronDown size={20} className={isDropdownOpen ? 'rotate-180' : ''} />
          </div>
          
          {isDropdownOpen && (
            <div className="player-selector-dropdown">
              <input
                type="text"
                className="player-selector-search"
                placeholder="Search players..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                autoFocus
              />
              <div className="player-selector-options">
                {!allPlayers ? (
                  <div className="player-selector-option disabled">Loading players...</div>
                ) : filteredPlayers.length > 0 ? (
                  filteredPlayers.map((player) => (
                    <div
                      key={player}
                      className={`player-selector-option ${player === playerName ? 'selected' : ''}`}
                      onClick={() => handlePlayerSelect(player)}
                    >
                      {player}
                    </div>
                  ))
                ) : (
                  <div className="player-selector-option disabled">
                    {searchTerm ? 'No players found' : 'No players available'}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Player Overview */}
      {overview.ranking && (
        <div className="player-overview">
          <div className="overview-stat">
            <Trophy size={24} className="overview-icon" />
            <div className="overview-content">
              <div className="overview-label">Ranking</div>
              <div className="overview-value">#{overview.ranking}</div>
            </div>
          </div>
          <div className="overview-stat">
            <Target size={24} className="overview-icon" />
            <div className="overview-content">
              <div className="overview-label">Points</div>
              <div className="overview-value">{overview.points}</div>
            </div>
          </div>
          <div className="overview-stat">
            <TrendingUp size={24} className="overview-icon" />
            <div className="overview-content">
              <div className="overview-label">Rating</div>
              <div className="overview-value">{overview.rating}</div>
            </div>
          </div>
        </div>
      )}
      
      {/* Match History Section */}
      {matchHistory && matchHistory.length > 0 && (
        <>
          <h3><History size={22} />Match History</h3>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Partner</th>
                <th>Opponents</th>
                <th>Result</th>
                <th>Score</th>
                <th>New Rating</th>
              </tr>
            </thead>
            <tbody>
              {matchHistory.map((match, idx) => {
                const ratingDisplay = formatNewRating(match['ELO After'], match['ELO Change']);
                return (
                  <tr key={idx}>
                    <td>{match.Date}</td>
                    <td>
                      <span className="player-name" onClick={() => onPlayerChange(match.Partner)}>
                        {match.Partner}
                      </span>
                    </td>
                    <td>
                      <span className="player-name" onClick={() => onPlayerChange(match['Opponent 1'])}>
                        {match['Opponent 1']}
                      </span>
                      {' / '}
                      <span className="player-name" onClick={() => onPlayerChange(match['Opponent 2'])}>
                        {match['Opponent 2']}
                      </span>
                    </td>
                    <td>
                      <strong className={match.Result === 'W' ? 'result-win' : 'result-loss'}>
                        {match.Result}
                      </strong>
                    </td>
                    <td>{match.Score}</td>
                    <td>
                      {ratingDisplay}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </>
      )}

      <h3><BarChart3 size={22} />Player Stats</h3>
      <table>
        <thead>
          <tr>
            <th>Partner/Opponent</th>
            <th>Wins</th>
            <th>Losses</th>
            <th>Win Rate</th>
            <th>Points</th>
            <th>Games</th>
            <th>Avg Pt Diff</th>
          </tr>
        </thead>
        <tbody>
          {playerStats.map((row, idx) => {
            const isSectionHeader = 
              row['Partner/Opponent'] === 'WITH PARTNERS' || 
              row['Partner/Opponent'] === 'VS OPPONENTS';
            const isEmpty = row['Partner/Opponent'] === '';
            const isOverall = row['Partner/Opponent'] === 'OVERALL';

            if (isEmpty) {
              return <tr key={idx}><td colSpan="7" className="spacer-row"></td></tr>;
            } else if (isSectionHeader) {
              return (
                <tr key={idx} className="section-header">
                  <td colSpan="7">{row['Partner/Opponent']}</td>
                </tr>
              );
            } else {
              return (
                <tr key={idx} className={isOverall ? 'section-header' : ''}>
                  <td>
                    {isOverall ? (
                      <strong>{row['Partner/Opponent']}</strong>
                    ) : (
                      <strong>
                        <span className="player-name" onClick={() => onPlayerChange(row['Partner/Opponent'])}>
                          {row['Partner/Opponent']}
                        </span>
                      </strong>
                    )}
                  </td>
                  <td>{row['Wins']}</td>
                  <td>{row['Losses']}</td>
                  <td>{formatWinRate(row['Win Rate'])}</td>
                  <td>{row['Points']}</td>
                  <td>{row['Games']}</td>
                  <td>{formatPtDiff(row['Avg Pt Diff'])}</td>
                </tr>
              );
            }
          })}
        </tbody>
      </table>
    </div>
  );
}

