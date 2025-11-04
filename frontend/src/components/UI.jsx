import { useState, useRef, useEffect } from 'react';
import { Calendar, Trophy } from 'lucide-react';

// Button Component - handles all button variants
export function Button({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'default', // 'default', 'success', 'tab', 'close'
  className = '',
  active = false,
  type = 'button'
}) {
  let buttonClass = 'button';
  
  if (variant === 'success') {
    buttonClass = 'btn-success';
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
        style={{ position: 'relative' }}
      >
        {children}
      </span>
      {isVisible && (
        <div
          ref={tooltipRef}
          className="tooltip"
          style={{
            position: 'fixed',
            top: `${position.top}px`,
            left: `${position.left}px`,
            transform: 'translate(-50%, -100%)',
            pointerEvents: 'none',
            zIndex: 10000,
            willChange: 'transform',
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
export function MatchCard({ match, onPlayerClick }) {
  const team1Won = match.Winner === 'Team 1';
  const team2Won = match.Winner === 'Team 2';
  
  return (
    <div className="match-card">
      {/* Team 1 */}
      <div className={`match-team ${team1Won ? 'winner' : 'loser'}`}>
        <div className="team-players">
          <span className="player-name" onClick={() => onPlayerClick(match['Team 1 Player 1'])}>
            {match['Team 1 Player 1']}
          </span>
          <span className="player-name" onClick={() => onPlayerClick(match['Team 1 Player 2'])}>
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
          <span className="player-name" onClick={() => onPlayerClick(match['Team 2 Player 1'])}>
            {match['Team 2 Player 1']}
          </span>
          <span className="player-name" onClick={() => onPlayerClick(match['Team 2 Player 2'])}>
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

