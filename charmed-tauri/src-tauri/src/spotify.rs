// spotify.rs - Integration Spotify Web API via rspotify

use serde::{Deserialize, Serialize};
use rspotify::{
    prelude::*,
    AuthCodePkceSpotify, Credentials, OAuth,
};

/// Playlist Spotify avec metadonnees pour l'affichage
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
#[derive(Clone)]
pub struct SpotifyClient {
    client: Option<AuthCodePkceSpotify>,
    client_id: String,
    authenticated: bool,
}

impl SpotifyClient {
    /// Cree un nouveau client Spotify
    pub fn new(client_id: String, _client_secret: String) -> Self {
        Self {
            client: None,
            client_id,
            authenticated: false,
        }
    }

    /// Genere l'URL d'authentification OAuth
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
        
        // Generer l'URL d'autorisation
        let url = spotify.get_authorize_url(None).unwrap_or_default();
        
        // Sauvegarder pour completer l'auth plus tard
        self.client = Some(spotify);
        
        url
    }

    /// Complete l'authentification avec le code callback
    pub async fn complete_auth(&mut self, code: String) -> Result<(), String> {
        if let Some(ref mut spotify) = self.client {
            // Echanger le code contre un token
            spotify
                .request_token(&code)
                .await
                .map_err(|e| format!("Erreur token: {}", e))?;
            
            self.authenticated = true;
            Ok(())
        } else {
            Err("Client non initialise".to_string())
        }
    }

    /// Verifie si l'utilisateur est authentifie
    pub fn is_authenticated(&self) -> bool {
        self.authenticated
    }

    /// Recupere les playlists de l'utilisateur
    pub async fn get_playlists(&self) -> Result<Vec<SpotifyPlaylist>, String> {
        if let Some(ref spotify) = self.client {
            if !self.authenticated {
                return Err("Non authentifie".to_string());
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
                    uri: format!("spotify:playlist:{}", p.id),
                    image_url: p.images.first().map(|img| img.url.clone()),
                    track_count: p.tracks.total,
                    owner: p.owner.display_name.unwrap_or_else(|| "Unknown".to_string()),
                })
                .collect();

            Ok(result)
        } else {
            Err("Client non initialise".to_string())
        }
    }

    /// Lance la lecture d'une playlist
    pub async fn play_playlist(&self, playlist_uri: &str) -> Result<(), String> {
        if let Some(ref spotify) = self.client {
            if !self.authenticated {
                return Err("Non authentifie".to_string());
            }

            // Verifier qu'un appareil actif existe
            let devices = spotify
                .device()
                .await
                .map_err(|e| format!("Erreur appareils: {}", e))?;

            let has_active = devices.iter().any(|d| d.is_active);
            
            if !has_active {
                return Err("Aucun appareil Spotify actif. Ouvrez Spotify sur un appareil.".to_string());
            }

            // Demarrer la lecture avec l'URI de contexte
            // Extraire l'ID de la playlist depuis l'URI (format: spotify:playlist:ID)
            let playlist_id = playlist_uri
                .strip_prefix("spotify:playlist:")
                .unwrap_or(&playlist_uri);
            
            let context = rspotify::model::PlayContextId::Playlist(
                rspotify::model::PlaylistId::from_id(playlist_id)
                    .map_err(|e| format!("ID playlist invalide: {:?}", e))?
            );
            
            spotify
                .start_context_playback(context, None, None, None)
                .await
                .map_err(|e| format!("Erreur lecture: {}", e))?;

            Ok(())
        } else {
            Err("Client non initialise".to_string())
        }
    }

    /// Regle le volume de lecture
    pub async fn set_volume(&self, volume_percent: u8) -> Result<(), String> {
        if let Some(ref spotify) = self.client {
            if !self.authenticated {
                return Err("Non authentifie".to_string());
            }

            let volume = volume_percent.min(100) as u8;

            spotify
                .volume(volume, None)
                .await
                .map_err(|e| format!("Erreur volume: {}", e))?;

            Ok(())
        } else {
            Err("Client non initialise".to_string())
        }
    }

    /// Recupere les appareils disponibles
    pub async fn get_devices(&self) -> Result<Vec<SpotifyDevice>, String> {
        if let Some(ref spotify) = self.client {
            if !self.authenticated {
                return Err("Non authentifie".to_string());
            }

            let devices = spotify
                .device()
                .await
                .map_err(|e| format!("Erreur appareils: {}", e))?;

            let result: Vec<SpotifyDevice> = devices
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
            Err("Client non initialise".to_string())
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