# WhatsApp Integration Setup Guide

This guide will help you set up the WhatsApp integration feature for the Beach Volleyball ELO system.

## Overview

The WhatsApp integration allows you to:
- Connect your WhatsApp account via QR code authentication
- Send test messages to phone numbers
- Use WhatsApp for notifications and updates

The integration consists of two parts:
1. **Node.js WhatsApp Service** - Handles WhatsApp Web.js integration (port 3001)
2. **Python Backend Proxy** (optional) - Proxies requests through the FastAPI backend (port 8000)

## Prerequisites

- Node.js 16+ installed
- Python 3.7+ with requirements installed
- Active internet connection
- WhatsApp account on your mobile device

## Installation

### 1. Install Node.js Dependencies

Navigate to the whatsapp-service directory and install dependencies:

```bash
cd whatsapp-service
npm install
```

### 2. Install Python Dependencies

If you haven't already, install the Python dependencies (including httpx for proxy support):

```bash
# From the root directory
pip install -r requirements.txt
```

## Running the Services

You'll need to run both the WhatsApp service and your main application.

### Option 1: Run Services Separately

**Terminal 1 - WhatsApp Service:**
```bash
cd whatsapp-service
npm start
```

The WhatsApp service will start on `http://localhost:3001`.

**Terminal 2 - Main Application:**
```bash
# Backend
uvicorn backend.api.main:app --reload

# Frontend (separate terminal)
cd frontend
npm run dev
```

### Option 2: Using Makefile (if available)

```bash
# Start WhatsApp service
make whatsapp

# Start main app
make dev
```

## Using the WhatsApp Integration

### 1. Access the WhatsApp Page

Once the services are running:
1. Open your browser and navigate to your app (e.g., `http://localhost:5173`)
2. Click the "WhatsApp" button in the navigation bar
3. Or navigate directly to `/whatsapp`

### 2. Connect Your WhatsApp Account

1. Click "Initialize WhatsApp" if the QR code doesn't appear automatically
2. Open WhatsApp on your mobile device
3. Go to **Settings → Linked Devices** (or tap the three dots menu → Linked Devices)
4. Tap **"Link a Device"**
5. Scan the QR code displayed in your browser
6. Wait for authentication to complete (the page will update automatically)

### 3. Send Test Messages

Once authenticated:
1. Enter a phone number with country code (e.g., `15551234567` for US)
2. Type your message
3. Click "Send Message"

### Phone Number Format

The phone number must include the country code:
- **USA**: `1` + 10-digit number → `15551234567`
- **UK**: `44` + number → `447700900000`
- **India**: `91` + number → `919876543210`

## Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
│   Port: 5173    │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌──────────────────┐
│  Python Backend │  │  Node.js Service │
│   (FastAPI)     │  │  (WhatsApp.js)   │
│   Port: 8000    │  │  Port: 3001      │
└────────┬────────┘  └──────────────────┘
         │                  │
         └──────────────────┘
         (Backend proxies to Node service)
```

### API Endpoints

The frontend can call either:
1. **Direct to Node.js service**: `http://localhost:3001/api/whatsapp/*`
2. **Through Python proxy**: `http://localhost:8000/api/whatsapp/*`

Both provide the same functionality:
- `GET /api/whatsapp/qr` - Get QR code for authentication
- `GET /api/whatsapp/status` - Check authentication status
- `POST /api/whatsapp/initialize` - Initialize WhatsApp client
- `POST /api/whatsapp/logout` - Logout and clear session
- `POST /api/whatsapp/send` - Send a message

## Troubleshooting

### QR Code Not Appearing

**Issue**: QR code doesn't show up after clicking "Initialize WhatsApp"

**Solutions**:
1. Check that the WhatsApp service is running on port 3001
2. Check browser console for errors
3. Verify port 3001 is not blocked by firewall
4. Restart the WhatsApp service

### "WhatsApp service is not available" Error

**Issue**: Frontend can't connect to the WhatsApp service

**Solutions**:
1. Verify the WhatsApp service is running: `curl http://localhost:3001/health`
2. Check for port conflicts
3. Restart the service

### "Number not registered on WhatsApp"

**Issue**: Error when sending message

**Solutions**:
1. Verify the phone number format includes country code
2. Confirm the number is actually registered on WhatsApp
3. Try using the number without any special characters (+, -, spaces)

### Session Expired

**Issue**: Need to re-authenticate after some time

**Solution**: This is normal WhatsApp behavior. Simply:
1. Click "Logout" (optional)
2. Scan the QR code again to re-authenticate

### Puppeteer/Chrome Issues

**Issue**: Errors about Chrome or Chromium not found

**Solutions**:
1. The whatsapp-web.js library will automatically download Chromium
2. If it fails, you may need to install Chrome/Chromium manually
3. On Linux: `sudo apt-get install chromium-browser`

## Session Persistence

The WhatsApp session is stored in `whatsapp-service/.wwebjs_auth/` directory. This means:
- ✅ You won't need to scan QR code every time you restart
- ✅ Session persists across service restarts
- ⚠️ Don't commit this directory to git (already in .gitignore)
- ⚠️ Delete this directory if you want to log out completely

## Security Considerations

1. **Local Development Only**: This setup is designed for local development and testing
2. **Don't Expose Publicly**: Don't expose port 3001 or the WhatsApp service to the public internet
3. **Rate Limiting**: WhatsApp may limit message sending if you send too many messages
4. **Terms of Service**: Ensure your use complies with WhatsApp's Terms of Service

## Production Deployment

For production deployment:

1. **Environment Variables**: Set `WHATSAPP_SERVICE_URL` in your backend:
   ```bash
   export WHATSAPP_SERVICE_URL=http://your-whatsapp-service:3001
   ```

2. **Separate Server**: Consider running the WhatsApp service on a separate server/container

3. **Authentication**: Add authentication to protect the WhatsApp endpoints

4. **Monitoring**: Monitor the service health and session status

5. **Backup Sessions**: Consider backing up the `.wwebjs_auth` directory

## Uninstalling

To remove the WhatsApp integration:

1. Stop the WhatsApp service
2. Delete the `whatsapp-service` directory
3. Remove WhatsApp-related code from:
   - `frontend/src/components/WhatsAppPage.jsx`
   - `frontend/src/Router.jsx`
   - `backend/api/routes.py` (WhatsApp endpoints)
4. Remove `httpx` from `requirements.txt` (if not used elsewhere)

## Additional Resources

- [whatsapp-web.js Documentation](https://docs.wwebjs.dev/)
- [WhatsApp Business API](https://business.whatsapp.com/)
- [FAQ and Common Issues](https://github.com/pedroslopez/whatsapp-web.js/issues)

## Support

If you encounter issues:
1. Check the service logs in the terminal
2. Check browser console for frontend errors
3. Review the troubleshooting section above
4. Check whatsapp-web.js GitHub issues

