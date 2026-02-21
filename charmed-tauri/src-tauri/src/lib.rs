// Charmed — Rust Backend (Tauri IPC Commands)
// Application de réveil Spotify avec interface glassmorphism moderne

mod alarm;
mod spotify;
mod storage;
mod audio;

use std::sync::Mutex;
use serde::{Deserialize, Serialize};
use tauri::State;

// -- STRUCTURES DE DONNÉES --

/// Représente une alarme programmée
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlarmEntry {
    pub id: String,
    pub time: String,           // Format "HH:MM"
    pub playlist_name: String,
    pub playlist_uri: String,
    pub volume: u8,             // 0-100
    pub active: bool,
    pub days: Vec<String>,      // ["Monday", "Tuesday", ...]
    pub fade_in: bool,
    pub fade_in_duration: u16,  // Secondes
}

/// État global de l'application partagé entre tous les appels IPC
pub struct AppState {
    pub alarms: Mutex<Vec<AlarmEntry>>,
    pub spotify_client: Mutex<Option<spotify::SpotifyClient>>,
}

// -- COMMANDES IPC --

/// Retourne l'heure actuelle du système
#[tauri::command]
fn get_current_time() -> String {
    chrono::Local::now().format("%H:%M:%S").to_string()
}

/// Ajoute une nouvelle alarme
#[tauri::command]
fn set_alarm(
    app_handle: tauri::AppHandle,
    state: State<'_, AppState>,
    time: String,
    playlist_name: String,
    playlist_uri: String,
    volume: u8,
    days: Vec<String>,
    fade_in: bool,
    fade_in_duration: u16,
) -> Result<AlarmEntry, String> {
    // Valider le format de l'heure (HH:MM)
    chrono::NaiveTime::parse_from_str(&time, "%H:%M")
        .map_err(|_| "Format d'heure invalide. Utilisez HH:MM".to_string())?;

    let alarm = AlarmEntry {
        id: uuid::Uuid::new_v4().to_string(),
        time,
        playlist_name,
        playlist_uri,
        volume: volume.min(100),
        active: true,
        days,
        fade_in,
        fade_in_duration,
    };

    // Ajouter à la liste en mémoire
    let mut alarms = state.alarms.lock().map_err(|e| e.to_string())?;
    alarms.push(alarm.clone());

    // Persister sur disque
    if let Ok(app_data_dir) = app_handle.path().app_data_dir() {
        let _ = storage::save_alarms(&app_data_dir, &alarms);
    }

    Ok(alarm)
}

/// Retourne la liste de toutes les alarmes
#[tauri::command]
fn get_alarms(state: State<'_, AppState>) -> Result<Vec<AlarmEntry>, String> {
    let alarms = state.alarms.lock().map_err(|e| e.to_string())?;
    Ok(alarms.clone())
}

/// Active ou désactive une alarme
#[tauri::command]
fn toggle_alarm(
    app_handle: tauri::AppHandle,
    state: State<'_, AppState>,
    alarm_id: String,
) -> Result<bool, String> {
    let mut alarms = state.alarms.lock().map_err(|e| e.to_string())?;
    
    if let Some(alarm) = alarms.iter_mut().find(|a| a.id == alarm_id) {
        alarm.active = !alarm.active;
        let new_state = alarm.active;
        
        // Persister
        if let Ok(app_data_dir) = app_handle.path().app_data_dir() {
            let _ = storage::save_alarms(&app_data_dir, &alarms);
        }
        
        Ok(new_state)
    } else {
        Err(format!("Alarme '{}' introuvable", alarm_id))
    }
}

/// Supprime une alarme
#[tauri::command]
fn delete_alarm(
    app_handle: tauri::AppHandle,
    state: State<'_, AppState>,
    alarm_id: String,
) -> Result<(), String> {
    let mut alarms = state.alarms.lock().map_err(|e| e.to_string())?;
    let before = alarms.len();
    alarms.retain(|a| a.id != alarm_id);
    
    if alarms.len() < before {
        // Persister
        if let Ok(app_data_dir) = app_handle.path().app_data_dir() {
            let _ = storage::save_alarms(&app_data_dir, &alarms);
        }
        Ok(())
    } else {
        Err(format!("Alarme '{}' introuvable", alarm_id))
    }
}

/// Vérifie si une alarme doit sonner maintenant
#[tauri::command]
fn check_alarms(state: State<'_, AppState>) -> Result<Option<AlarmEntry>, String> {
    let now = chrono::Local::now();
    let current_time = now.format("%H:%M").to_string();
    let today = match now.weekday() {
        chrono::Weekday::Mon => "Monday",
        chrono::Weekday::Tue => "Tuesday",
        chrono::Weekday::Wed => "Wednesday",
        chrono::Weekday::Thu => "Thursday",
        chrono::Weekday::Fri => "Friday",
        chrono::Weekday::Sat => "Saturday",
        chrono::Weekday::Sun => "Sunday",
    };

    let alarms = state.alarms.lock().map_err(|e| e.to_string())?;
    for alarm in alarms.iter() {
        if alarm.active
            && alarm.time == current_time
            && (alarm.days.is_empty() || alarm.days.iter().any(|d| d == today))
        {
            return Ok(Some(alarm.clone()));
        }
    }
    Ok(None)
}

