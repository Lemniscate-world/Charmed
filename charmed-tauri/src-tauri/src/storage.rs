// storage.rs - Persistance des données (alarmes, configuration)

use std::fs;
use std::path::Path;
use serde::{Deserialize, Serialize};

use crate::AlarmEntry;

const ALARMS_FILE: &str = "alarms.json";

/// Sauvegarde les alarmes dans un fichier JSON
pub fn save_alarms(data_dir: &Path, alarms: &[AlarmEntry]) -> Result<(), String> {
    // Créer le dossier de données si nécessaire
    if !data_dir.exists() {
        fs::create_dir_all(data_dir)
            .map_err(|e| format!("Impossible de créer le dossier: {}", e))?;
    }

    let file_path = data_dir.join(ALARMS_FILE);
    let json = serde_json::to_string_pretty(alarms)
        .map_err(|e| format!("Erreur sérialisation: {}", e))?;
    
    fs::write(&file_path, json)
        .map_err(|e| format!("Erreur écriture fichier: {}", e))?;
    
    Ok(())
}

/// Charge les alarmes depuis le fichier JSON
pub fn load_alarms(data_dir: &Path) -> Result<Vec<AlarmEntry>, String> {
    let file_path = data_dir.join(ALARMS_FILE);
    
    if !file_path.exists() {
        return Ok(Vec::new());
    }

    let content = fs::read_to_string(&file_path)
        .map_err(|e| format!("Erreur lecture fichier: {}", e))?;
    
    let alarms: Vec<AlarmEntry> = serde_json::from_str(&content)
        .map_err(|e| format!("Erreur désérialisation: {}", e))?;
    
    Ok(alarms)
}

/// Configuration de l'application
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub spotify_client_id: Option<String>,
    pub spotify_client_secret: Option<String>,
    pub spotify_redirect_uri: String,
    pub default_volume: u8,
    pub default_fade_in_duration: u16,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            spotify_client_id: None,
            spotify_client_secret: None,
            spotify_redirect_uri: "http://localhost:8888/callback".to_string(),
            default_volume: 80,
            default_fade_in_duration: 300, // 5 minutes
        }
    }
}

const CONFIG_FILE: &str = "config.json";

/// Sauvegarde la configuration
pub fn save_config(data_dir: &Path, config: &AppConfig) -> Result<(), String> {
    if !data_dir.exists() {
        fs::create_dir_all(data_dir)
            .map_err(|e| format!("Impossible de créer le dossier: {}", e))?;
    }

    let file_path = data_dir.join(CONFIG_FILE);
    let json = serde_json::to_string_pretty(config)
        .map_err(|e| format!("Erreur sérialisation: {}", e))?;
    
    fs::write(&file_path, json)
        .map_err(|e| format!("Erreur écriture fichier: {}", e))?;
    
    Ok(())
}

/// Charge la configuration
pub fn load_config(data_dir: &Path) -> Result<AppConfig, String> {
    let file_path = data_dir.join(CONFIG_FILE);
    
    if !file_path.exists() {
        return Ok(AppConfig::default());
    }

    let content = fs::read_to_string(&file_path)
        .map_err(|e| format!("Erreur lecture fichier: {}", e))?;
    
    let config: AppConfig = serde_json::from_str(&content)
        .unwrap_or_else(|_| AppConfig::default());
    
    Ok(config)
}