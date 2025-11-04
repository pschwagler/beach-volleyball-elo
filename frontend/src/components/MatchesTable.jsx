import { MatchCard } from './UI';

export default function MatchesTable({ matches, onPlayerClick }) {

  if (matches.length === 0) {
    return <div className="loading">No matches available yet. Click "Recalculate Stats" to load data.</div>;
  }

  // Group matches by date
  const matchesByDate = matches.reduce((acc, match) => {
    const date = match.Date;
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(match);
    return acc;
  }, {});

  return (
    <div className="matches-container">
      {Object.entries(matchesByDate).map(([date, dateMatches]) => (
        <div key={date} className="match-date-group">
          <h3 className="match-date-header">{date}</h3>
          <div className="match-cards">
            {dateMatches.map((match, idx) => (
              <MatchCard 
                key={idx} 
                match={match} 
                onPlayerClick={onPlayerClick} 
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

