// audio.rs - Lecture audio locale (alarme fallback)
// TODO: Améliorer la gestion audio avec un thread dédié

#![allow(dead_code)]

use rodio::{OutputStream, Sink, Source};
use rodio::source::SineWave;
use std::time::Duration;

/// Joue le son d'alarme local
/// Note: Cette fonction cree un nouveau flux audio a chaque appel
/// car OutputStream n'est pas Send/Sync et ne peut pas etre stocke globalement
pub fn play_alarm_sound() -> Result<(), String> {
    // Creer un nouveau flux audio
    let (_stream, stream_handle) = OutputStream::try_default()
        .map_err(|e| format!("Impossible d'ouvrir le flux audio: {}", e))?;

    let sink = Sink::try_new(&stream_handle)
        .map_err(|e| format!("Impossible de creer le sink audio: {}", e))?;

    // Generer un son de beep avec une source
    let source = SineWave::new(440.0); // 440 Hz = A4
    
    // Appliquer les transformations via le trait Source
    let source = source.amplify(0.5);
    let source = source.repeat_infinite();
    let source = source.take_duration(Duration::from_secs(30));
    
    sink.append(source);
    sink.set_volume(0.8);
    sink.play();

    // Garder le flux en vie en le "leakant" - c'est le seul moyen pour que le son continue
    // Note: Pour une vraie application, il faudrait un thread dedie
    std::mem::forget(_stream);
    std::mem::forget(sink);

    Ok(())
}

/// Arrete le son d'alarme
/// Note: Avec l'approche actuelle, cette fonction ne peut pas vraiment arreter le son
/// car le sink est "oublie". Pour une vraie implementation, il faudrait un thread dedie.
pub fn stop_alarm_sound() -> Result<(), String> {
    // Avec l'approche actuelle, on ne peut pas arreter le son
    // Pour l'instant, cette fonction est un no-op
    Ok(())
}

/// Regle le volume de l'alarme locale (0-100)
pub fn set_alarm_volume(_volume_percent: u8) -> Result<(), String> {
    // Avec l'approche actuelle, on ne peut pas changer le volume
    Ok(())
}

/// Verifie si l'alarme est en cours de lecture
pub fn is_playing() -> bool {
    // Avec l'approche actuelle, on ne peut pas verifier
    false
}