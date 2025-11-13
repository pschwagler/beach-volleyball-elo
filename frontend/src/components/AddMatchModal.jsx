import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from './UI';
import PlayerDropdown from './PlayerDropdown';

export default function AddMatchModal({ isOpen, onClose, onSubmit, allPlayerNames, onCreatePlayer, editMatch = null }) {
  const [team1Player1, setTeam1Player1] = useState('');
  const [team1Player2, setTeam1Player2] = useState('');
  const [team2Player1, setTeam2Player1] = useState('');
  const [team2Player2, setTeam2Player2] = useState('');
  const [team1Score, setTeam1Score] = useState('');
  const [team2Score, setTeam2Score] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle player selection with duplicate prevention
  const handlePlayerChange = (setter, newPlayer) => {
    // If a player is selected, remove them from other positions
    if (newPlayer) {
      if (team1Player1 === newPlayer && setter !== setTeam1Player1) setTeam1Player1('');
      if (team1Player2 === newPlayer && setter !== setTeam1Player2) setTeam1Player2('');
      if (team2Player1 === newPlayer && setter !== setTeam2Player1) setTeam2Player1('');
      if (team2Player2 === newPlayer && setter !== setTeam2Player2) setTeam2Player2('');
    }
    setter(newPlayer);
  };

  // Pre-populate fields when editing
  useEffect(() => {
    if (editMatch) {
      setTeam1Player1(editMatch['Team 1 Player 1'] || '');
      setTeam1Player2(editMatch['Team 1 Player 2'] || '');
      setTeam2Player1(editMatch['Team 2 Player 1'] || '');
      setTeam2Player2(editMatch['Team 2 Player 2'] || '');
      setTeam1Score(editMatch['Team 1 Score']?.toString() || '');
      setTeam2Score(editMatch['Team 2 Score']?.toString() || '');
    } else {
      // Reset when not editing
      setTeam1Player1('');
      setTeam1Player2('');
      setTeam2Player1('');
      setTeam2Player2('');
      setTeam1Score('');
      setTeam2Score('');
    }
  }, [editMatch, isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate all fields are filled
    if (!team1Player1 || !team1Player2 || !team2Player1 || !team2Player2 || !team1Score || !team2Score) {
      alert('Please fill in all fields');
      return;
    }

    // Validate scores are numbers
    const score1 = parseInt(team1Score);
    const score2 = parseInt(team2Score);
    if (isNaN(score1) || isNaN(score2) || score1 < 0 || score2 < 0) {
      alert('Please enter valid scores');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        team1_player1: team1Player1,
        team1_player2: team1Player2,
        team2_player1: team2Player1,
        team2_player2: team2Player2,
        team1_score: score1,
        team2_score: score2
      }, editMatch ? editMatch['Match ID'] : null);

      // Reset form only if not editing (edit mode will close and reset via useEffect)
      if (!editMatch) {
        setTeam1Player1('');
        setTeam1Player2('');
        setTeam2Player1('');
        setTeam2Player2('');
        setTeam1Score('');
        setTeam2Score('');
      }
      
      onClose();
    } catch (error) {
      console.error('Error submitting match:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  // Get list of selected players for each dropdown to exclude
  const getExcludedPlayers = (currentPlayer) => {
    const allSelected = [team1Player1, team1Player2, team2Player1, team2Player2];
    return allSelected.filter(player => player && player !== currentPlayer);
  };

  // Determine winner based on scores
  const score1 = parseInt(team1Score) || 0;
  const score2 = parseInt(team2Score) || 0;
  const team1IsWinner = score1 > score2 && score2 > 0;
  const team2IsWinner = score2 > score1 && score1 > 0;

  const winnerBadgeClass = 'winner-badge';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{editMatch ? 'Edit Match' : 'Add New Match'}</h2>
          <Button variant="close" onClick={onClose}>
            <X size={20} />
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="add-match-form">
          <div className="team-section">
            <div className="team-header">
              <h3>Team 1</h3>
              {team1IsWinner && (
                <div className={winnerBadgeClass}>
                  Winner
                </div>
              )}
            </div>
            <div className="team-inputs-row">
              <div className="player-inputs">
                <PlayerDropdown
                  value={team1Player1}
                  onChange={(player) => handlePlayerChange(setTeam1Player1, player)}
                  allPlayerNames={allPlayerNames || []}
                  onCreatePlayer={onCreatePlayer}
                  placeholder="Player 1"
                  excludePlayers={getExcludedPlayers(team1Player1)}
                />
                <PlayerDropdown
                  value={team1Player2}
                  onChange={(player) => handlePlayerChange(setTeam1Player2, player)}
                  allPlayerNames={allPlayerNames || []}
                  onCreatePlayer={onCreatePlayer}
                  placeholder="Player 2"
                  excludePlayers={getExcludedPlayers(team1Player2)}
                />
              </div>
              <input
                type="number"
                min="0"
                value={team1Score}
                onChange={(e) => setTeam1Score(e.target.value)}
                placeholder="0"
                className="score-input"
                required
              />
            </div>
          </div>

          <div className="vs-divider">VS</div>

          <div className="team-section">
            <div className="team-header">
              <h3>Team 2</h3>
              {team2IsWinner && (
                <div className={winnerBadgeClass}>
                  Winner
                </div>
              )}
            </div>
            <div className="team-inputs-row">
              <div className="player-inputs">
                <PlayerDropdown
                  value={team2Player1}
                  onChange={(player) => handlePlayerChange(setTeam2Player1, player)}
                  allPlayerNames={allPlayerNames || []}
                  onCreatePlayer={onCreatePlayer}
                  placeholder="Player 1"
                  excludePlayers={getExcludedPlayers(team2Player1)}
                />
                <PlayerDropdown
                  value={team2Player2}
                  onChange={(player) => handlePlayerChange(setTeam2Player2, player)}
                  allPlayerNames={allPlayerNames || []}
                  onCreatePlayer={onCreatePlayer}
                  placeholder="Player 2"
                  excludePlayers={getExcludedPlayers(team2Player2)}
                />
              </div>
              <input
                type="number"
                min="0"
                value={team2Score}
                onChange={(e) => setTeam2Score(e.target.value)}
                placeholder="0"
                className="score-input"
                required
              />
            </div>
          </div>

          <div className="modal-actions">
            <Button type="button" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" variant="success" disabled={isSubmitting}>
              {isSubmitting ? (editMatch ? 'Updating...' : 'Adding...') : (editMatch ? 'Update Match' : 'Add Match')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

