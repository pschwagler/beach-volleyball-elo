import pkg from "whatsapp-web.js";
const { Client, LocalAuth } = pkg;
import qrcode from "qrcode";
import express from "express";
import cors from "cors";

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// WhatsApp client state
let client = null;
let qrCodeData = null;
let isReady = false;
let isAuthenticating = false;
let clientInfo = null;
let isInitializing = false; // NEW: Prevent race conditions
let authEventCount = 0; // Track duplicate events
let readyEventCount = 0; // Track duplicate events
let currentClientId = null; // Track client instance ID

// Initialize WhatsApp client
function initializeClient() {
  console.log("📞 initializeClient() called");

  if (client) {
    console.log(
      `⚠️  Client already exists [${currentClientId}], skipping initialization`
    );
    return;
  }

  if (isInitializing) {
    console.log("⚠️  Already initializing, skipping duplicate call");
    return;
  }

  // Generate unique client ID
  currentClientId = `client-${Date.now()}-${Math.random()
    .toString(36)
    .substr(2, 9)}`;
  console.log(`🆔 Creating new client with ID: ${currentClientId}`);
  console.log("🚀 Initializing WhatsApp client...");
  console.log("📂 Session data path: ./.wwebjs_auth");

  // Reset event counters for new initialization
  authEventCount = 0;
  readyEventCount = 0;

  isInitializing = true; // Set flag IMMEDIATELY
  isAuthenticating = true;
  qrCodeData = null;
  isReady = false;

  client = new Client({
    authStrategy: new LocalAuth({
      dataPath: "./.wwebjs_auth",
      clientId: "beach-volleyball-elo",
    }),
    puppeteer: {
      headless: true,
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    },
  });

  // Log when loading saved session
  client.on("loading_screen", (percent, message) => {
    console.log(
      `[${currentClientId}] 📂 Loading session... ${percent}% ${message}`
    );
  });

  // QR Code event
  client.on("qr", async (qr) => {
    console.log(`[${currentClientId}] 📱 QR Code received`);
    try {
      qrCodeData = await qrcode.toDataURL(qr);
      isAuthenticating = true;
      console.log(`[${currentClientId}] ✅ QR Code converted to data URL`);
    } catch (err) {
      console.error(`[${currentClientId}] ❌ Error generating QR code:`, err);
    }
  });

  // Ready event - use .once() to prevent duplicate events (known whatsapp-web.js issue)
  client.once("ready", async () => {
    readyEventCount++;
    console.log(
      `[${currentClientId}] 🟢 WhatsApp client is ready! (Ready Event #${readyEventCount})`
    );

    isReady = true;
    isAuthenticating = false;
    isInitializing = false; // Clear initialization flag
    qrCodeData = null;

    // Get client info
    try {
      const info = await client.info;
      clientInfo = {
        pushname: info.pushname,
        phone: info.wid.user,
        platform: info.platform,
      };
      console.log(`[${currentClientId}] 📱 Client info:`, clientInfo);
    } catch (err) {
      console.error(`[${currentClientId}] ❌ Error getting client info:`, err);
      // Even if we can't get info, the client is still ready
      // Just set basic info
      clientInfo = {
        pushname: "WhatsApp User",
        phone: "Connected",
        platform: "unknown",
      };
    }
  });

  // Authentication event - use .once() to prevent duplicate events (known whatsapp-web.js issue)
  client.once("authenticated", (session) => {
    authEventCount++;
    console.log(
      `[${currentClientId}] ✅ Client authenticated successfully (Auth Event #${authEventCount})`
    );

    console.log(`[${currentClientId}] 📱 Session saved to .wwebjs_auth/`);
    if (session) {
      console.log(`[${currentClientId}] 📦 Session type:`, typeof session);
    }
    isAuthenticating = false;
  });

  // Authentication failure
  client.on("auth_failure", (msg) => {
    console.error(`[${currentClientId}] ❌ Authentication failure:`, msg);
    isAuthenticating = false;
    isReady = false;
    qrCodeData = null;
  });

  // Disconnected event
  client.on("disconnected", (reason) => {
    console.error("❌ Client was disconnected:", reason);
    console.error(
      `📊 Final event counts - Auth: ${authEventCount}, Ready: ${readyEventCount}`
    );
    console.error("⚠️  You will need to re-scan QR code");

    // Clear ALL state
    isReady = false;
    isAuthenticating = false;
    isInitializing = false; // Clear initialization flag
    qrCodeData = null;
    clientInfo = null;
    client = null;
    authEventCount = 0;
    readyEventCount = 0;
  });

  // Initialize the client
  client.initialize().catch((err) => {
    console.error(`[${currentClientId}] ❌ Error initializing client:`, err);
    isAuthenticating = false;
    isInitializing = false;
    client = null;
    currentClientId = null;
  });

  console.log(`[${currentClientId}] ✅ Client initialization started`);
}

// API Routes

// Health check
app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    service: "whatsapp-service",
    timestamp: new Date().toISOString(),
  });
});

// Get QR code for authentication
app.get("/api/whatsapp/qr", (req, res) => {
  if (isReady) {
    return res.json({
      authenticated: true,
      qrCode: null,
      message: "Already authenticated",
      clientInfo,
    });
  }

  if (qrCodeData) {
    return res.json({
      authenticated: false,
      qrCode: qrCodeData,
      message: "Scan QR code to authenticate",
    });
  }

  res.json({
    authenticated: false,
    qrCode: null,
    message: isAuthenticating ? "Generating QR code..." : "Initializing...",
  });
});

