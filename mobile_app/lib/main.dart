/// main.dart - Alarmify Mobile App Entry Point
///
/// Flutter mobile companion app for Alarmify desktop
/// Provides alarm management with cloud sync integration

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:uuid/uuid.dart';

import 'theme/app_theme.dart';
import 'theme/app_colors.dart';
import 'services/cloud_sync_service.dart';
import 'services/storage_service.dart';
import 'providers/auth_provider.dart';
import 'providers/alarm_provider.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Set system UI overlay style
  AppTheme.setSystemUIOverlay();
  
  // Initialize services
  final storageService = await StorageService.initialize();
  final cloudSyncService = CloudSyncService();
  
  // Generate device ID if not exists
  if (storageService.getDeviceId() == null) {
    final deviceId = const Uuid().v4();
    await storageService.saveDeviceId(deviceId);
  }
  
  runApp(AlarmifyApp(
    storageService: storageService,
    cloudSyncService: cloudSyncService,
  ));
}

class AlarmifyApp extends StatelessWidget {
  final StorageService storageService;
  final CloudSyncService cloudSyncService;
  
  const AlarmifyApp({
    Key? key,
    required this.storageService,
    required this.cloudSyncService,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Services
        Provider<StorageService>.value(value: storageService),
        Provider<CloudSyncService>.value(value: cloudSyncService),
        
        // State providers
        ChangeNotifierProvider<AuthProvider>(
          create: (_) => AuthProvider(
            cloudService: cloudSyncService,
            storage: storageService,
          ),
        ),
        ChangeNotifierProvider<AlarmProvider>(
          create: (_) => AlarmProvider(
            cloudService: cloudSyncService,
            storage: storageService,
          ),
        ),
      ],
      child: MaterialApp(
        title: 'Alarmify',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        home: const SplashScreen(),
        routes: {
          '/login': (context) => const LoginScreen(),
          '/home': (context) => const HomeScreen(),
        },
      ),
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);
  
  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _navigateToNextScreen();
  }
  
  Future<void> _navigateToNextScreen() async {
    // Wait for auth provider to initialize
    await Future.delayed(const Duration(milliseconds: 500));
    
    if (!mounted) return;
    
    final authProvider = context.read<AuthProvider>();
    
    // Navigate based on auth status
    if (authProvider.isAuthenticated) {
      Navigator.of(context).pushReplacementNamed('/home');
    } else {
      Navigator.of(context).pushReplacementNamed('/login');
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.alarm,
              size: 100,
              color: AppColors.accent,
            ),
            const SizedBox(height: 24),
            Text(
              'Alarmify',
              style: Theme.of(context).textTheme.displayMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Wake up to your music',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 48),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.accent),
            ),
          ],
        ),
      ),
    );
  }
}
