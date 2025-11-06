# WhatsApp Integration on Railway

This guide explains how to deploy the WhatsApp integration to Railway.

## 🚀 Quick Setup

The Dockerfile now includes WhatsApp service by default. No extra configuration needed!

### Deploy to Railway

1. **Push your code to GitHub:**
```bash
git add .
git commit -m "Add WhatsApp integration"
git push
```

2. **Railway will automatically:**
   - Build the Docker image (includes WhatsApp)
   - Install Chromium and dependencies
   - Start both backend (port 8000) and WhatsApp service (port 3001)

3. **Configure WhatsApp** (one-time setup):
   - Visit `https://your-app.railway.app/whatsapp`
   - Scan the QR code with your phone
   - Session will persist across container restarts (stored in volume)

## 🎛️ Environment Variables

### ENABLE_WHATSAPP

Control whether the WhatsApp service starts:

```bash
ENABLE_WHATSAPP=true   # Default - WhatsApp enabled
ENABLE_WHATSAPP=false  # Disable WhatsApp (saves ~500MB RAM)
```

**To disable in Railway:**
1. Go to your project → Variables
2. Add variable: `ENABLE_WHATSAPP` = `false`
3. Redeploy

## 📱 Production Usage

### First-Time Setup

1. **Access WhatsApp Page:**
   ```
   https://your-app.railway.app/whatsapp
   ```

2. **Scan QR Code:**
   - Open WhatsApp on your phone
   - Go to Settings → Linked Devices
   - Tap "Link a Device"
   - Scan the QR code

3. **Session Persistence:**
   - Session data is stored in `/app/whatsapp-service/.wwebjs_auth/`
   - Persists across container restarts
   - May need to re-scan after ~2 weeks of inactivity

### Sending Messages

Once authenticated, you can:
- Use the `/whatsapp` page to send test messages
- Call the API endpoints to send notifications:

```bash
curl -X POST https://your-app.railway.app/api/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "15551234567",
    "message": "Hello from Beach Volleyball ELO!"
  }'
```

## 🔒 Security Considerations

### Production Recommendations

1. **Add Authentication:**
   - Protect `/whatsapp` page with login
   - Add API key validation for send endpoints

2. **Rate Limiting:**
   - WhatsApp may ban accounts that spam
   - Add rate limiting to prevent abuse

3. **Session Management:**
   - Monitor session health
   - Set up alerts for disconnections
   - Have a re-authentication workflow

## 📊 Resource Usage

### With WhatsApp Enabled

- **Disk:** +500MB (Chromium + dependencies)
- **RAM:** +200-300MB (when active)
- **Startup:** +10-15 seconds (Chromium initialization)

### Without WhatsApp

Set `ENABLE_WHATSAPP=false` to save resources.

## 🐛 Troubleshooting

### QR Code Not Appearing

**Symptoms:** `/whatsapp` page shows "Initializing..." forever

**Solutions:**
1. Check Railway logs for errors
2. Ensure `ENABLE_WHATSAPP=true`
3. Verify Chromium installed correctly
4. Restart the service

**Check logs:**
```bash
railway logs
```

Look for:
```
📱 Starting WhatsApp service on port 3001...
✅ WhatsApp service started
```

### Session Expired

**Symptoms:** Need to re-scan QR code after restart

**Solutions:**
1. This is normal WhatsApp behavior
2. Sessions typically last 2 weeks
3. Consider setting up session monitoring
4. Log back in via `/whatsapp` page

### Connection Errors

**Symptoms:** "WhatsApp service not available" errors

**Solutions:**
1. Verify service is running: `railway logs`
2. Check `ENABLE_WHATSAPP` is set to `true`
3. Ensure port 3001 is accessible internally
4. Restart deployment

### Memory Issues

**Symptoms:** Container crashes or restarts

**Solutions:**
1. Upgrade Railway plan for more RAM
2. Disable WhatsApp: `ENABLE_WHATSAPP=false`
3. Monitor usage in Railway dashboard

## 🔧 Advanced Configuration

### Custom WhatsApp Service URL

If running WhatsApp on a separate server:

```bash
WHATSAPP_SERVICE_URL=https://whatsapp-service.example.com
```

Default: `http://localhost:3001`

### Persistent Storage

Railway provides ephemeral storage by default. For production:

1. **Add Volume:**
   - Go to Railway → Your service → Settings
   - Add a volume mounted at `/app/whatsapp-service/.wwebjs_auth`
   - This persists session data across deployments

2. **Alternative:** Use Redis/Database
   - Store session data externally
   - Requires modifying `whatsapp-service/server.js`

## 📈 Monitoring

### Health Checks

Check if WhatsApp service is running:

```bash
curl https://your-app.railway.app/api/whatsapp/status
```

Response:
```json
{
  "isReady": true,
  "isAuthenticating": false,
  "hasQrCode": false,
  "clientInfo": {
    "pushname": "Your Name",
    "phone": "15551234567",
    "platform": "android"
  }
}
```

### Automated Monitoring

Set up a cron job or monitoring service:

```bash
# Check every 5 minutes
*/5 * * * * curl https://your-app.railway.app/api/whatsapp/status
```

## 🚨 Important Notes

1. **WhatsApp Terms:** Ensure compliance with WhatsApp's Terms of Service
2. **Business Account:** Consider WhatsApp Business API for official use
3. **Backup Sessions:** Export `.wwebjs_auth/` periodically
4. **Rate Limits:** Don't send too many messages (risk of ban)
5. **Privacy:** Only send messages to users who opted in

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [WhatsApp Web.js Docs](https://docs.wwebjs.dev/)
- [WhatsApp Business API](https://business.whatsapp.com/)

## 🆘 Support

If you encounter issues:

1. Check Railway logs: `railway logs`
2. Review [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)
3. Check [whatsapp-web.js issues](https://github.com/pedroslopez/whatsapp-web.js/issues)
4. Verify environment variables in Railway dashboard

## 🎉 Example Use Cases

Once deployed, you can:

- ✅ Send match result notifications
- ✅ Send weekly ranking updates
- ✅ Notify players about upcoming games
- ✅ Send tournament announcements
- ✅ Automated reminders

All from a production environment! 🚀

