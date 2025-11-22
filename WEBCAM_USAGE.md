# Webcam Usage Guide

## 🌿 Plant Disease Detection with Webcam

The Plant Health Scanner now supports **webcam capture** for easy, real-time plant scanning!

## How to Use Webcam

### From Dashboard
1. Go to the **Plant Health Scanner** section
2. Click **"📹 Use Webcam"** button
3. Allow camera permissions when prompted
4. Position your plant in front of the camera
5. Click **"📸 Capture Photo"** to take a picture
6. Click **"🔍 Scan for Diseases"** to analyze

### From Advanced Scanner Page
1. Visit `/plant-scan` page
2. Click **"📹 Use Webcam"** button
3. Allow camera permissions
4. Capture and scan your plant

## Browser Permissions

### First Time Use
- Your browser will ask for camera permission
- Click **"Allow"** to enable webcam access
- The permission is remembered for future visits

### If Permission is Denied
1. Check browser settings
2. Look for camera/microphone permissions
3. Allow access for `localhost` or your domain
4. Refresh the page and try again

## Supported Browsers

✅ **Chrome/Edge** (Recommended)
✅ **Firefox**
✅ **Safari** (macOS/iOS)
✅ **Opera**
❌ Internet Explorer (not supported)

## Mobile Devices

### Android
- Uses back camera by default (better quality)
- Tap to focus before capturing
- Ensure good lighting

### iOS (iPhone/iPad)
- Uses back camera by default
- Safari browser required
- May need to enable camera in Settings

## Tips for Best Results

### 📸 Camera Setup
- **Good Lighting**: Natural light works best
- **Stable Position**: Hold camera steady or use a stand
- **Focus**: Tap to focus on the plant
- **Distance**: 30-50cm from plant is ideal
- **Angle**: Capture leaves and stems clearly

### 🌿 Plant Positioning
- Show affected areas clearly
- Include both healthy and unhealthy parts
- Capture multiple angles if needed
- Remove background distractions

### 🔍 Scanning Tips
- Capture high-resolution images
- Ensure plant fills most of the frame
- Avoid shadows and reflections
- Clean camera lens before use

## Troubleshooting

### Webcam Not Working?

1. **Check Permissions**
   - Browser settings → Privacy → Camera
   - Allow access for localhost

2. **Check Camera Availability**
   - Make sure no other app is using the camera
   - Close other video apps (Zoom, Teams, etc.)

3. **Try Different Browser**
   - Chrome/Edge usually work best
   - Some browsers have stricter permissions

4. **Check Camera Hardware**
   - Ensure camera is connected (for external cameras)
   - Test camera in another app first

### Error Messages

**"Could not access webcam"**
- Check browser permissions
- Close other apps using camera
- Try refreshing the page

**"Webcam is not supported"**
- Update your browser
- Use Chrome, Edge, or Firefox
- Check if device has a camera

**"Permission denied"**
- Go to browser settings
- Allow camera access
- Refresh page

## Privacy & Security

- ✅ Camera access is **local only** (no data sent to servers)
- ✅ Images processed on your device
- ✅ No video recording (only photos)
- ✅ You control when to capture
- ✅ Can stop camera anytime

## Features

### Real-time Preview
- See live camera feed
- Adjust position before capturing
- Preview before scanning

### Capture Options
- **Capture Photo**: Takes a snapshot
- **Stop Camera**: Closes camera feed
- **Clear Image**: Removes captured image

### Camera Controls
- Automatic focus
- Adjustable resolution
- Back camera on mobile (better quality)

## Alternative: File Upload

If webcam doesn't work, you can still:
- Upload images from your device
- Drag & drop image files
- Use photos from gallery

## Need Help?

If webcam still doesn't work:
1. Use the **Upload Image** option instead
2. Take photo with phone camera
3. Transfer to computer and upload
4. Or use drag & drop feature

---

**Note**: Webcam requires HTTPS in production. For localhost development, HTTP works fine.

