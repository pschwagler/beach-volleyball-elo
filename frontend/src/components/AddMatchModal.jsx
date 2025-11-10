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
            <h3>Team 1</h3>
            <div className="player-inputs">
              <PlayerDropdown
                value={team1Player1}
                onChange={setTeam1Player1}
                allPlayerNames={allPlayerNames || []}
                onCreatePlayer={onCreatePlayer}
                placeholder="Player 1"
              />
              <PlayerDropdown
                value={team1Player2}
                onChange={setTeam1Player2}
                allPlayerNames={allPlayerNames || []}
                onCreatePlayer={onCreatePlayer}
                placeholder="Player 2"
              />
            </div>
            <input
              type="number"
              min="0"
              value={team1Score}
              onChange={(e) => setTeam1Score(e.target.value)}
              placeholder="Score"
              className="score-input"
              required
            />
          </div>

          <div className="vs-divider">VS</div>

          <div className="team-section">
            <h3>Team 2</h3>
            <div className="player-inputs">
              <PlayerDropdown
                value={team2Player1}
                onChange={setTeam2Player1}
                allPlayerNames={allPlayerNames || []}
                onCreatePlayer={onCreatePlayer}
                placeholder="Player 1"
              />
              <PlayerDropdown
                value={team2Player2}
                onChange={setTeam2Player2}
                allPlayerNames={allPlayerNames || []}
                onCreatePlayer={onCreatePlayer}
                placeholder="Player 2"
              />
            </div>
            <input
              type="number"
              min="0"
              value={team2Score}
              onChange={(e) => setTeam2Score(e.target.value)}
              placeholder="Score"
              className="score-input"
              required
            />
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

