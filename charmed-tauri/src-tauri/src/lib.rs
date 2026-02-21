// Charmed — Rust Backend (IPC Commands)
// Ce fichier contient toutes les commandes que React peut appeler via invoke().
// Chaque fonction annotée #[tauri::command] est un "point d'entrée IPC".

use std::sync::Mutex;
use chrono::{NaiveTime, Local, Weekday, Datelike};
use serde::{Deserialize, Serialize};
use tauri::State;

// -- STRUCTURES DE DONNÉES (Les "structs" dont on parlait !) --

/// Représente une alarme programmée.
/// En Rust, `derive` génère automatiquement le code pour sérialiser/désérialiser en JSON.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlarmEntry {
    pub id: String,
    pub time: String,         // Format "HH:MM"
    pub playlist_name: String,
    pub playlist_uri: String,
    pub volume: u8,           // 0-100 (u8 = unsigned 8-bit integer, max 255)
    pub active: bool,
    pub days: Vec<String>,    // Ex: ["Monday", "Tuesday"]
    pub fade_in: bool,
    pub fade_in_duration: u16,
}

/// L'état global de l'application, partagé entre tous les appels IPC.
/// Le `Mutex` est un verrou qui empêche deux threads de modifier la liste en même temps.
/// C'est l'équivalent Rust du concept "thread-safe" (sécurité multi-tâches).
pub struct AppState {
    pub alarms: Mutex<Vec<AlarmEntry>>,
}

// -- COMMANDES IPC (Les fonctions que React appelle) --

/// Retourne l'heure actuelle du système.
/// React appelle: invoke("get_current_time")
#[tauri::command]
fn get_current_time() -> String {
    Local::now().format("%H:%M:%S").to_string()
}

/// Ajoute une nouvelle alarme à la liste.
/// React appelle: invoke("set_alarm", { time: "08:00", playlistName: "Morning", ... })
#[tauri::command]
fn set_alarm(
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
    NaiveTime::parse_from_str(&time, "%H:%M")
        .map_err(|_| "Format d'heure invalide. Utilisez HH:MM".to_string())?;

    let alarm = AlarmEntry {
        id: format!("alarm_{}", chrono::Utc::now().timestamp_millis()),
        time,
        playlist_name,
        playlist_uri,
        volume: volume.min(100), // Assure que le volume ne dépasse pas 100
        active: true,
        days,
        fade_in,
        fade_in_duration,
    };

    // Verrouiller le Mutex pour écrire dans la liste partagée
    let mut alarms = state.alarms.lock().map_err(|e| e.to_string())?;
    alarms.push(alarm.clone());

    Ok(alarm)
}

/// Retourne la liste de toutes les alarmes.
/// React appelle: invoke("get_alarms")
#[tauri::command]
fn get_alarms(state: State<'_, AppState>) -> Result<Vec<AlarmEntry>, String> {
    let alarms = state.alarms.lock().map_err(|e| e.to_string())?;
    Ok(alarms.clone())
}

/// Active ou désactive une alarme par son ID.
/// React appelle: invoke("toggle_alarm", { alarmId: "alarm_123" })
#[tauri::command]
fn toggle_alarm(state: State<'_, AppState>, alarm_id: String) -> Result<bool, String> {
    let mut alarms = state.alarms.lock().map_err(|e| e.to_string())?;
    if let Some(alarm) = alarms.iter_mut().find(|a| a.id == alarm_id) {
        alarm.active = !alarm.active;
        Ok(alarm.active)
    } else {
        Err(format!("Alarme '{}' introuvable", alarm_id))
    }
}

/// Supprime une alarme par son ID.
/// React appelle: invoke("delete_alarm", { alarmId: "alarm_123" })
#[tauri::command]
fn delete_alarm(state: State<'_, AppState>, alarm_id: String) -> Result<(), String> {
    let mut alarms = state.alarms.lock().map_err(|e| e.to_string())?;
    let before = alarms.len();
    alarms.retain(|a| a.id != alarm_id);
    if alarms.len() < before {
        Ok(())
    } else {
        Err(format!("Alarme '{}' introuvable", alarm_id))
    }
}

/// Vérifie si une alarme doit sonner maintenant.
/// React appelle: invoke("check_alarms")
#[tauri::command]
fn check_alarms(state: State<'_, AppState>) -> Result<Option<AlarmEntry>, String> {
    let now = Local::now();
    let current_time = now.format("%H:%M").to_string();
    let today = match now.weekday() {
        Weekday::Mon => "Monday",
        Weekday::Tue => "Tuesday",
        Weekday::Wed => "Wednesday",
        Weekday::Thu => "Thursday",
        Weekday::Fri => "Friday",
        Weekday::Sat => "Saturday",
        Weekday::Sun => "Sunday",
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

// -- POINT D'ENTRÉE PRINCIPAL --

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        // On enregistre l'état global (la liste d'alarmes) dans Tauri
        .manage(AppState {
            alarms: Mutex::new(Vec::new()),
        })
        // On enregistre TOUTES les commandes IPC ici
        .invoke_handler(tauri::generate_handler![
            get_current_time,
            set_alarm,
            get_alarms,
            toggle_alarm,
            delete_alarm,
            check_alarms,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
