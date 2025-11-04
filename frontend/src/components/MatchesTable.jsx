export default function MatchesTable({ matches, onPlayerClick }) {
  const formatRatingChange = (value) => {
    return value >= 0 ? `+${value}` : `${value}`;
  };

  if (matches.length === 0) {
    return <div className="loading">No matches available yet. Click "Recalculate Stats" to load data.</div>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Team 1 P1</th>
          <th>Team 1 P2</th>
          <th>Team 2 P1</th>
          <th>Team 2 P2</th>
          <th>Score</th>
          <th>Winner</th>
          <th>T1 Rating +/-</th>
          <th>T2 Rating +/-</th>
        </tr>
      </thead>
      <tbody>
        {matches.map((match, idx) => (
          <tr key={idx}>
            <td>{match.Date}</td>
            <td>
              <span className="player-name" onClick={() => onPlayerClick(match['Team 1 Player 1'])}>
                {match['Team 1 Player 1']}
              </span>
            </td>
            <td>
              <span className="player-name" onClick={() => onPlayerClick(match['Team 1 Player 2'])}>
                {match['Team 1 Player 2']}
              </span>
            </td>
            <td>
              <span className="player-name" onClick={() => onPlayerClick(match['Team 2 Player 1'])}>
                {match['Team 2 Player 1']}
              </span>
            </td>
            <td>
              <span className="player-name" onClick={() => onPlayerClick(match['Team 2 Player 2'])}>
                {match['Team 2 Player 2']}
              </span>
            </td>
            <td>{match['Team 1 Score']}-{match['Team 2 Score']}</td>
            <td>{match.Winner}</td>
            <td>{formatRatingChange(match['Team 1 ELO Change'])}</td>
            <td>{formatRatingChange(match['Team 2 ELO Change'])}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

