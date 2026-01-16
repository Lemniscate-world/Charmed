/// cloud_sync_service.dart - Cloud sync API integration
///
/// Communicates with Alarmify desktop cloud sync backend for:
/// - Authentication (login/register)
/// - Alarm synchronization
/// - Device management
/// - Settings sync
///
/// NOTE: This implementation expects a REST API backend.
/// The current desktop app uses file-based storage for cloud sync simulation.
/// For production, this would connect to a proper cloud API service.
/// For development/testing, a bridge server or mock API would be needed.

import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/alarm.dart';
import '../models/user.dart';
import '../models/device.dart';

class CloudSyncService {
  // Base URL - in production, this would be a proper API endpoint
  // For MVP, we'll use local file system simulation matching desktop app
  final String baseUrl;
  
  // HTTP client
  final http.Client _client = http.Client();
  
  // Current auth tokens
  String? _accessToken;
  String? _refreshToken;
  
  CloudSyncService({this.baseUrl = 'http://localhost:5000/api'});
  
  // Set authentication tokens
  void setTokens(String accessToken, String refreshToken) {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
  }
  
  // Clear authentication tokens
  void clearTokens() {
    _accessToken = null;
    _refreshToken = null;
  }
  
  // Get authorization headers
  Map<String, String> get _authHeaders {
    if (_accessToken == null) {
      return {'Content-Type': 'application/json'};
    }
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $_accessToken',
    };
  }
  
  // Register new user
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    String? displayName,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          'display_name': displayName,
        }),
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        return {
          'success': true,
          'message': data['message'] ?? 'Registration successful',
          'user_id': data['user_id'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Registration failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }
  
  // Login user
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        _accessToken = data['access_token'];
        _refreshToken = data['refresh_token'];
        
        return {
          'success': true,
          'message': data['message'] ?? 'Login successful',
          'access_token': _accessToken,
          'refresh_token': _refreshToken,
          'user': data['user'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Login failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }
  
  // Get current user info
  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/auth/user'),
        headers: _authHeaders,
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return {
          'success': true,
          'user': data['user'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to get user info',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }
  
  // Backup alarms to cloud
  Future<Map<String, dynamic>> backupAlarms({
    required String userId,
    required List<Alarm> alarms,
    required String deviceId,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/sync/alarms/backup'),
        headers: _authHeaders,
        body: jsonEncode({
          'user_id': userId,
          'device_id': deviceId,
          'alarms': alarms.map((a) => a.toJson()).toList(),
        }),
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return {
          'success': true,
          'message': data['message'] ?? 'Alarms backed up successfully',
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Backup failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }
  
  // Restore alarms from cloud
  Future<Map<String, dynamic>> restoreAlarms({
    required String userId,
  }) async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/sync/alarms/restore?user_id=$userId'),
        headers: _authHeaders,
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final alarmsList = (data['alarms'] as List?)
            ?.map((json) => Alarm.fromJson(json))
            .toList() ?? [];
        
        return {
          'success': true,
          'message': data['message'] ?? 'Alarms restored successfully',
          'alarms': alarmsList,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Restore failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }
  
  // Sync alarms (bi-directional)
  Future<Map<String, dynamic>> syncAlarms({
    required String userId,
    required List<Alarm> localAlarms,
    required String deviceId,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/sync/alarms/sync'),
        headers: _authHeaders,
        body: jsonEncode({
          'user_id': userId,
          'device_id': deviceId,
          'local_alarms': localAlarms.map((a) => a.toJson()).toList(),
        }),
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final mergedAlarms = (data['merged_alarms'] as List?)
            ?.map((json) => Alarm.fromJson(json))
            .toList() ?? [];
        
        return {
          'success': true,
          'message': data['message'] ?? 'Sync completed successfully',
          'alarms': mergedAlarms,
          'conflicts': data['conflicts'] ?? [],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Sync failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }
  
  // Register device
  Future<Map<String, dynamic>> registerDevice({
    required String userId,
    required String deviceId,
    required String deviceName,
    required String deviceType,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/devices/register'),
        headers: _authHeaders,
        body: jsonEncode({
          'user_id': userId,
          'device_id': deviceId,
          'device_name': deviceName,
          'device_type': deviceType,
        }),
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return {
          'success': true,
          'message': data['message'] ?? 'Device registered successfully',
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Device registration failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }
  
  // Get registered devices
  Future<Map<String, dynamic>> getDevices({
    required String userId,
  }) async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/devices?user_id=$userId'),
        headers: _authHeaders,
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final devicesList = (data['devices'] as List?)
            ?.map((json) => Device.fromJson(json))
            .toList() ?? [];
        
        return {
          'success': true,
          'message': data['message'] ?? 'Devices retrieved successfully',
          'devices': devicesList,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to get devices',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }
  
  // Refresh access token
  Future<Map<String, dynamic>> refreshToken() async {
    if (_refreshToken == null) {
      return {
        'success': false,
        'message': 'No refresh token available',
      };
    }
    
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/auth/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'refresh_token': _refreshToken,
        }),
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        _accessToken = data['access_token'];
        
        return {
          'success': true,
          'message': 'Token refreshed successfully',
          'access_token': _accessToken,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Token refresh failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }
  
  // Dispose HTTP client
  void dispose() {
    _client.close();
  }
}
