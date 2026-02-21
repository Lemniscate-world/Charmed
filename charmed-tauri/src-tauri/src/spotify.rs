// spotify.rs - Intégration Spotify Web API via rspotify

use serde::{Deserialize, Serialize};
use rspotify::{
    model::PlaylistContext,
    prelude::*,
    AuthCodePkceSpotify, Credentials, OAuth,
};

/// Playlist Spotify avec métadonnées pour l'affichage
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpotifyPlaylist {
    pub id: String,
    pub name: String,
    pub uri: String,
    pub image_url: Option<String>,
    pub track_count: u32,
    pub owner: String,
}

/// Client Spotify avec support OAuth PKCE
pub struct SpotifyClient {
    client: Option<AuthCodePkceSpotify>,
    client_id: String,
    client_secret: String,
    authenticated: bool,
}

impl SpotifyClient {
    /// Crée un nouveau client Spotify
    pub fn new(client_id: String, client_secret: String) -> Self {
        Self {
            client: None,
            client_id,
            client_secret,
            authenticated: false,
        }
    }

    /// Génère l'URL d'authentification OAuth
    pub fn get_auth_url(&mut self) -> String {
        let oauth = OAuth {
            scopes: rspotify::scopes!(
                "user-library-read",
                "user-read-playback-state",
                "user-modify-playback-state",
                "playlist-read-private",
                "playlist-read-collaborative"
            ),
            redirect_uri: "http://localhost:8888/callback".to_string(),
            ..Default::default()
        };

        let creds = Credentials::new_pkce(&self.client_id);
        
        let mut spotify = AuthCodePkceSpotify::new(creds.clone(), oauth.clone());
        
        // Générer l'URL d'autorisation
        let url = spotify.get_authorize_url(None).unwrap_or_default();
        
        // Sauvegarder pour compléter l'auth plus tard
        self.client = Some(spotify);
        
        url
    }

    /// Complète l'authentification avec le code callback
    pub async fn complete_auth(&mut self, code: String) -> Result<(), String> {
        if let Some(ref mut spotify) = self.client {
            // Échanger le code contre un token
            spotify
                .request_token(&code)
                .await
                .map_err(|e| format!("Erreur token: {}", e))?;
            
            self.authenticated = true;
            Ok(())
        } else {
            Err("Client non initialisé".to_string())
        }
    }

    /// Vérifie si l'utilisateur est authentifié
    pub fn is_authenticated(&self) -> bool {
        self.authenticated
    }

    /// Récupère les playlists de l'utilisateur
    pub async fn get_playlists(&self) -> Result<Vec<SpotifyPlaylist>, String> {
        if let Some(ref spotify) = self.client {
            if !self.authenticated {
                return Err("Non authentifié".to_string());
            }

            let playlists = spotify
                .current_user_playlists_manual(None, None)
                .await
                .map_err(|e| format!("Erreur API: {}", e))?;

            let result: Vec<SpotifyPlaylist> = playlists
                .items
                .into_iter()
                .map(|p| SpotifyPlaylist {
                    id: p.id.to_string(),
                    name: p.name,
                    uri: p.uri.to_string(),
                    image_url: p.images.first().map(|img| img.url.clone()),
                    track_count: p.tracks.total,
                    owner: p.owner.display_name.unwrap_or_else(|| "Unknown".to_string()),
                })
                .collect();

            Ok(result)
        } else {
            Err("Client non initialisé".to_string())
        }
    }

    /// Lance la lecture d'une playlist
    pub async fn play_playlist(&self, playlist_uri: &str) -> Result<(), String> {
        if let Some(ref spotify) = self.client {
            if !self.authenticated {
                return Err("Non authentifié".to_string());
            }

            // Vérifier qu'un appareil actif existe
            let devices = spotify
                .device()
                .await
                .map_err(|e| format!("Erreur appareils: {}", e))?;

            let has_active = devices.devices.iter().any(|d| d.is_active);
            
            if !has_active {
                return Err("Aucun appareil Spotify actif. Ouvrez Spotify sur un appareil.".to_string());
            }

            // Démarrer la lecture
            spotify
                .start_context_playback(Some(PlaylistContext::Uri(playlist_uri.to_string())), None, None, None)
                .await
                .map_err(|e| format!("Erreur lecture: {}", e))?;

            Ok(())
        } else {
            Err("Client non initialisé".to_string())
        }
    }

    /// Règle le volume de lecture
    pub async fn set_volume(&self, volume_percent: u8) -> Result<(), String> {
        if let Some(ref spotify) = self.client {
            if !self.authenticated {
                return Err("Non authentifié".to_string());
            }

            let volume = volume_percent.min(100) as u8;

            spotify
                .volume(volume, None)
                .await
                .map_err(|e| format!("Erreur volume: {}", e))?;

            Ok(())
        } else {
            Err("Client non initialisé".to_string())
        }
    }

    /// Récupère les appareils disponibles
    pub async fn get_devices(&self) -> Result<Vec<SpotifyDevice>, String> {
        if let Some(ref spotify) = self.client {
            if !self.authenticated {
                return Err("Non authentifié".to_string());
            }

            let devices = spotify
                .device()
                .await
                .map_err(|e| format!("Erreur appareils: {}", e))?;

            let result: Vec<SpotifyDevice> = devices
                .devices
                .into_iter()
                .map(|d| SpotifyDevice {
                    id: d.id.unwrap_or_default(),
                    name: d.name,
                    device_type: format!("{:?}", d._type),
                    is_active: d.is_active,
                    volume_percent: d.volume_percent.unwrap_or(0) as u8,
                })
                .collect();

            Ok(result)
        } else {
            Err("Client non initialisé".to_string())
        }
    }
}

/// Appareil Spotify pour l'affichage
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpotifyDevice {
    pub id: String,
    pub name: String,
    pub device_type: String,
    pub is_active: bool,
    pub volume_percent: u8,
}