/// alarm.dart - Alarm data model matching desktop app structure
///
/// Represents an alarm with all its properties including:
/// - Time and recurrence
/// - Spotify playlist information
/// - Volume and fade-in settings
/// - Device and sync metadata

import 'package:json_annotation/json_annotation.dart';

part 'alarm.g.dart';

@JsonSerializable()
class Alarm {
  final String id;
  final String time;  // Format: HH:MM
  final String playlistName;
  final String playlistUri;
  final int volume;  // 0-100
  final bool fadeInEnabled;
  final int fadeInDuration;  // minutes
  final List<String> days;  // Active days: Monday, Tuesday, etc.
  final bool isActive;
  final String? deviceId;
  final DateTime? lastModified;
  final DateTime? createdAt;
  
  Alarm({
    required this.id,
    required this.time,
    required this.playlistName,
    required this.playlistUri,
    required this.volume,
    this.fadeInEnabled = false,
    this.fadeInDuration = 10,
    this.days = const ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    this.isActive = true,
    this.deviceId,
    this.lastModified,
    this.createdAt,
  });
  
  // Create alarm from JSON
  factory Alarm.fromJson(Map<String, dynamic> json) => _$AlarmFromJson(json);
  
  // Convert alarm to JSON
  Map<String, dynamic> toJson() => _$AlarmToJson(this);
  
  // Copy with modifications
  Alarm copyWith({
    String? id,
    String? time,
    String? playlistName,
    String? playlistUri,
    int? volume,
    bool? fadeInEnabled,
    int? fadeInDuration,
    List<String>? days,
    bool? isActive,
    String? deviceId,
    DateTime? lastModified,
    DateTime? createdAt,
  }) {
    return Alarm(
      id: id ?? this.id,
      time: time ?? this.time,
      playlistName: playlistName ?? this.playlistName,
      playlistUri: playlistUri ?? this.playlistUri,
      volume: volume ?? this.volume,
      fadeInEnabled: fadeInEnabled ?? this.fadeInEnabled,
      fadeInDuration: fadeInDuration ?? this.fadeInDuration,
      days: days ?? this.days,
      isActive: isActive ?? this.isActive,
      deviceId: deviceId ?? this.deviceId,
      lastModified: lastModified ?? this.lastModified,
      createdAt: createdAt ?? this.createdAt,
    );
  }
  
  // Get formatted time (e.g., "7:00 AM")
  String get formattedTime {
    final parts = time.split(':');
    if (parts.length != 2) return time;
    
    final hour = int.tryParse(parts[0]) ?? 0;
    final minute = int.tryParse(parts[1]) ?? 0;
    
    final period = hour >= 12 ? 'PM' : 'AM';
    final displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
    
    return '$displayHour:${minute.toString().padLeft(2, '0')} $period';
  }
  
  // Get day abbreviations (e.g., "M T W T F")
  String get dayAbbreviations {
    const abbrevMap = {
      'Monday': 'M',
      'Tuesday': 'T',
      'Wednesday': 'W',
      'Thursday': 'T',
      'Friday': 'F',
      'Saturday': 'S',
      'Sunday': 'S',
    };
    
    return days.map((day) => abbrevMap[day] ?? day[0]).join(' ');
  }
  
  // Check if alarm is set for today
  bool get isActiveToday {
    if (!isActive) return false;
    
    final weekdayMap = {
      1: 'Monday',
      2: 'Tuesday',
      3: 'Wednesday',
      4: 'Thursday',
      5: 'Friday',
      6: 'Saturday',
      7: 'Sunday',
    };
    
    final today = weekdayMap[DateTime.now().weekday];
    return days.contains(today);
  }
  
  @override
  String toString() {
    return 'Alarm(id: $id, time: $time, playlist: $playlistName, active: $isActive)';
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    
    return other is Alarm &&
        other.id == id &&
        other.time == time &&
        other.playlistUri == playlistUri;
  }
  
  @override
  int get hashCode => id.hashCode ^ time.hashCode ^ playlistUri.hashCode;
}
