# Plan de Migration : Charmed vers Tauri (Rust + React)

## Prérequis Système (À faire ensemble)
Pour compiler une application Tauri, nous aurons besoin d'installer deux choses fondamentales sur votre machine (Linux) :
1. **Rust** : Le langage et son compilateur (via l'outil `rustup`).
2. **Node.js** : Pour compiler l'interface React (via `npx` / `npm`).

> [!IMPORTANT]
> Actuellement, la commande `rustc` n'est pas installée sur votre système. Voulez-vous que je lance l'installation de Rust (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`) et de Node.js pour préparer le terrain ?

---

## 🏗️ Architecture du Nouveau Projet

Nous allons créer un nouveau dossier propre pour l'application Tauri, tout en gardant l'ancien code Python sous les yeux pour le traduire.

### Phase 1 : Initialisation
1. Création de la coquille Tauri (`npm create tauri-app@latest`).
2. Configuration de **React** avec **TailwindCSS** (pour le design *Charm*).

### Phase 2 : Le Frontend (La Vue)
1. Création des composants React (Boutons, Horloge, Formulaire Spotify).
2. Implémentation du *Glassmorphism* et des animations fluides.
3. Simulation de l'interface sans logique métier.

### Phase 3 : Le Backend (Rust remplace Python)
1. **`alarm.py` -> `alarm.rs`** : Traduction du système d'attente et du déclenchement sonore. (Nous utiliserons la librairie audio native de Rust : `rodio`).
2. **`spotify_api.py` -> `spotify.rs`** : Refonte des requêtes HTTP vers l'API Spotify (avec la librairie `reqwest`).
3. Création des commandes **IPC** (les fonctions Rust annotées avec `#[tauri::command]` que React pourra appeler).

---

## Verification Plan
- **Mocking** : Nous testerons d'abord l'interface avec de fausses données.
- **Compilation** : Nous vérifierons que `cargo tauri dev` lance bien l'application sur votre Linux.
- **Sécurité** : Le code Rust étant sécurisé par nature (Safe Memory), nous n'aurons plus besoin de `bandit`, mais nous utiliserons `cargo audit`.
