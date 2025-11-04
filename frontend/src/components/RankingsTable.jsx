import { useState } from 'react';

export default function RankingsTable({ rankings, onPlayerClick }) {
  const [sortConfig, setSortConfig] = useState({ column: 'Points', ascending: false });

  const handleSort = (column) => {
    setSortConfig(prev => ({
      column,
      ascending: prev.column === column ? !prev.ascending : false
    }));
  };

  const getSortArrow = (column) => {
    if (sortConfig.column === column) {
      return sortConfig.ascending ? ' ↑' : ' ↓';
    }
    return '';
  };

  const sortedRankings = [...rankings].sort((a, b) => {
    // Primary sort by selected column
    const aVal = a[sortConfig.column];
    const bVal = b[sortConfig.column];
    
    const primaryComparison = aVal > bVal ? 1 : -1;
    const primaryResult = sortConfig.ascending ? primaryComparison : -primaryComparison;
    
    if (aVal !== bVal) return primaryResult;
    
    // Tiebreakers: Points → Avg Pt Diff → Win Rate → ELO
    if (a.Points !== b.Points) return b.Points - a.Points;
    if (a['Avg Pt Diff'] !== b['Avg Pt Diff']) return b['Avg Pt Diff'] - a['Avg Pt Diff'];
    if (a['Win Rate'] !== b['Win Rate']) return b['Win Rate'] - a['Win Rate'];
    return b.ELO - a.ELO;
  });

  const formatPtDiff = (value) => {
    return value >= 0 ? `+${value}` : `${value}`;
  };

  if (rankings.length === 0) {
    return <div className="loading">No rankings available yet. Click "Recalculate Stats" to load data.</div>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th onClick={() => handleSort('Name')}>Name{getSortArrow('Name')}</th>
          <th onClick={() => handleSort('Points')}>Points{getSortArrow('Points')}</th>
          <th onClick={() => handleSort('Games')}>Games{getSortArrow('Games')}</th>
          <th onClick={() => handleSort('Win Rate')}>Win Rate{getSortArrow('Win Rate')}</th>
          <th onClick={() => handleSort('Wins')}>Wins{getSortArrow('Wins')}</th>
          <th onClick={() => handleSort('Losses')}>Losses{getSortArrow('Losses')}</th>
          <th onClick={() => handleSort('Avg Pt Diff')}>Avg Pt Diff{getSortArrow('Avg Pt Diff')}</th>
          <th onClick={() => handleSort('ELO')}>Rating{getSortArrow('ELO')}</th>
        </tr>
      </thead>
      <tbody>
        {sortedRankings.map((player, idx) => (
          <tr key={idx}>
            <td>
              <span className="player-name" onClick={() => onPlayerClick(player.Name)}>
                {player.Name}
              </span>
            </td>
            <td>{player.Points}</td>
            <td>{player.Games}</td>
            <td>{(player['Win Rate'] * 100).toFixed(1)}%</td>
            <td>{player.Wins}</td>
            <td>{player.Losses}</td>
            <td>{formatPtDiff(player['Avg Pt Diff'])}</td>
            <td>{player.ELO}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

