import { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, MessageCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const MODE_TITLES = {
  'sign-in': 'Sign In',
  'sign-up': 'Create Account',
  'sms-login': 'SMS Login',
  verify: 'Verify Phone Number',
};

const defaultFormState = {
  phoneNumber: '',
  password: '',
  name: '',
  email: '',
  code: '',
};

const getErrorMessage = (error) => error.response?.data?.detail || error.message || 'Something went wrong';

export default function AuthModal({ isOpen, mode = 'sign-in', onClose }) {
  const {
    loginWithPassword,
    loginWithSms,
    signup,
    sendVerificationCode,
    verifyPhone,
  } = useAuth();
  const [activeMode, setActiveMode] = useState(mode);
  const [formData, setFormData] = useState(defaultFormState);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setActiveMode(mode);
      setErrorMessage('');
      setStatusMessage('');
    }
  }, [isOpen, mode]);

  if (!isOpen) {
    return null;
  }

  const handleClose = () => {
    setActiveMode('sign-in');
    setFormData(defaultFormState);
    setErrorMessage('');
    setStatusMessage('');
    onClose?.();
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSendVerification = async () => {
    if (!formData.phoneNumber) {
      setErrorMessage('Phone number is required');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage('');
    setStatusMessage('');
    try {
      await sendVerificationCode(formData.phoneNumber);
      setStatusMessage('Verification code sent! Please check your SMS messages.');
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrorMessage('');
    setStatusMessage('');
    setIsSubmitting(true);

    try {
      if (activeMode === 'sign-in') {
        await loginWithPassword(formData.phoneNumber, formData.password);
        handleClose();
        return;
      }

      if (activeMode === 'sign-up') {
        const result = await signup({
          phoneNumber: formData.phoneNumber,
          password: formData.password,
          name: formData.name,
          email: formData.email,
        });
        setStatusMessage('Account created! Enter the verification code we just sent you.');
        setFormData((prev) => ({
          ...prev,
          phoneNumber: result.phone_number || prev.phoneNumber,
        }));
        setActiveMode('verify');
        return;
      }

      if (activeMode === 'sms-login') {
        await loginWithSms(formData.phoneNumber, formData.code);
        handleClose();
        return;
      }

      if (activeMode === 'verify') {
        await verifyPhone(formData.phoneNumber, formData.code);
        handleClose();
      }
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderDescription = () => {
    switch (activeMode) {
      case 'sign-up':
        return 'Create an account to record matches, manage sessions, and send WhatsApp updates.';
      case 'sms-login':
        return 'Enter your phone number and the 6-digit code we send via SMS.';
      case 'verify':
        return 'Enter the 6-digit verification code we sent to your phone to complete signup.';
      default:
        return 'Sign in to manage sessions, record matches, and sync WhatsApp updates.';
    }
  };

  return (
    <div className="auth-modal-overlay">
      <div className="auth-modal">
        <div className="auth-modal__header">
          <div>
            <p className="auth-modal__eyebrow">Beach Volleyball Accounts</p>
            <h2>{MODE_TITLES[activeMode]}</h2>
          </div>
          <button className="auth-modal__close" onClick={handleClose} aria-label="Close authentication modal">
            <X size={20} />
          </button>
        </div>

        <p className="auth-modal__description">{renderDescription()}</p>

        {(statusMessage || errorMessage) && (
          <div className={`auth-modal__alert ${errorMessage ? 'error' : 'success'}`}>
            {errorMessage ? <AlertCircle size={18} /> : <CheckCircle size={18} />}
            <span>{errorMessage || statusMessage}</span>
          </div>
        )}

        <form className="auth-modal__form" onSubmit={handleSubmit}>
          <label className="auth-modal__label">
            Phone Number
            <input
              type="tel"
              name="phoneNumber"
              className="auth-modal__input"
              placeholder="+15551234567"
              value={formData.phoneNumber}
              onChange={handleInputChange}
              required
            />
          </label>

          {(activeMode === 'sign-in' || activeMode === 'sign-up') && (
            <label className="auth-modal__label">
              Password
              <input
                type="password"
                name="password"
                className="auth-modal__input"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleInputChange}
                required={activeMode === 'sign-in'}
              />
            </label>
          )}

          {activeMode === 'sign-up' && (
            <>
              <label className="auth-modal__label">
                Name
                <input
                  type="text"
                  name="name"
                  className="auth-modal__input"
                  placeholder="Optional"
                  value={formData.name}
                  onChange={handleInputChange}
                />
              </label>
              <label className="auth-modal__label">
                Email
                <input
                  type="email"
                  name="email"
                  className="auth-modal__input"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleInputChange}
                />
              </label>
            </>
          )}

          {(activeMode === 'sms-login' || activeMode === 'verify') && (
            <label className="auth-modal__label">
              Verification Code
              <div className="auth-modal__code-row">
                <input
                  type="text"
                  name="code"
                  className="auth-modal__input"
                  placeholder="123456"
                  value={formData.code}
                  onChange={handleInputChange}
                  maxLength={6}
                  required
                />
                <button
                  type="button"
                  className="auth-modal__ghost-button"
                  onClick={handleSendVerification}
                  disabled={isSubmitting}
                >
                  <MessageCircle size={16} />
                  Send Code
                </button>
              </div>
            </label>
          )}

          <button type="submit" className="auth-modal__submit" disabled={isSubmitting}>
            {isSubmitting ? 'Please wait...' : MODE_TITLES[activeMode]}
          </button>
        </form>
      </div>
    </div>
  );
}

