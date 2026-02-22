# Charmed - Premium Spotify Alarm Clock

A modern, cross-platform Spotify alarm clock built with **Tauri (Rust + React)** featuring a stunning glassmorphism UI.

[![Build Status](https://img.shields.io/github/actions/workflow/status/Lemniscate-world/Charmed/build.yml?branch=main&label=build&logo=github)](https://github.com/Lemniscate-world/Charmed/actions/workflows/build.yml)
[![Test Coverage](https://img.shields.io/badge/coverage-64%25-brightgreen?logo=vitest)](./charmed-tauri/coverage)
[![Version](https://img.shields.io/github/package-json/v/Lemniscate-world/Charmed?filename=charmed-tauri%2Fpackage.json&logo=tauri)](https://github.com/Lemniscate-world/Charmed/releases)
[![License](https://img.shields.io/github/license/Lemniscate-world/Charmed?color=green)](./LICENSE)
[![Rust](https://img.shields.io/badge/Rust-1.93+-orange?logo=rust)](https://www.rust-lang.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?logo=typescript)](https://www.typescriptlang.org/)

## ✨ Features

- 🎵 **Spotify Integration** - Wake up to your favorite playlists
- ⏰ **Smart Alarms** - Schedule multiple alarms with custom settings
- 🎨 **Premium UI** - Glassmorphism design with smooth animations
- 🔔 **Local Fallback** - Built-in alarm sound when Spotify is unavailable
- 💾 **Persistent Storage** - Alarms saved locally, survive app restarts
- 🚀 **Lightweight** - Native performance with Tauri (no Electron bloat)
- 🔒 **Secure** - OAuth 2.0 authentication, credentials stored securely

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + TypeScript + TailwindCSS |
| Backend | Rust (Tauri 2.0) |
| Audio | rodio (Rust audio library) |
| Spotify API | rspotify |
| Build | Vite |

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Rust** (via [rustup](https://rustup.rs/))
- **Spotify Premium** account (for playback control)
- **Spotify Developer App** credentials

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/Lemniscate-world/Charmed.git
cd Charmed/charmed-tauri
npm install
```

### 2. Configure Spotify Credentials

Create a `.env` file in `charmed-tauri/`:

```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

Get credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

### 3. Run Development Build

```bash
npm run tauri dev
```

### 4. Build for Production

```bash
npm run tauri build
```

Outputs:
- Windows: `.msi` installer and `.exe` (NSIS) in `src-tauri/target/release/bundle/`

## 📁 Project Structure

```
charmed-tauri/
├── src/                    # React frontend
│   ├── App.tsx             # Main application component
│   ├── index.css           # TailwindCSS + glassmorphism styles
│   └── main.tsx            # React entry point
├── src-tauri/              # Rust backend
│   ├── src/
│   │   ├── lib.rs          # IPC commands (alarm CRUD, time, etc.)
│   │   └── main.rs         # Tauri entry point
│   ├── Cargo.toml          # Rust dependencies
│   └── tauri.conf.json     # Tauri configuration
├── package.json
└── vite.config.ts
```

## 🎯 Roadmap

### Phase 1: Core (Current)
- [x] Basic alarm CRUD operations
- [x] Time display and alarm checking
- [x] Glassmorphism UI
- [ ] Spotify OAuth integration
- [ ] Spotify playback control
- [ ] Alarm persistence (JSON file)

### Phase 2: Enhancement
- [ ] Fade-in volume control
- [ ] Repeat days (Mon-Fri, weekends, etc.)
- [ ] Snooze functionality
- [ ] System tray integration
- [ ] Auto-start on boot

### Phase 3: Polish
- [ ] Multi-platform builds (macOS, Linux)
- [ ] Auto-update mechanism
- [ ] Custom alarm sounds
- [ ] Sleep timer

## 🔧 Development

### Available Scripts

```bash
# Development server with hot reload
npm run tauri dev

# Build production release
npm run tauri build

# Lint frontend
npm run lint

# Check Rust code
cargo clippy --manifest-path=charmed-tauri/src-tauri/Cargo.toml
```

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│              React Frontend                  │
│  (App.tsx, components, TailwindCSS)         │
└─────────────────┬───────────────────────────┘
                  │ invoke() - Tauri IPC
┌─────────────────▼───────────────────────────┐
│              Rust Backend                    │
│  (lib.rs: alarm logic, time, Spotify API)   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Native OS Integration               │
│  (Audio, File System, Network)              │
└─────────────────────────────────────────────┘
```

## 🧪 Testing

```bash
# Run Rust tests
cd charmed-tauri/src-tauri
cargo test

# Run frontend type check
cd charmed-tauri
npm run typecheck
```

## 📖 Documentation

- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](security.md)
- [AI Guidelines](AI_GUIDELINES.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Tauri](https://tauri.app/) - Build smaller, faster apps
- [Spotify Web API](https://developer.spotify.com/)
- [rspotify](https://github.com/ramsayleung/rspotify) - Rust Spotify wrapper
- [Lucide Icons](https://lucide.dev/) - Beautiful icons

---

Made with ❤️ by [Lemniscate](https://github.com/Lemniscate-world)