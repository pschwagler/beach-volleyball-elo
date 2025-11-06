# WhatsApp Integration - Quick Start

Get the WhatsApp integration running in 3 simple steps!

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Install WhatsApp service dependencies
cd whatsapp-service
npm install
cd ..

# Install Python dependencies (if not already done)
pip install -r requirements.txt
```

Or use the Makefile:
```bash
make whatsapp-install
```

### Step 2: Start the Services

**Terminal 1 - Main App:**
```bash
make dev
# or manually:
# uvicorn backend.api.main:app --reload
```

**Terminal 2 - WhatsApp Service:**
```bash
make whatsapp
# or manually:
# cd whatsapp-service && npm start
```

### Step 3: Connect WhatsApp

1. Open http://localhost:8000 (or http://localhost:5173 if using Vite dev server)
2. Click the **"WhatsApp"** button in the navigation bar
3. Click **"Initialize WhatsApp"**
4. Scan the QR code with your phone:
   - Open WhatsApp on your phone
   - Go to **Settings → Linked Devices**
   - Tap **"Link a Device"**
   - Scan the QR code

## 📱 Send a Test Message

Once connected:
1. Enter a phone number with country code (e.g., `15551234567`)
2. Type your message
3. Click **"Send Message"**

## 🎯 That's It!

The WhatsApp session will persist, so you won't need to scan the QR code every time you restart the service.

## 📖 Need More Help?

See [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) for detailed documentation, troubleshooting, and API details.

## 🛑 Stop the Services

Press `Ctrl+C` in both terminal windows to stop the services.

