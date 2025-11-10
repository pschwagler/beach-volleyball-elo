import { useState, useRef, useEffect } from 'react';
import { ChevronDown, UserPlus } from 'lucide-react';

export default function PlayerDropdown({ value, onChange, allPlayerNames, onCreatePlayer, placeholder = "Select player" }) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchTerm('');
        setIsCreatingNew(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredPlayers = allPlayerNames
    ? allPlayerNames.filter(player => 
        player.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : [];

  const handleSelect = (player) => {
    onChange(player);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleCreateNew = async () => {
    const newName = searchTerm.trim();
    if (newName) {
      setIsCreating(true);
      try {
        // Create player in database if callback provided
        if (onCreatePlayer) {
          await onCreatePlayer(newName);
        }
        onChange(newName);
        setIsOpen(false);
        setSearchTerm('');
      } catch (error) {
        console.error('Error creating player:', error);
        alert('Error creating player. Please try again.');
      } finally {
        setIsCreating(false);
      }
    }
  };

  const showCreateOption = searchTerm.trim() && 
    !allPlayerNames.some(name => name.toLowerCase() === searchTerm.toLowerCase());

  return (
    <div className="player-dropdown-container" ref={dropdownRef}>
      <div 
        className={`player-dropdown-trigger ${isOpen ? 'open' : ''} ${isCreating ? 'disabled' : ''}`}
        onClick={() => !isCreating && setIsOpen(!isOpen)}
      >
        <span className={value ? 'player-dropdown-value' : 'player-dropdown-placeholder'}>
          {isCreating ? 'Creating player...' : (value || placeholder)}
        </span>
        <ChevronDown size={18} className={isOpen ? 'rotate-180' : ''} />
      </div>

      {isOpen && (
        <div className="player-dropdown-menu">
          <input
            type="text"
            className="player-dropdown-search"
            placeholder="Search or type new name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            autoFocus
            onClick={(e) => e.stopPropagation()}
          />
          
          <div className="player-dropdown-options">
            {showCreateOption && (
              <div 
                className={`player-dropdown-option create-new ${isCreating ? 'disabled' : ''}`}
                onClick={!isCreating ? handleCreateNew : undefined}
              >
                <UserPlus size={16} />
                <span>{isCreating ? 'Creating...' : `Create "${searchTerm}"`}</span>
              </div>
            )}
            
            {filteredPlayers.length > 0 ? (
              filteredPlayers.map((player) => (
                <div
                  key={player}
                  className={`player-dropdown-option ${player === value ? 'selected' : ''}`}
                  onClick={() => handleSelect(player)}
                >
                  {player}
                </div>
              ))
            ) : !showCreateOption ? (
              <div className="player-dropdown-option disabled">
                {searchTerm ? 'No players found' : 'No players available'}
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

