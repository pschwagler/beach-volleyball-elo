import { X } from 'lucide-react';
import { Button } from './UI';
import PlayerSelector from './PlayerSelector';
import PlayerOverview from './PlayerOverview';
import MatchHistoryTable from './MatchHistoryTable';
import PlayerStatsTable from './PlayerStatsTable';

export default function PlayerDetails({ playerName, stats, matchHistory, onClose, allPlayers, onPlayerChange }) {
  if (!stats || !stats.stats || stats.stats.length === 0) {
    return null;
  }

  const overview = stats.overview || {};
  const playerStats = stats.stats || [];

  return (
    <div className="player-details">
      <Button variant="close" onClick={onClose}>
        <X size={16} />
        Close
      </Button>
      
      <PlayerSelector 
        playerName={playerName}
        allPlayers={allPlayers}
        onPlayerChange={onPlayerChange}
      />

      <PlayerOverview overview={overview} />
      
      <MatchHistoryTable 
        matchHistory={matchHistory}
        onPlayerChange={onPlayerChange}
      />

      <PlayerStatsTable 
        playerStats={playerStats}
        onPlayerChange={onPlayerChange}
      />
    </div>
  );
}

