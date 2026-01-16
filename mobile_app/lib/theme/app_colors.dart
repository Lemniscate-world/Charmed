/// app_colors.dart - Charm-inspired color system for Alarmify Mobile
///
/// Colors based on the Charm design system and PRODUCT_ROADMAP.md specifications:
/// - Deep black background
/// - Subtle surface elevation
/// - Spotify green accent
/// - High contrast text hierarchy

import 'package:flutter/material.dart';

class AppColors {
  // Prevent instantiation
  AppColors._();
  
  // Background colors
  static const Color background = Color(0xFF0A0A0A);  // Deep black
  static const Color surface = Color(0xFF1A1A1A);     // Slightly lighter
  static const Color card = Color(0xFF252525);        // Elevated surface
  static const Color elevated = Color(0xFF303030);    // Higher elevation
  
  // Accent colors
  static const Color accent = Color(0xFF1DB954);      // Spotify green
  static const Color accentDark = Color(0xFF1AA34A);  // Darker green
  static const Color alert = Color(0xFFFF6B6B);       // Alert/important
  static const Color alertDark = Color(0xFFE85555);   // Darker alert
  static const Color warning = Color(0xFFFFA500);     // Warning orange
  static const Color success = Color(0xFF1DB954);     // Success (same as accent)
  
  // Text colors
  static const Color textPrimary = Color(0xFFFFFFFF);    // White
  static const Color textSecondary = Color(0xFFB3B3B3);  // Light gray
  static const Color textTertiary = Color(0xFF727272);   // Medium gray
  static const Color textDisabled = Color(0xFF4A4A4A);   // Dark gray
  
  // Border colors
  static const Color border = Color(0xFF303030);
  static const Color borderLight = Color(0xFF404040);
  
  // Glass effect
  static const Color glass = Color(0x1AFFFFFF);       // 10% white
  static const Color glassHighlight = Color(0x33FFFFFF); // 20% white
  
  // Status colors for alarms
  static const Color alarmActive = Color(0xFF1DB954);
  static const Color alarmInactive = Color(0xFF727272);
  static const Color alarmSnoozed = Color(0xFFFFA500);
  
  // Gradient colors
  static const LinearGradient cardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFF252525),
      Color(0xFF1A1A1A),
    ],
  );
  
  static const LinearGradient accentGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFF1DB954),
      Color(0xFF1AA34A),
    ],
  );
  
  // Shadows
  static const List<BoxShadow> cardShadow = [
    BoxShadow(
      color: Color(0x40000000),
      blurRadius: 24,
      offset: Offset(0, 8),
    ),
  ];
  
  static const List<BoxShadow> elevatedShadow = [
    BoxShadow(
      color: Color(0x60000000),
      blurRadius: 32,
      offset: Offset(0, 12),
    ),
  ];
}
