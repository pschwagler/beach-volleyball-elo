import { X, User, History } from 'lucide-react';

export default function PlayerDetails({ playerName, stats, matchHistory, onClose }) {
  if (!stats || stats.length === 0) {
    return null;
  }

  const formatPtDiff = (value) => {
    if (value === '' || value === null || value === undefined) return '';
    return value >= 0 ? `+${value}` : `${value}`;
  };

  const formatRatingChange = (value) => {
    if (value === '' || value === null || value === undefined) return '';
    return value >= 0 ? `+${value}` : `${value}`;
  };

  const formatWinRate = (value) => {
    if (value === '' || value === null || value === undefined) return '';
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="player-details">
      <button className="close-btn" onClick={onClose}>
        <X size={16} />
        Close
      </button>
      <h2><User size={28} />{playerName}</h2>
      
      <table>
        <thead>
          <tr>
            <th>Partner/Opponent</th>
            <th>Points</th>
            <th>Games</th>
            <th>Win Rate</th>
            <th>Wins</th>
            <th>Losses</th>
            <th>Avg Pt Diff</th>
          </tr>
        </thead>
        <tbody>
          {stats.map((row, idx) => {
            const isSectionHeader = 
              row['Partner/Opponent'] === 'WITH PARTNERS' || 
              row['Partner/Opponent'] === 'VS OPPONENTS';
            const isEmpty = row['Partner/Opponent'] === '';
            const isOverall = row['Partner/Opponent'] === 'OVERALL';

            if (isEmpty) {
              return <tr key={idx}><td colSpan="7" style={{ height: '10px' }}></td></tr>;
            } else if (isSectionHeader) {
              return (
                <tr key={idx} className="section-header">
                  <td colSpan="7">{row['Partner/Opponent']}</td>
                </tr>
              );
            } else {
              return (
                <tr key={idx} className={isOverall ? 'section-header' : ''}>
                  <td><strong>{row['Partner/Opponent']}</strong></td>
                  <td>{row['Points']}</td>
                  <td>{row['Games']}</td>
                  <td>{formatWinRate(row['Win Rate'])}</td>
                  <td>{row['Wins']}</td>
                  <td>{row['Losses']}</td>
                  <td>{formatPtDiff(row['Avg Pt Diff'])}</td>
                </tr>
              );
            }
          })}
        </tbody>
      </table>

      {/* Match History Section */}
      {matchHistory && matchHistory.length > 0 && (
        <>
          <h3><History size={22} />Match History</h3>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Partner</th>
                <th>Opponent 1</th>
                <th>Opponent 2</th>
                <th>Result</th>
                <th>Score</th>
                <th>Rating Change</th>
              </tr>
            </thead>
            <tbody>
              {matchHistory.map((match, idx) => (
                <tr key={idx} style={{ 
                  background: match.Result === 'W' ? '#e8f5e9' : 
                             match.Result === 'L' ? '#ffebee' : 'transparent'
                }}>
                  <td>{match.Date}</td>
                  <td>{match.Partner}</td>
                  <td>{match['Opponent 1']}</td>
                  <td>{match['Opponent 2']}</td>
                  <td><strong>{match.Result}</strong></td>
                  <td>{match.Score}</td>
                  <td>{formatRatingChange(match['ELO Change'])}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}

