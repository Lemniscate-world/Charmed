// alarm.rs - Logique de gestion des alarmes
// TODO: Ces fonctions seront utilisées quand l'UI sera connectée

#![allow(dead_code)]

use chrono::{Local, NaiveTime, Weekday, Datelike, TimeZone};
use crate::AlarmEntry;

/// Vérifie si une alarme doit se déclencher maintenant
pub fn should_trigger(alarm: &AlarmEntry) -> bool {
    if !alarm.active {
        return false;
    }

    let now = Local::now();
    let current_time = now.format("%H:%M").to_string();
    let today = weekday_to_string(now.weekday());

    // Vérifier l'heure
    if alarm.time != current_time {
        return false;
    }

    // Vérifier le jour si des jours sont spécifiés
    if !alarm.days.is_empty() && !alarm.days.iter().any(|d| d == today) {
        return false;
    }

    true
}

/// Convertit un Weekday en String
fn weekday_to_string(day: Weekday) -> &'static str {
    match day {
        Weekday::Mon => "Monday",
        Weekday::Tue => "Tuesday",
        Weekday::Wed => "Wednesday",
        Weekday::Thu => "Thursday",
        Weekday::Fri => "Friday",
        Weekday::Sat => "Saturday",
        Weekday::Sun => "Sunday",
    }
}

/// Convertit une String en Weekday
pub fn string_to_weekday(s: &str) -> Option<Weekday> {
    match s {
        "Monday" => Some(Weekday::Mon),
        "Tuesday" => Some(Weekday::Tue),
        "Wednesday" => Some(Weekday::Wed),
        "Thursday" => Some(Weekday::Thu),
        "Friday" => Some(Weekday::Fri),
        "Saturday" => Some(Weekday::Sat),
        "Sunday" => Some(Weekday::Sun),
        _ => None,
    }
}

/// Calcule le temps restant avant le déclenchement de l'alarme (en secondes)
pub fn time_until_alarm(alarm: &AlarmEntry) -> Option<i64> {
    let now = Local::now();
    
    // Parser l'heure de l'alarme
    let alarm_time = NaiveTime::parse_from_str(&alarm.time, "%H:%M").ok()?;
    
    // Construire le datetime d'aujourd'hui avec l'heure de l'alarme
    let alarm_datetime = now.date_naive().and_time(alarm_time);
    let alarm_datetime = Local::from_utc_datetime(&Local::now().timezone(), &alarm_datetime);
    
    // Calculer la différence
    let diff = alarm_datetime.signed_duration_since(now);
    
    // Si l'heure est déjà passée aujourd'hui, c'est pour demain
    if diff.num_seconds() < 0 {
        // Ajouter 24 heures
        Some(86400 + diff.num_seconds())
    } else {
        Some(diff.num_seconds())
    }
}

/// Formate le temps restant en texte lisible
pub fn format_time_until(seconds: i64) -> String {
    if seconds < 60 {
        format!("{} seconde{}", seconds, if seconds > 1 { "s" } else { "" })
    } else if seconds < 3600 {
        let minutes = seconds / 60;
        format!("{} minute{}", minutes, if minutes > 1 { "s" } else { "" })
    } else {
        let hours = seconds / 3600;
        let minutes = (seconds % 3600) / 60;
        if minutes > 0 {
            format!("{}h {}m", hours, minutes)
        } else {
            format!("{} heure{}", hours, if hours > 1 { "s" } else { "" })
        }
    }
}

/// Génère la liste des jours de la semaine
pub fn get_weekdays() -> Vec<&'static str> {
    vec!["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
}

/// Vérifie si l'alarme est pour un jour de semaine
pub fn is_weekday_only(days: &[String]) -> bool {
    let weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
    days.iter().all(|d| weekdays.contains(&d.as_str())) && days.len() == 5
}

/// Vérifie si l'alarme est pour le weekend
pub fn is_weekend_only(days: &[String]) -> bool {
    let weekend = ["Saturday", "Sunday"];
    days.iter().all(|d| weekend.contains(&d.as_str())) && days.len() == 2
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_weekday_conversion() {
        assert_eq!(weekday_to_string(Weekday::Mon), "Monday");
        assert_eq!(weekday_to_string(Weekday::Sun), "Sunday");
        
        assert_eq!(string_to_weekday("Monday"), Some(Weekday::Mon));
        assert_eq!(string_to_weekday("Invalid"), None);
    }

    #[test]
    fn test_time_format() {
        assert_eq!(format_time_until(30), "30 secondes");
        assert_eq!(format_time_until(1), "1 seconde");
        assert_eq!(format_time_until(90), "1 minute");
        assert_eq!(format_time_until(180), "3 minutes");
        assert_eq!(format_time_until(3600), "1 heure");
        assert_eq!(format_time_until(7200), "2 heures");
        assert_eq!(format_time_until(3661), "1h 1m");
    }

    #[test]
    fn test_weekday_checks() {
        let weekdays = vec![
            "Monday".to_string(),
            "Tuesday".to_string(),
            "Wednesday".to_string(),
            "Thursday".to_string(),
            "Friday".to_string(),
        ];
        assert!(is_weekday_only(&weekdays));
        assert!(!is_weekend_only(&weekdays));

        let weekend = vec!["Saturday".to_string(), "Sunday".to_string()];
        assert!(is_weekend_only(&weekend));
        assert!(!is_weekday_only(&weekend));
    }
}