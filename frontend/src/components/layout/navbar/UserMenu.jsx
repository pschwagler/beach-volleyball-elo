import { useState, useRef, useEffect } from 'react';
import { User, LogIn, UserPlus, UserCircle, LogOut } from 'lucide-react';
import NavDropdown from './NavDropdown';
import NavDropdownItem from './NavDropdownItem';

export default function UserMenu({
  isLoggedIn,
  user,
  onMenuClick,
  onSignIn,
  onSignUp,
  onSignOut,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleItemClick = (action) => {
    setIsOpen(false);
    switch (action) {
      case 'sign-in':
        onSignIn?.();
        break;
      case 'sign-up':
        onSignUp?.();
        break;
      case 'sign-out':
        onSignOut?.();
        break;
      default:
        onMenuClick?.(action);
    }
  };

  return (
    <div className="navbar-menu-group" ref={menuRef}>
      <button
        className="navbar-menu-button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="User menu"
      >
        <User size={20} />
        <span className="navbar-menu-label">Account</span>
      </button>

      {isOpen && (
        <NavDropdown className="navbar-dropdown-user">
          {!isLoggedIn ? (
            <>
              <NavDropdownItem icon={UserPlus} onClick={() => handleItemClick('sign-up')}>
                Sign Up
              </NavDropdownItem>
              <NavDropdownItem icon={LogIn} onClick={() => handleItemClick('sign-in')}>
                Sign In
              </NavDropdownItem>
            </>
          ) : (
            <>
              <div className="navbar-dropdown-header">
                Signed in as {user?.name || user?.phone_number || 'Member'}
              </div>
              <NavDropdownItem icon={UserCircle} onClick={() => handleItemClick('profile')}>
                My Profile
              </NavDropdownItem>
              <NavDropdownItem
                icon={LogOut}
                variant="danger"
                onClick={() => handleItemClick('sign-out')}
              >
                Sign Out
              </NavDropdownItem>
            </>
          )}
        </NavDropdown>
      )}
    </div>
  );
}

