import { useState, useRef, useEffect } from 'react';
import { Calendar, Trophy, Edit } from 'lucide-react';

// Button Component - handles all button variants
export function Button({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'default', // 'default', 'success', 'danger', 'tab', 'close', 'whatsapp'
  className = '',
  active = false,
  type = 'button',
  style = {}
}) {
  let buttonClass = 'button';
  
  if (variant === 'success') {
    buttonClass = 'btn-success';
  } else if (variant === 'danger') {
    buttonClass = 'btn-danger';
  } else if (variant === 'whatsapp') {
    buttonClass = 'btn-whatsapp';
  } else if (variant === 'tab') {
    buttonClass = `tab ${active ? 'active' : ''}`;
  } else if (variant === 'close') {
    buttonClass = 'close-btn';
  }
  
  return (
    <button
      type={type}
      className={`${buttonClass} ${className}`}
      onClick={onClick}
      disabled={disabled}
      style={style}
    >
      {children}
    </button>
  );
}

// Alert Component - displays messages
export function Alert({ type, children, className = '' }) {
  if (!type || !children) return null;
  
  return (
    <div className={`${type} ${className}`}>
      {children}
    </div>
  );
}

// Tooltip Component - React-based tooltip
export function Tooltip({ children, text }) {
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const [isVisible, setIsVisible] = useState(false);
  const tooltipRef = useRef(null);
  const triggerRef = useRef(null);
  
  const handleMouseEnter = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    // Set initial position and show the tooltip
    setPosition({
      top: rect.top - 10,
      left: rect.left + rect.width / 2,
    });
    setIsVisible(true);
  };
  
  const handleMouseLeave = () => {
    setIsVisible(false);
  };
  
  return (
    <>
      <span
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="tooltip-trigger"
      >
        {children}
      </span>
      {isVisible && (
        <div
          ref={tooltipRef}
          className="tooltip tooltip-fixed"
          style={{
            top: `${position.top}px`,
            left: `${position.left}px`,
          }}
        >
          {text}
        </div>
      )}
    </>
  );
}

// Tabs Component - tab navigation
export function Tabs({ activeTab, onTabChange }) {
  return (
    <div className="tabs">
      <Button
        variant="tab"
        active={activeTab === 'matches'}
        onClick={() => onTabChange('matches')}
      >
        <Calendar size={18} />
        Matches
      </Button>
      <Button
        variant="tab"
        active={activeTab === 'rankings'}
        onClick={() => onTabChange('rankings')}
      >
        <Trophy size={18} />
        Players
      </Button>
    </div>
  );
}

// MatchCard Component - individual match display
export function MatchCard({ match, onPlayerClick, onEdit, showEdit = false }) {
  const team1Won = match.Winner === 'Team 1';
  const team2Won = match.Winner === 'Team 2';
  
  const handleCardClick = (e) => {
    // Don't trigger card click if clicking on player name
    if (e.target.classList.contains('player-name')) {
      return;
    }
    if (showEdit && onEdit) {
      onEdit(match);
    }
  };
  
  return (
    <div 
      className={`match-card ${showEdit ? 'editable' : ''}`}
      onClick={handleCardClick}
    >
      {/* Edit icon for active session matches */}
      {showEdit && onEdit && (
        <div className="match-card-edit-icon">
          <Edit size={16} />
        </div>
      )}
      
      {/* Team 1 */}
      <div className={`match-team ${team1Won ? 'winner' : 'loser'}`}>
        <div className="team-players">
          <span className="player-name" onClick={(e) => { e.stopPropagation(); onPlayerClick(match['Team 1 Player 1']); }}>
            {match['Team 1 Player 1']}
          </span>
          <span className="player-name" onClick={(e) => { e.stopPropagation(); onPlayerClick(match['Team 1 Player 2']); }}>
            {match['Team 1 Player 2']}
          </span>
        </div>
        <div className={`team-score ${team1Won ? 'winner-score' : 'loser-score'}`}>
          {match['Team 1 Score']}
        </div>
      </div>

      {/* Team 2 */}
      <div className={`match-team ${team2Won ? 'winner' : 'loser'}`}>
        <div className="team-players">
          <span className="player-name" onClick={(e) => { e.stopPropagation(); onPlayerClick(match['Team 2 Player 1']); }}>
            {match['Team 2 Player 1']}
          </span>
          <span className="player-name" onClick={(e) => { e.stopPropagation(); onPlayerClick(match['Team 2 Player 2']); }}>
            {match['Team 2 Player 2']}
          </span>
        </div>
        <div className={`team-score ${team2Won ? 'winner-score' : 'loser-score'}`}>
          {match['Team 2 Score']}
        </div>
      </div>
    </div>
  );
}

