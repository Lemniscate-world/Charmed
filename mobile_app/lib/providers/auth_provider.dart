/// auth_provider.dart - Authentication state management
///
/// Manages user authentication state and provides auth methods

import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../services/cloud_sync_service.dart';
import '../services/storage_service.dart';

enum AuthStatus {
  initial,
  authenticated,
  unauthenticated,
  loading,
}

class AuthProvider with ChangeNotifier {
  final CloudSyncService _cloudService;
  final StorageService _storage;
  
  User? _user;
  AuthStatus _status = AuthStatus.initial;
  String? _errorMessage;
  
  AuthProvider({
    required CloudSyncService cloudService,
    required StorageService storage,
  })  : _cloudService = cloudService,
        _storage = storage {
    _initialize();
  }
  
  // Getters
  User? get user => _user;
  AuthStatus get status => _status;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _status == AuthStatus.authenticated;
  bool get isLoading => _status == AuthStatus.loading;
  
  // Initialize - check for stored credentials
  Future<void> _initialize() async {
    final storedUser = _storage.getUser();
    final accessToken = await _storage.getAccessToken();
    final refreshToken = await _storage.getRefreshToken();
    
    if (storedUser != null && accessToken != null && refreshToken != null) {
      _user = storedUser;
      _cloudService.setTokens(accessToken, refreshToken);
      _status = AuthStatus.authenticated;
      notifyListeners();
      
      // Verify token is still valid
      await _verifyAuth();
    } else {
      _status = AuthStatus.unauthenticated;
      notifyListeners();
    }
  }
  
  // Verify authentication
  Future<void> _verifyAuth() async {
    final result = await _cloudService.getCurrentUser();
    
    if (!result['success']) {
      // Try to refresh token
      final refreshResult = await _cloudService.refreshToken();
      
      if (refreshResult['success']) {
        await _storage.saveAccessToken(refreshResult['access_token']);
      } else {
        // Token refresh failed, logout
        await logout();
      }
    }
  }
  
  // Register new user
  Future<bool> register({
    required String email,
    required String password,
    String? displayName,
  }) async {
    _status = AuthStatus.loading;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final result = await _cloudService.register(
        email: email,
        password: password,
        displayName: displayName,
      );
      
      if (result['success']) {
        // Auto-login after registration
        return await login(email: email, password: password);
      } else {
        _errorMessage = result['message'];
        _status = AuthStatus.unauthenticated;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Registration failed: ${e.toString()}';
      _status = AuthStatus.unauthenticated;
      notifyListeners();
      return false;
    }
  }
  
  // Login user
  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _status = AuthStatus.loading;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final result = await _cloudService.login(
        email: email,
        password: password,
      );
      
      if (result['success']) {
        // Parse user data
        _user = User.fromJson(result['user']);
        
        // Store credentials
        await _storage.saveUser(_user!);
        await _storage.saveAccessToken(result['access_token']);
        await _storage.saveRefreshToken(result['refresh_token']);
        
        _status = AuthStatus.authenticated;
        notifyListeners();
        return true;
      } else {
        _errorMessage = result['message'];
        _status = AuthStatus.unauthenticated;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Login failed: ${e.toString()}';
      _status = AuthStatus.unauthenticated;
      notifyListeners();
      return false;
    }
  }
  
  // Logout user
  Future<void> logout() async {
    _user = null;
    _status = AuthStatus.unauthenticated;
    _errorMessage = null;
    
    // Clear stored data
    await _storage.clearUser();
    await _storage.clearTokens();
    _cloudService.clearTokens();
    
    notifyListeners();
  }
  
  // Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
