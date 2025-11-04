import { Info } from 'lucide-react';

export default function MatchesTable({ matches, onPlayerClick }) {
  const getRatingChange = (match) => {
    // Get the absolute value of rating change (winners gain, losers lose the same amount)
    const change = Math.abs(match['Team 1 ELO Change']);
    return change;
  };

  if (matches.length === 0) {
    return <div className="loading">No matches available yet. Click "Recalculate Stats" to load data.</div>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Team 1</th>
          <th>Score</th>
          <th>Team 2</th>
          <th>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              Rating +/-
              <span title="Rating points exchanged between teams - winners gain this amount, losers lose it" style={{ cursor: 'help', display: 'flex', alignItems: 'center' }}>
                <Info size={14} />
              </span>
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        {matches.map((match, idx) => {
          const team1Won = match.Winner === 'Team 1';
          const team2Won = match.Winner === 'Team 2';
          
          return (
            <tr key={idx}>
              <td>{match.Date}</td>
              <td className={team1Won ? 'winner-cell' : 'loser-cell'}>
                <span className="player-name" onClick={() => onPlayerClick(match['Team 1 Player 1'])}>
                  {match['Team 1 Player 1']}
                </span>
                {' + '}
                <span className="player-name" onClick={() => onPlayerClick(match['Team 1 Player 2'])}>
                  {match['Team 1 Player 2']}
                </span>
              </td>
              <td>{match['Team 1 Score']}-{match['Team 2 Score']}</td>
              <td className={team2Won ? 'winner-cell' : 'loser-cell'}>
                <span className="player-name" onClick={() => onPlayerClick(match['Team 2 Player 1'])}>
                  {match['Team 2 Player 1']}
                </span>
                {' + '}
                <span className="player-name" onClick={() => onPlayerClick(match['Team 2 Player 2'])}>
                  {match['Team 2 Player 2']}
                </span>
              </td>
              <td>{getRatingChange(match)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

