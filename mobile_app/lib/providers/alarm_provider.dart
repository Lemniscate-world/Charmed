/// alarm_provider.dart - Alarm state management
///
/// Manages alarm list state and provides CRUD operations with cloud sync

import 'package:flutter/foundation.dart';
import 'dart:async';
import '../models/alarm.dart';
import '../services/cloud_sync_service.dart';
import '../services/storage_service.dart';

enum SyncStatus {
  idle,
  syncing,
  success,
  error,
}

class AlarmProvider with ChangeNotifier {
  final CloudSyncService _cloudService;
  final StorageService _storage;
  
  List<Alarm> _alarms = [];
  SyncStatus _syncStatus = SyncStatus.idle;
  String? _syncMessage;
  Timer? _autoSyncTimer;
  
  AlarmProvider({
    required CloudSyncService cloudService,
    required StorageService storage,
  })  : _cloudService = cloudService,
        _storage = storage {
    _loadAlarms();
    _setupAutoSync();
  }
  
  // Getters
  List<Alarm> get alarms => List.unmodifiable(_alarms);
  SyncStatus get syncStatus => _syncStatus;
  String? get syncMessage => _syncMessage;
  bool get isSyncing => _syncStatus == SyncStatus.syncing;
  
  // Get active alarms only
  List<Alarm> get activeAlarms => _alarms.where((a) => a.isActive).toList();
  
  // Get inactive alarms only
  List<Alarm> get inactiveAlarms => _alarms.where((a) => !a.isActive).toList();
  
  // Load alarms from local storage
  void _loadAlarms() {
    _alarms = _storage.getAlarms();
    notifyListeners();
  }
  
  // Save alarms to local storage
  Future<void> _saveAlarms() async {
    await _storage.saveAlarms(_alarms);
  }
  
  // Add new alarm
  Future<void> addAlarm(Alarm alarm) async {
    _alarms.add(alarm);
    await _saveAlarms();
    notifyListeners();
    
    // Auto-sync if enabled
    if (_storage.getAutoSync()) {
      await syncAlarms();
    }
  }
  
  // Update existing alarm
  Future<void> updateAlarm(String id, Alarm updatedAlarm) async {
    final index = _alarms.indexWhere((a) => a.id == id);
    if (index != -1) {
      _alarms[index] = updatedAlarm;
      await _saveAlarms();
      notifyListeners();
      
      // Auto-sync if enabled
      if (_storage.getAutoSync()) {
        await syncAlarms();
      }
    }
  }
  
  // Delete alarm
  Future<void> deleteAlarm(String id) async {
    _alarms.removeWhere((a) => a.id == id);
    await _saveAlarms();
    notifyListeners();
    
    // Auto-sync if enabled
    if (_storage.getAutoSync()) {
      await syncAlarms();
    }
  }
  
  // Toggle alarm active state
  Future<void> toggleAlarm(String id) async {
    final index = _alarms.indexWhere((a) => a.id == id);
    if (index != -1) {
      _alarms[index] = _alarms[index].copyWith(
        isActive: !_alarms[index].isActive,
        lastModified: DateTime.now(),
      );
      await _saveAlarms();
      notifyListeners();
      
      // Auto-sync if enabled
      if (_storage.getAutoSync()) {
        await syncAlarms();
      }
    }
  }
  
  // Sync alarms with cloud
  Future<void> syncAlarms() async {
    if (_syncStatus == SyncStatus.syncing) {
      return; // Already syncing
    }
    
    _syncStatus = SyncStatus.syncing;
    _syncMessage = 'Syncing alarms...';
    notifyListeners();
    
    try {
      final user = _storage.getUser();
      final deviceId = _storage.getDeviceId();
      
      if (user == null || deviceId == null) {
        throw Exception('Not authenticated');
      }
      
      final result = await _cloudService.syncAlarms(
        userId: user.userId,
        localAlarms: _alarms,
        deviceId: deviceId,
      );
      
      if (result['success']) {
        // Update local alarms with merged data
        _alarms = result['alarms'] as List<Alarm>;
        await _saveAlarms();
        
        _syncStatus = SyncStatus.success;
        _syncMessage = result['message'];
        notifyListeners();
        
        // Clear success message after 3 seconds
        Future.delayed(const Duration(seconds: 3), () {
          if (_syncStatus == SyncStatus.success) {
            _syncStatus = SyncStatus.idle;
            _syncMessage = null;
            notifyListeners();
          }
        });
      } else {
        _syncStatus = SyncStatus.error;
        _syncMessage = result['message'];
        notifyListeners();
      }
    } catch (e) {
      _syncStatus = SyncStatus.error;
      _syncMessage = 'Sync failed: ${e.toString()}';
      notifyListeners();
    }
  }
  
  // Backup alarms to cloud
  Future<void> backupAlarms() async {
    _syncStatus = SyncStatus.syncing;
    _syncMessage = 'Backing up alarms...';
    notifyListeners();
    
    try {
      final user = _storage.getUser();
      final deviceId = _storage.getDeviceId();
      
      if (user == null || deviceId == null) {
        throw Exception('Not authenticated');
      }
      
      final result = await _cloudService.backupAlarms(
        userId: user.userId,
        alarms: _alarms,
        deviceId: deviceId,
      );
      
      if (result['success']) {
        _syncStatus = SyncStatus.success;
        _syncMessage = result['message'];
      } else {
        _syncStatus = SyncStatus.error;
        _syncMessage = result['message'];
      }
      notifyListeners();
    } catch (e) {
      _syncStatus = SyncStatus.error;
      _syncMessage = 'Backup failed: ${e.toString()}';
      notifyListeners();
    }
  }
  
  // Restore alarms from cloud
  Future<void> restoreAlarms() async {
    _syncStatus = SyncStatus.syncing;
    _syncMessage = 'Restoring alarms...';
    notifyListeners();
    
    try {
      final user = _storage.getUser();
      
      if (user == null) {
        throw Exception('Not authenticated');
      }
      
      final result = await _cloudService.restoreAlarms(
        userId: user.userId,
      );
      
      if (result['success']) {
        _alarms = result['alarms'] as List<Alarm>;
        await _saveAlarms();
        
        _syncStatus = SyncStatus.success;
        _syncMessage = result['message'];
      } else {
        _syncStatus = SyncStatus.error;
        _syncMessage = result['message'];
      }
      notifyListeners();
    } catch (e) {
      _syncStatus = SyncStatus.error;
      _syncMessage = 'Restore failed: ${e.toString()}';
      notifyListeners();
    }
  }
  
  // Setup auto-sync timer
  void _setupAutoSync() {
    _autoSyncTimer?.cancel();
    
    if (_storage.getAutoSync()) {
      final interval = _storage.getSyncInterval();
      _autoSyncTimer = Timer.periodic(
        Duration(minutes: interval),
        (_) => syncAlarms(),
      );
    }
  }
  
  // Enable/disable auto-sync
  Future<void> setAutoSync(bool enabled) async {
    await _storage.setAutoSync(enabled);
    _setupAutoSync();
    
    if (enabled) {
      await syncAlarms();
    }
  }
  
  // Set auto-sync interval
  Future<void> setSyncInterval(int minutes) async {
    await _storage.setSyncInterval(minutes);
    _setupAutoSync();
  }
  
  // Clear sync message
  void clearSyncMessage() {
    _syncMessage = null;
    if (_syncStatus != SyncStatus.syncing) {
      _syncStatus = SyncStatus.idle;
    }
    notifyListeners();
  }
  
  @override
  void dispose() {
    _autoSyncTimer?.cancel();
    super.dispose();
  }
}
