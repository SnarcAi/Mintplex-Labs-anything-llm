# MissYak Social - Mobile App

React Native mobile application for MissYak Social platform.

---

## 📱 Overview

Mobile-first social app for grilling culture, built with:
- **React Native** via Expo
- **TypeScript** for type safety
- **React Navigation** for routing
- **LiveKit** for video streaming
- **Axios** for API communication

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- iOS Simulator (Mac only) or Android Studio
- Expo Go app on your phone (for quick testing)

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. Configure Backend URL

Edit `src/services/api.ts`:

```typescript
const API_BASE_URL = __DEV__
  ? 'http://YOUR_LOCAL_IP:8000/api/v1'  // Change this!
  : 'https://api.missyak.com/api/v1';
```

**Important**: Use your computer's local IP (not `localhost`) for physical devices.

Find your IP:
```bash
# Mac/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

### 3. Start Development Server

```bash
npm start
```

This opens Expo Dev Tools. You can:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app on your phone

### 4. Run on Specific Platform

```bash
# iOS (Mac only)
npm run ios

# Android
npm run android

# Web (experimental)
npm run web
```

---

## 📂 Project Structure

```
mobile/
├── src/
│   ├── screens/          # All app screens
│   │   ├── auth/         # Login, Register
│   │   ├── home/         # Home feed
│   │   ├── live/         # Live rooms
│   │   ├── recipes/      # Recipe feed
│   │   ├── shop/         # Product catalog
│   │   └── profile/      # User profile
│   ├── navigation/       # React Navigation setup
│   ├── services/         # API client
│   ├── utils/            # Auth context, helpers
│   ├── types/            # TypeScript types
│   └── components/       # Reusable components (future)
├── App.tsx               # App entry point
├── app.json              # Expo configuration
├── package.json          # Dependencies
└── tsconfig.json         # TypeScript config
```

---

## 🎨 Screens

### Authentication
- **LoginScreen** - Email/password login
- **RegisterScreen** - User registration with grill level selection

### Main Tabs
- **HomeScreen** - Live rooms + latest recipes feed
- **LiveScreen** - List of active live rooms + create button
- **RecipesScreen** - Recipe feed with latest/top toggle
- **ShopScreen** - Product catalog with category filters

### Detail Screens
- **RoomScreen** - Live video room with chat
- **CreateRoomScreen** - Create new live room
- **RecipeDetailScreen** - Recipe details with like button
- **CreateRecipeScreen** - Post new recipe
- **ProductDetailScreen** - Product details with buy button
- **ProfileScreen** - User profile and settings

---

## 🔐 Authentication Flow

1. App starts → `AuthContext` checks for stored token
2. If token exists → call `/api/v1/auth/me` to validate
3. If valid → show main app (tabs)
4. If invalid → show login screen
5. After login/register → store token → show main app

Token is stored in AsyncStorage and automatically included in all API requests.

---

## 📹 LiveKit Integration

### Setup

The app uses `@livekit/react-native` for video streaming.

**V1 Note**: Video component is a placeholder. To fully implement:

1. Install LiveKit dependencies:
   ```bash
   npm install @livekit/react-native @livekit/react-native-webrtc
   ```

2. Follow setup guide:
   https://docs.livekit.io/guides/react-native/

3. Replace placeholder in `RoomScreen.tsx` with:
   ```tsx
   import { LiveKitRoom, VideoTrack } from '@livekit/react-native';

   <LiveKitRoom
     serverUrl={token.ws_url}
     token={token.token}
     audio={isHost}
     video={isHost}
   >
     {/* Video tracks */}
   </LiveKitRoom>
   ```

---

## 🎨 Styling

The app uses StyleSheet for styling with a dark theme:

**Colors**:
- Background: `#1a1a1a`
- Secondary: `#2a2a2a`
- Primary (Orange): `#ff6b35`
- Text: `#fff`, `#888`, `#aaa`

All styles are inline in each screen for V1 simplicity. Consider moving to a theme provider in V2.

---

## 🧪 Testing

```bash
# Type checking
npx tsc --noEmit

# Run tests (when implemented)
npm test

# Lint
npx eslint .
```

---

## 📦 Building for Production

### Using EAS (Expo Application Services)

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure project
eas build:configure

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

### Manual Build (Advanced)

```bash
# Prebuild native code
npx expo prebuild

# Build Android APK
cd android
./gradlew assembleRelease

# Build iOS (Mac only)
cd ios
xcodebuild -workspace MissYakSocial.xcworkspace -scheme MissYakSocial -configuration Release
```

---

## 🔧 Configuration

### app.json

Key settings:
```json
{
  "expo": {
    "name": "MissYak Social",
    "slug": "missyak-social",
    "version": "1.0.0",
    "orientation": "portrait",
    "ios": {
      "bundleIdentifier": "com.missyak.social"
    },
    "android": {
      "package": "com.missyak.social",
      "permissions": [
        "CAMERA",
        "RECORD_AUDIO",
        "READ_EXTERNAL_STORAGE"
      ]
    }
  }
}
```

---

## 📸 Image Uploads (Future)

For V1, recipes use image URLs. To implement uploads:

1. Install image picker:
   ```bash
   npx expo install expo-image-picker
   ```

2. Add upload endpoint to backend
3. Update `CreateRecipeScreen.tsx`:
   ```tsx
   import * as ImagePicker from 'expo-image-picker';

   const pickImage = async () => {
     const result = await ImagePicker.launchImageLibraryAsync({
       mediaTypes: ImagePicker.MediaTypeOptions.Images,
       quality: 0.8,
     });

     if (!result.canceled) {
       // Upload to backend
       const formData = new FormData();
       formData.append('file', {
         uri: result.assets[0].uri,
         type: 'image/jpeg',
         name: 'photo.jpg',
       });

       const response = await api.uploadImage(formData);
       setImageUrl(response.url);
     }
   };
   ```

---

## 🐛 Troubleshooting

### Cannot connect to backend

```bash
# Make sure backend is running
curl http://localhost:8000/health

# Check API_BASE_URL in src/services/api.ts
# Use computer's local IP, not localhost!

# For Android emulator, use:
# http://10.0.2.2:8000/api/v1

# For iOS simulator, use:
# http://localhost:8000/api/v1
```

### Expo errors

```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
npx expo start --clear
```

### Build errors

```bash
# Update dependencies
npx expo install --fix

# Check compatibility
npx expo-doctor
```

---

## 📱 Platform-Specific Notes

### iOS

- Requires Xcode on Mac
- Test with iOS Simulator (free)
- Publishing requires Apple Developer account ($99/year)

### Android

- Works on any platform
- Test with Android Studio emulator (free)
- Publishing to Play Store requires one-time $25 fee

---

## 🎯 Next Steps for V2

- [ ] Implement actual LiveKit video streaming
- [ ] Add image upload for recipes/avatars
- [ ] Implement WebSocket for real-time chat
- [ ] Add push notifications
- [ ] Improve error handling
- [ ] Add loading states
- [ ] Implement pagination for feeds
- [ ] Add pull-to-refresh everywhere
- [ ] Create reusable component library
- [ ] Add unit tests
- [ ] Improve accessibility

---

## 📖 Resources

- [Expo Documentation](https://docs.expo.dev/)
- [React Native](https://reactnative.dev/)
- [React Navigation](https://reactnavigation.org/)
- [LiveKit React Native](https://docs.livekit.io/guides/react-native/)
- [TypeScript](https://www.typescriptlang.org/)

---

**Questions? Check the main [README](../README.md) or create an issue.**
