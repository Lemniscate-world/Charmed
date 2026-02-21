# Security Policy — Charmed

## 🔒 Security Standards

This project follows strict security practices for Rust/Tauri applications.

### Code Scanning (MANDATORY)

| Scanner | Language | Command |
|---------|----------|---------|
| `cargo audit` | Rust | `cargo audit` |
| `cargo clippy` | Rust | `cargo clippy -- -D warnings` |
| `npm audit` | Node.js | `npm audit` |

### Pre-commit Hooks

Before every commit, run:
```bash
# Rust security audit
cd charmed-tauri/src-tauri && cargo audit

# Rust linter
cargo clippy -- -D warnings

# Node.js audit
cd .. && npm audit
```

## 🚨 Reporting Security Vulnerabilities

**DO NOT** open a public issue for security vulnerabilities.

Instead, please report them via:
- GitHub Security Advisories: [Report a vulnerability](https://github.com/Lemniscate-world/Charmed/security/advisories)

We will respond within 48 hours.

## 🔐 Secrets Management

### Never Commit These
- Spotify Client ID/Secret
- API tokens
- `.env` files
- Token cache files (`.cache`, `.cache-*`)

### Environment Variables (Required)
```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

Store these in a `.env` file in `charmed-tauri/` (already gitignored).

## 📋 Security Checklist

### Always
- [x] Validate user input (time format, alarm IDs)
- [x] Use environment variables for secrets
- [x] Run `cargo audit` before releases
- [x] Keep dependencies updated
- [x] Use OAuth PKCE for Spotify (no client secret in frontend)

### Never
- [ ] Hardcode API keys or secrets
- [ ] Log sensitive information
- [ ] Commit `.env` files
- [ ] Store tokens in plain text

## 🛡️ Rust Security Features

### Memory Safety
Rust provides:
- **Ownership system**: Prevents use-after-free, double-free
- **Borrowing rules**: Prevents data races
- **No null pointers**: `Option<T>` forces explicit handling

### Thread Safety
- `Mutex<T>` for shared state
- `Arc<T>` for thread-safe reference counting
- All IPC commands are thread-safe by design

### Tauri Security
- Content Security Policy (CSP) enforced
- Context isolation enabled
- No eval() in production

## 📦 Dependency Audit

### Rust Dependencies
| Crate | Purpose | Security |
|-------|---------|----------|
| `tauri` | App framework | Active maintenance |
| `rspotify` | Spotify API | OAuth PKCE |
| `rodio` | Audio playback | Pure Rust |
| `serde` | Serialization | Memory safe |

### Node.js Dependencies
| Package | Purpose | Security |
|---------|---------|----------|
| `react` | UI framework | Active maintenance |
| `tailwindcss` | Styling | No runtime |
| `lucide-react` | Icons | No external calls |

## 🔄 CI/CD Security

GitHub Actions includes:
- **CodeQL**: Static analysis for Rust and JavaScript
- **Dependency review**: Checks for vulnerable dependencies
- **Secret scanning**: Detects leaked credentials

## 📚 References

- [Rust Security Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Tauri Security](https://tauri.app/v1/guides/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)