// -- COMMANDES SPOTIFY --

/// Initie l'authentification Spotify OAuth
#[tauri::command]
async fn spotify_login(
    state: State<'_, AppState>,
    client_id: String,
    client_secret: String,
) -> Result<String, String> {
    let mut client = spotify::SpotifyClient::new(client_id, client_secret);
    let auth_url = client.get_auth_url();
    
    let mut spotify_guard = state.spotify_client.lock().map_err(|e| e.to_string())?;
    *spotify_guard = Some(client);
    
    Ok(auth_url)
}

/// Complète l'authentification avec le code callback
#[tauri::command]
async fn spotify_callback(
    state: State<'_, AppState>,
    code: String,
) -> Result<(), String> {
    let mut spotify_guard = state.spotify_client.lock().map_err(|e| e.to_string())?;
    
    if let Some(client) = spotify_guard.as_mut() {
        client.complete_auth(code).await
            .map_err(|e| format!("Erreur auth Spotify: {}", e))?;
        Ok(())
    } else {
        Err("Client Spotify non initialisé".to_string())
    }
}

/// Récupère les playlists de l'utilisateur
#[tauri::command]
async fn get_spotify_playlists(
    state: State<'_, AppState>,
) -> Result<Vec<spotify::SpotifyPlaylist>, String> {
    let spotify_guard = state.spotify_client.lock().map_err(|e| e.to_string())?;
    
    if let Some(client) = spotify_guard.as_ref() {
        client.get_playlists().await
            .map_err(|e| format!("Erreur récupération playlists: {}", e))
    } else {
        Err("Non connecté à Spotify".to_string())
    }
}

/// Lance la lecture d'une playlist
#[tauri::command]
async fn play_spotify_playlist(
    state: State<'_, AppState>,
    playlist_uri: String,
) -> Result<(), String> {
    let spotify_guard = state.spotify_client.lock().map_err(|e| e.to_string())?;
    
    if let Some(client) = spotify_guard.as_ref() {
        client.play_playlist(&playlist_uri).await
            .map_err(|e| format!("Erreur lecture: {}", e))
    } else {
        Err("Non connecté à Spotify".to_string())
    }
}

/// Règle le volume Spotify
#[tauri::command]
async fn set_spotify_volume(
    state: State<'_, AppState>,
    volume: u8,
) -> Result<(), String> {
    let spotify_guard = state.spotify_client.lock().map_err(|e| e.to_string())?;
    
    if let Some(client) = spotify_guard.as_ref() {
        client.set_volume(volume).await
            .map_err(|e| format!("Erreur volume: {}", e))
    } else {
        Err("Non connecté à Spotify".to_string())
    }
}

/// Vérifie si l'utilisateur est authentifié
#[tauri::command]
fn is_spotify_authenticated(state: State<'_, AppState>) -> bool {
    if let Ok(spotify_guard) = state.spotify_client.lock() {
        if let Some(client) = spotify_guard.as_ref() {
            return client.is_authenticated();
        }
    }
    false
}

// -- COMMANDES AUDIO --

/// Joue l'alarme locale (fallback)
#[tauri::command]
fn play_local_alarm() -> Result<(), String> {
    audio::play_alarm_sound()
        .map_err(|e| format!("Erreur audio: {}", e))
}

/// Arrête l'alarme locale
#[tauri::command]
fn stop_local_alarm() -> Result<(), String> {
    audio::stop_alarm_sound()
        .map_err(|e| format!("Erreur audio: {}", e))
}

// -- POINT D'ENTRÉE PRINCIPAL --

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Charger les alarmes sauvegardées
            if let Ok(app_data_dir) = app.path().app_data_dir() {
                if let Ok(alarms) = storage::load_alarms(&app_data_dir) {
                    let state = app.state::<AppState>();
                    if let Ok(mut stored_alarms) = state.alarms.lock() {
                        *stored_alarms = alarms;
                    }
                }
            }
            Ok(())
        })
        .manage(AppState {
            alarms: Mutex::new(Vec::new()),
            spotify_client: Mutex::new(None),
        })
        .invoke_handler(tauri::generate_handler![
            get_current_time,
            set_alarm,
            get_alarms,
            toggle_alarm,
            delete_alarm,
            check_alarms,
            spotify_login,
            spotify_callback,
            get_spotify_playlists,
            play_spotify_playlist,
            set_spotify_volume,
            is_spotify_authenticated,
            play_local_alarm,
            stop_local_alarm,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}