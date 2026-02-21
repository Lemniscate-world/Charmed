// audio.rs - Lecture audio locale (alarme fallback)

use rodio::{Decoder, OutputStream, OutputStreamHandle, Sink};
use std::io::Cursor;
use std::sync::Mutex;

/// État audio global pour le contrôle de lecture
static AUDIO_STATE: Mutex<Option<AudioState>> = Mutex::new(None);

struct AudioState {
    _stream: OutputStream,
    _stream_handle: OutputStreamHandle,
    sink: Sink,
}

/// Son d'alarme intégré (généré programmatiquement - beep simple)
/// En production, on utiliserait un fichier MP3 intégré dans les ressources
const ALARM_SOUND_BYTES: &[u8] = include_bytes!("../icons/icon.png");

/// Joue le son d'alarme local
pub fn play_alarm_sound() -> Result<(), String> {
    let mut state_guard = AUDIO_STATE
        .lock()
        .map_err(|_| "Impossible de verrouiller l'état audio")?;

    // Arrêter le son existant si présent
    if let Some(ref mut state) = *state_guard {
        state.sink.stop();
    }

    // Créer un nouveau flux audio
    let (_stream, _stream_handle) = OutputStream::try_default()
        .map_err(|e| format!("Impossible d'ouvrir le flux audio: {}", e))?;

    let sink = Sink::try_new(&_stream_handle)
        .map_err(|e| format!("Impossible de créer le sink audio: {}", e))?;

    // Pour l'instant, on génère un beep simple
    // Note: rodio peut jouer des fichiers MP3, WAV, OGG, FLAC
    // On génère un son de beep avec une source
    let source = rodio::source::SineWave::new(440.0); // 440 Hz = A4
    let source = rodio::source::Amplify::new(source, 0.5);
    let source = rodio::source::Repeat::new(source).take_duration(std::time::Duration::from_secs(30));
    
    sink.append(source);
    sink.set_volume(0.8);
    sink.play();

    *state_guard = Some(AudioState {
        _stream,
        _stream_handle,
        sink,
    });

    Ok(())
}

/// Arrête le son d'alarme
pub fn stop_alarm_sound() -> Result<(), String> {
    let mut state_guard = AUDIO_STATE
        .lock()
        .map_err(|_| "Impossible de verrouiller l'état audio")?;

    if let Some(ref mut state) = *state_guard {
        state.sink.stop();
    }
    
    *state_guard = None;

    Ok(())
}

/// Règle le volume de l'alarme locale (0-100)
pub fn set_alarm_volume(volume_percent: u8) -> Result<(), String> {
    let mut state_guard = AUDIO_STATE
        .lock()
        .map_err(|_| "Impossible de verrouiller l'état audio")?;

    if let Some(ref mut state) = *state_guard {
        let volume = (volume_percent.min(100) as f32) / 100.0;
        state.sink.set_volume(volume);
    }

    Ok(())
}

/// Vérifie si l'alarme est en cours de lecture
pub fn is_playing() -> bool {
    if let Ok(state_guard) = AUDIO_STATE.lock() {
        if let Some(ref state) = *state_guard {
            return !state.sink.is_paused() && !state.sink.empty();
        }
    }
    false
}