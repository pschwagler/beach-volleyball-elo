import { useState, useEffect } from "react";
import {
  QrCode,
  Send,
  LogOut,
  RefreshCw,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import "../App.css";

function WhatsAppPage() {
  const [qrCode, setQrCode] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [sendStatus, setSendStatus] = useState(null);
  const [clientInfo, setClientInfo] = useState(null);
  const [error, setError] = useState(null);
  const [serviceUnavailable, setServiceUnavailable] = useState(false);
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState("");
  const [loadingGroups, setLoadingGroups] = useState(false);

  const WHATSAPP_API_BASE = "http://localhost:3001/api/whatsapp";

  const fetchGroups = async () => {
    setLoadingGroups(true);
    try {
      const response = await fetch(`${WHATSAPP_API_BASE}/groups`);
      const data = await response.json();

      if (data.success) {
        setGroups(data.groups);
        console.log(`Loaded ${data.groups.length} groups`);
      } else {
        console.error("Failed to fetch groups:", data.message);
      }
    } catch (err) {
      console.error("Error fetching groups:", err);
    }
    setLoadingGroups(false);
  };

  // Poll for QR code and status
  useEffect(() => {
    let interval;
    let statusSuccessful = false;

    const checkStatus = async () => {
      // Stop polling if service is unavailable
      if (serviceUnavailable) {
        console.log("Service marked as unavailable, skipping status check");
        return;
      }

      try {
        const response = await fetch(`${WHATSAPP_API_BASE}/status`);

        // Check for 500 error - service is not enabled
        if (response.status === 500 || response.status === 503) {
          console.error("WhatsApp service returned error:", response.status);
          setServiceUnavailable(true);
          setError(
            "WhatsApp integration is not configured or unavailable at this time. Please contact your administrator."
          );
          setIsLoading(false);
          if (interval) clearInterval(interval);
          return;
        }

        if (!response.ok) {
          throw new Error(`Status check failed: ${response.status}`);
        }

        const data = await response.json();
        statusSuccessful = true; // Mark that status API is working

        setIsAuthenticated(data.isReady);
        setClientInfo(data.clientInfo);
        setError(null); // Clear any previous errors
        setServiceUnavailable(false); // Clear unavailable flag

        // Fetch groups when authenticated
        if (data.isReady && groups.length === 0) {
          fetchGroups();
        }

        // Only fetch QR code if:
        // 1. Not authenticated yet
        // 2. Don't already have a QR code
        // 3. Status check was successful
        if (!data.isReady && !qrCode && statusSuccessful) {
          fetchQRCode();
        }

        setIsLoading(false);
      } catch (err) {
        console.error("Error checking status:", err);
        statusSuccessful = false;
        
        // Network error - service likely not running
        if (err.message.includes("Failed to fetch")) {
          setServiceUnavailable(true);
          setError(
            "WhatsApp integration is currently unavailable. Please try again later or contact your administrator."
          );
          if (interval) clearInterval(interval);
        } else {
          setError(
            "Unable to connect to WhatsApp integration. Please try again later."
          );
        }
        setIsLoading(false);
      }
    };

    const fetchQRCode = async () => {
      try {
        const response = await fetch(`${WHATSAPP_API_BASE}/qr`);

        if (!response.ok) {
          throw new Error(`QR fetch failed: ${response.status}`);
        }

        const data = await response.json();

        if (data.authenticated) {
          setIsAuthenticated(true);
          setClientInfo(data.clientInfo);
          setQrCode(null);
        } else if (data.qrCode) {
          setQrCode(data.qrCode);
          setIsAuthenticated(false);
        }
      } catch (err) {
        console.error("Error fetching QR code:", err);
        setError(
          "Failed to fetch QR code. The service may still be initializing."
        );
      }
    };

    // Initial check
    checkStatus();

    // Poll every 3 seconds when not authenticated AND service is available
    if (!isAuthenticated && !serviceUnavailable) {
      interval = setInterval(checkStatus, 3000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isAuthenticated, qrCode, serviceUnavailable, groups.length]);

  const handleLogout = async () => {
    if (
      !confirm(
        "Are you sure you want to logout? You will need to scan the QR code again."
      )
    ) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${WHATSAPP_API_BASE}/logout`, {
        method: "POST",
      });
      const data = await response.json();

      if (data.success) {
        setIsAuthenticated(false);
        setClientInfo(null);
        setQrCode(null);
        setSendStatus({ type: "success", message: "Logged out successfully" });
      } else {
        setError(data.message);
      }
    } catch (err) {
      console.error("Error logging out:", err);
      setError("Failed to logout");
    }
    setIsLoading(false);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    setSendStatus(null);
    setError(null);

    if (!selectedGroup || !message) {
      setSendStatus({ type: "error", message: "Please select a group and enter a message" });
      return;
    }

    try {
      const response = await fetch(`${WHATSAPP_API_BASE}/send`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          chatId: selectedGroup,
          message,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setSendStatus({
          type: "success",
          message: "Message sent successfully!",
        });
        setMessage(""); // Clear message field
      } else {
        setSendStatus({ type: "error", message: data.message });
      }
    } catch (err) {
      console.error("Error sending message:", err);
      setSendStatus({ type: "error", message: "Failed to send message" });
    }
  };

  return (
    <>
      <div
        className="container"
        style={{ maxWidth: "800px", margin: "0 auto", padding: "40px 20px" }}
      >
        <div style={{ textAlign: "center", marginBottom: "40px" }}>
          <h1
            style={{
              fontSize: "2.5rem",
              fontWeight: "bold",
              marginBottom: "10px",
            }}
          >
            🏐 WhatsApp Integration
          </h1>
          <p style={{ color: "#666", fontSize: "1.1rem" }}>
            Connect your WhatsApp to send notifications
          </p>
        </div>

        {error && (
          <div
            style={{
              backgroundColor: serviceUnavailable ? "#fff4e6" : "#fee",
              border: `1px solid ${serviceUnavailable ? "#ff9800" : "#fcc"}`,
              borderRadius: "8px",
              padding: "20px",
              marginBottom: "20px",
            }}
          >
            <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
              <AlertCircle size={24} color={serviceUnavailable ? "#ff9800" : "#c00"} />
              <div style={{ flex: 1 }}>
                <div style={{ 
                  fontWeight: "bold", 
                  color: serviceUnavailable ? "#e65100" : "#c00",
                  marginBottom: "8px",
                  fontSize: "1.1rem"
                }}>
                  {serviceUnavailable ? "⚠️ Service Unavailable" : "Error"}
                </div>
                <div style={{ color: "#333", lineHeight: "1.6" }}>
                  {error}
                </div>
              </div>
            </div>
          </div>
        )}

        {serviceUnavailable ? (
          // Don't show anything else if service is unavailable - error message is enough
          null
        ) : isLoading && !qrCode && !isAuthenticated ? (
          <div style={{ textAlign: "center", padding: "60px 20px" }}>
            <RefreshCw
              size={48}
              style={{ animation: "spin 1s linear infinite" }}
            />
            <p style={{ marginTop: "20px", fontSize: "1.1rem" }}>
              Loading WhatsApp service...
            </p>
          </div>
        ) : isAuthenticated ? (
          <div>
            {/* Authenticated View */}
            <div
              style={{
                backgroundColor: "#e8f5e9",
                border: "1px solid #4caf50",
                borderRadius: "8px",
                padding: "20px",
                marginBottom: "30px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <div
                style={{ display: "flex", alignItems: "center", gap: "10px" }}
              >
                <CheckCircle size={24} color="#4caf50" />
                <div>
                  <div style={{ fontWeight: "bold", color: "#2e7d32" }}>
                    Connected to WhatsApp
                  </div>
                  {clientInfo && (
                    <div
                      style={{
                        fontSize: "0.9rem",
                        color: "#666",
                        marginTop: "4px",
                      }}
                    >
                      {clientInfo.pushname} • {clientInfo.phone}
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={handleLogout}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "10px 20px",
                  backgroundColor: "#f44336",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontWeight: "500",
                }}
              >
                <LogOut size={16} />
                Logout
              </button>
            </div>

            {/* Send Message Form */}
            <div
              style={{
                backgroundColor: "white",
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "30px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              }}
            >
              <h2
                style={{
                  fontSize: "1.5rem",
                  marginBottom: "20px",
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                }}
              >
                <Send size={24} />
                Send Message to Group
              </h2>

              <form onSubmit={handleSendMessage}>
                <div style={{ marginBottom: "20px" }}>
                  <div style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    justifyContent: "space-between",
                    marginBottom: "8px"
                  }}>
                    <label
                      style={{
                        fontWeight: "500",
                        color: "#333",
                      }}
                    >
                      Select Group
                    </label>
                    <button
                      type="button"
                      onClick={fetchGroups}
                      disabled={loadingGroups}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        padding: "6px 12px",
                        fontSize: "0.9rem",
                        backgroundColor: "#f5f5f5",
                        color: "#333",
                        border: "1px solid #ddd",
                        borderRadius: "4px",
                        cursor: loadingGroups ? "not-allowed" : "pointer",
                        opacity: loadingGroups ? 0.6 : 1,
                      }}
                    >
                      <RefreshCw size={14} style={{ animation: loadingGroups ? "spin 1s linear infinite" : "none" }} />
                      Refresh
                    </button>
                  </div>
                  {loadingGroups ? (
                    <div style={{ padding: "12px", color: "#666" }}>
                      Loading groups...
                    </div>
                  ) : groups.length === 0 ? (
                    <div style={{ 
                      padding: "12px", 
                      backgroundColor: "#f5f5f5", 
                      borderRadius: "6px",
                      color: "#666"
                    }}>
                      No group chats found. Make sure you have group chats in WhatsApp.
                    </div>
                  ) : (
                    <select
                      value={selectedGroup}
                      onChange={(e) => setSelectedGroup(e.target.value)}
                      style={{
                        width: "100%",
                        padding: "12px",
                        fontSize: "1rem",
                        border: "1px solid #ddd",
                        borderRadius: "6px",
                        boxSizing: "border-box",
                        backgroundColor: "white",
                        cursor: "pointer",
                      }}
                    >
                      <option value="">-- Select a group --</option>
                      {groups.map((group) => (
                        <option key={group.id} value={group.id}>
                          {group.name} ({group.participantCount} members)
                        </option>
                      ))}
                    </select>
                  )}
                  <small
                    style={{
                      color: "#666",
                      fontSize: "0.85rem",
                      display: "block",
                      marginTop: "4px",
                    }}
                  >
                    Choose which group chat to send the message to
                  </small>
                </div>

                <div style={{ marginBottom: "20px" }}>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "8px",
                      fontWeight: "500",
                      color: "#333",
                    }}
                  >
                    Message
                  </label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Enter your message here..."
                    rows={4}
                    style={{
                      width: "100%",
                      padding: "12px",
                      fontSize: "1rem",
                      border: "1px solid #ddd",
                      borderRadius: "6px",
                      boxSizing: "border-box",
                      fontFamily: "inherit",
                      resize: "vertical",
                    }}
                  />
                </div>

                {sendStatus && (
                  <div
                    style={{
                      backgroundColor:
                        sendStatus.type === "success" ? "#e8f5e9" : "#fee",
                      border: `1px solid ${
                        sendStatus.type === "success" ? "#4caf50" : "#fcc"
                      }`,
                      borderRadius: "6px",
                      padding: "12px",
                      marginBottom: "20px",
                      color: sendStatus.type === "success" ? "#2e7d32" : "#c00",
                    }}
                  >
                    {sendStatus.message}
                  </div>
                )}

                <button
                  type="submit"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    width: "100%",
                    padding: "14px",
                    backgroundColor: "#25D366",
                    color: "white",
                    border: "none",
                    borderRadius: "6px",
                    fontSize: "1.1rem",
                    fontWeight: "600",
                    cursor: "pointer",
                    transition: "background-color 0.2s",
                  }}
                  onMouseOver={(e) =>
                    (e.target.style.backgroundColor = "#1da851")
                  }
                  onMouseOut={(e) =>
                    (e.target.style.backgroundColor = "#25D366")
                  }
                >
                  <Send size={20} />
                  Send Message
                </button>
              </form>
            </div>
          </div>
        ) : (
          <div>
            {/* QR Code View */}
            <div
              style={{
                backgroundColor: "white",
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "40px",
                textAlign: "center",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              }}
            >
              <QrCode size={48} style={{ margin: "0 auto 20px" }} />
              <h2 style={{ fontSize: "1.8rem", marginBottom: "10px" }}>
                Scan QR Code to Connect
              </h2>
              <p style={{ color: "#666", marginBottom: "30px" }}>
                Open WhatsApp on your phone, go to Settings → Linked Devices →
                Link a Device
              </p>

              {qrCode ? (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: "20px",
                  }}
                >
                  <img
                    src={qrCode}
                    alt="WhatsApp QR Code"
                    style={{
                      maxWidth: "300px",
                      width: "100%",
                      height: "auto",
                      border: "2px solid #ddd",
                      borderRadius: "8px",
                      padding: "10px",
                      backgroundColor: "white",
                    }}
                  />
                  <p style={{ color: "#666", fontSize: "0.9rem" }}>
                    Waiting for scan...
                  </p>
                </div>
              ) : (
                <div style={{ padding: "40px" }}>
                  <RefreshCw
                    size={48}
                    style={{
                      animation: "spin 1s linear infinite",
                      color: "#25D366",
                      margin: "0 auto 20px",
                      display: "block",
                    }}
                  />
                  <p style={{ color: "#666", fontSize: "1.1rem" }}>
                    {isLoading
                      ? "Generating QR code..."
                      : "Initializing WhatsApp service..."}
                  </p>
                  <p
                    style={{
                      color: "#999",
                      fontSize: "0.9rem",
                      marginTop: "10px",
                    }}
                  >
                    This should only take a few seconds
                  </p>
                </div>
              )}
            </div>

            {/* Only show instructions when QR code is displayed */}
            {qrCode && (
              <div
                style={{
                  marginTop: "30px",
                  padding: "20px",
                  backgroundColor: "#fff9e6",
                  border: "1px solid #ffe082",
                  borderRadius: "8px",
                }}
              >
                <h3 style={{ fontSize: "1.1rem", marginBottom: "10px" }}>
                  📱 How to Connect:
                </h3>
                <ol style={{ marginLeft: "20px", lineHeight: "1.8" }}>
                  <li>Open WhatsApp on your phone</li>
                  <li>Tap Menu (⋮) or Settings</li>
                  <li>Select "Linked Devices"</li>
                  <li>Tap "Link a Device"</li>
                  <li>Scan the QR code above</li>
                </ol>
              </div>
            )}
          </div>
        )}

        <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
      </div>
    </>
  );
}

export default WhatsAppPage;
