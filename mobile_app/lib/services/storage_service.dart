/// storage_service.dart - Local data persistence
///
/// Manages local storage using SharedPreferences for app settings
/// and FlutterSecureStorage for sensitive data like tokens

import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/alarm.dart';
import '../models/user.dart';

class StorageService {
  static const String _keyAlarms = 'alarms';
  static const String _keyUser = 'user';
  static const String _keyAccessToken = 'access_token';
  static const String _keyRefreshToken = 'refresh_token';
  static const String _keyDeviceId = 'device_id';
  static const String _keyAutoSync = 'auto_sync';
  static const String _keySyncInterval = 'sync_interval';
  
  final SharedPreferences _prefs;
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  
  StorageService(this._prefs);
  
  // Initialize storage service
  static Future<StorageService> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    return StorageService(prefs);
  }
  
  // Alarm storage
  Future<void> saveAlarms(List<Alarm> alarms) async {
    final alarmsJson = alarms.map((a) => a.toJson()).toList();
    await _prefs.setString(_keyAlarms, jsonEncode(alarmsJson));
  }
  
  List<Alarm> getAlarms() {
    final alarmsJson = _prefs.getString(_keyAlarms);
    if (alarmsJson == null) return [];
    
    try {
      final List<dynamic> decoded = jsonDecode(alarmsJson);
      return decoded.map((json) => Alarm.fromJson(json)).toList();
    } catch (e) {
      return [];
    }
  }
  
  // User storage
  Future<void> saveUser(User user) async {
    await _prefs.setString(_keyUser, jsonEncode(user.toJson()));
  }
  
  User? getUser() {
    final userJson = _prefs.getString(_keyUser);
    if (userJson == null) return null;
    
    try {
      return User.fromJson(jsonDecode(userJson));
    } catch (e) {
      return null;
    }
  }
  
  Future<void> clearUser() async {
    await _prefs.remove(_keyUser);
  }
  
  // Secure token storage
  Future<void> saveAccessToken(String token) async {
    await _secureStorage.write(key: _keyAccessToken, value: token);
  }
  
  Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: _keyAccessToken);
  }
  
  Future<void> saveRefreshToken(String token) async {
    await _secureStorage.write(key: _keyRefreshToken, value: token);
  }
  
  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: _keyRefreshToken);
  }
  
  Future<void> clearTokens() async {
    await _secureStorage.delete(key: _keyAccessToken);
    await _secureStorage.delete(key: _keyRefreshToken);
  }
  
  // Device ID storage
  Future<void> saveDeviceId(String deviceId) async {
    await _prefs.setString(_keyDeviceId, deviceId);
  }
  
  String? getDeviceId() {
    return _prefs.getString(_keyDeviceId);
  }
  
  // Auto-sync settings
  Future<void> setAutoSync(bool enabled) async {
    await _prefs.setBool(_keyAutoSync, enabled);
  }
  
  bool getAutoSync() {
    return _prefs.getBool(_keyAutoSync) ?? false;
  }
  
  Future<void> setSyncInterval(int minutes) async {
    await _prefs.setInt(_keySyncInterval, minutes);
  }
  
  int getSyncInterval() {
    return _prefs.getInt(_keySyncInterval) ?? 30; // Default: 30 minutes
  }
  
  // Clear all data (logout)
  Future<void> clearAll() async {
    await _prefs.clear();
    await _secureStorage.deleteAll();
  }
}