// Get authentication status
app.get("/api/whatsapp/status", (req, res) => {
  
  res.json({
    isReady,
    isAuthenticating,
    hasQrCode: !!qrCodeData,
    clientInfo: isReady ? clientInfo : null,
  });

  if (!client) {
    initializeClient();
  }
});

// Initialize/reinitialize client
app.post("/api/whatsapp/initialize", (req, res) => {
  console.log("📥 Initialize endpoint called");

  if (isReady) {
    console.log("⚠️  Client already ready, ignoring initialize request");
    return res.json({
      success: false,
      message: "Client is already initialized and ready",
    });
  }

  if (isAuthenticating) {
    console.log(
      "⚠️  Client already authenticating, ignoring initialize request"
    );
    return res.json({
      success: false,
      message: "Client is currently authenticating",
    });
  }

  if (client) {
    console.log("⚠️  Client already exists, ignoring initialize request");
    return res.json({
      success: false,
      message: "Client is already initialized",
    });
  }

  initializeClient();
  res.json({
    success: true,
    message: "Initializing WhatsApp client...",
  });
});

// Logout and clear session
app.post("/api/whatsapp/logout", async (req, res) => {
  console.log("🚪 LOGOUT ENDPOINT CALLED");
  console.log("Request from:", req.ip);
  console.log("User-Agent:", req.get("User-Agent"));

  if (!client) {
    console.log("⚠️  No client to logout");
    return res.json({
      success: false,
      message: "No active client to logout",
    });
  }

  try {
    console.log("🔴 Calling client.logout()...");
    await client.logout();
    await client.destroy();
    client = null;
    isReady = false;
    isAuthenticating = false;
    qrCodeData = null;
    clientInfo = null;

    console.log("✅ Logout completed successfully");
    res.json({
      success: true,
      message: "Logged out successfully",
    });
  } catch (error) {
    console.error("❌ Error during logout:", error);
    res.status(500).json({
      success: false,
      message: "Error during logout",
      error: error.message,
    });
  }
});

// Get all group chats
app.get("/api/whatsapp/groups", async (req, res) => {
  if (!isReady) {
    return res.status(400).json({
      success: false,
      message: "WhatsApp client is not ready. Please authenticate first.",
    });
  }

  try {
    console.log("Fetching all chats...");
    const chats = await client.getChats();
    
    // Filter for group chats only
    const groups = chats
      .filter(chat => chat.isGroup)
      .map(group => ({
        id: group.id._serialized,
        name: group.name,
        participantCount: group.participants ? group.participants.length : 0,
      }));

    console.log(`Found ${groups.length} group chats`);

    res.json({
      success: true,
      groups: groups,
    });
  } catch (error) {
    console.error("Error fetching groups:", error);
    res.status(500).json({
      success: false,
      message: "Error fetching group chats",
      error: error.message,
    });
  }
});

// Send a test message
app.post("/api/whatsapp/send", async (req, res) => {
  const { phoneNumber, message, chatId } = req.body;

  // Accept either phoneNumber (for individuals) or chatId (for groups)
  if (!message) {
    return res.status(400).json({
      success: false,
      message: "Message is required",
    });
  }

  if (!phoneNumber && !chatId) {
    return res.status(400).json({
      success: false,
      message: "Either phoneNumber or chatId is required",
    });
  }

  if (!isReady) {
    return res.status(400).json({
      success: false,
      message: "WhatsApp client is not ready. Please authenticate first.",
    });
  }

  try {
    let targetChatId;

    // Use chatId if provided (for groups), otherwise format phone number
    if (chatId) {
      targetChatId = chatId;
      console.log(`Attempting to send message to chat ${chatId}`);
    } else {
      // Format phone number (remove non-digits and ensure proper format)
      let formattedNumber = phoneNumber.replace(/\D/g, "");

      // Add country code if not present (assuming US for now)
      if (formattedNumber.length === 10) {
        formattedNumber = "1" + formattedNumber;
      }

      // WhatsApp ID format: number@c.us
      targetChatId = `${formattedNumber}@c.us`;

      console.log(`Attempting to send message to ${targetChatId}`);

      // Check if number exists on WhatsApp
      const isRegistered = await client.isRegisteredUser(targetChatId);

      if (!isRegistered) {
        return res.status(400).json({
          success: false,
          message: "This phone number is not registered on WhatsApp",
        });
      }
    }

    // Send the message
    const response = await client.sendMessage(targetChatId, message);

    console.log("Message sent successfully:", response.id);

    res.json({
      success: true,
      message: "Message sent successfully",
      messageId: response.id._serialized,
    });
  } catch (error) {
    console.error("Error sending message:", error);
    res.status(500).json({
      success: false,
      message: "Error sending message",
      error: error.message,
    });
  }
});

// Error handling middleware (must be last)
app.use((err, req, res, next) => {
  console.error("❌ Express Error Handler:");
  console.error("Path:", req.path);
  console.error("Error:", err);
  console.error("Stack:", err.stack);

  res.status(500).json({
    success: false,
    message: "Internal server error",
    error: err.message,
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`WhatsApp service running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
});

// Graceful shutdown
process.on("SIGINT", async () => {
  console.log("\nShutting down gracefully...");
  if (client) {
    await client.destroy();
  }
  process.exit(0);
});

// Global error handlers
process.on("uncaughtException", (error) => {
  console.error("❌ Uncaught Exception:", error);
  console.error("Stack trace:", error.stack);
  // Don't exit - let the service try to recover
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("❌ Unhandled Promise Rejection at:", promise);
  console.error("Reason:", reason);
  if (reason instanceof Error) {
    console.error("Stack trace:", reason.stack);
  }
  // Don't exit - let the service try to recover
});
