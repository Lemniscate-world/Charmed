/// settings_screen.dart - App settings and account management
///
/// Provides sync settings, account info, and logout

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/alarm_provider.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../services/storage_service.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({Key? key}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppTheme.spacingMedium),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Account section
            Consumer<AuthProvider>(
              builder: (context, auth, _) {
                final user = auth.user;
                
                return GlassCard(
                  child: Column(
                    children: [
                      ListTile(
                        leading: CircleAvatar(
                          backgroundColor: AppColors.accent,
                          child: Text(
                            user?.displayName[0].toUpperCase() ?? 'U',
                            style: const TextStyle(
                              color: AppColors.textPrimary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        title: Text(user?.displayName ?? 'User'),
                        subtitle: Text(user?.email ?? ''),
                      ),
                      const Divider(height: 1),
                      ListTile(
                        leading: const Icon(Icons.logout, color: AppColors.alert),
                        title: const Text(
                          'Logout',
                          style: TextStyle(color: AppColors.alert),
                        ),
                        onTap: () {
                          _showLogoutDialog(context);
                        },
                      ),
                    ],
                  ),
                );
              },
            ),
            
            const SizedBox(height: AppTheme.spacingMedium),
            
            // Sync settings
            Text(
              'Cloud Sync',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: AppTheme.spacingSmall),
            
            Consumer<AlarmProvider>(
              builder: (context, alarmProvider, _) {
                return GlassCard(
                  child: Column(
                    children: [
                      ListTile(
                        leading: const Icon(Icons.cloud_sync),
                        title: const Text('Sync Now'),
                        subtitle: Text(_getSyncStatusText(alarmProvider)),
                        trailing: alarmProvider.isSyncing
                            ? const SizedBox(
                                height: 24,
                                width: 24,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.chevron_right),
                        onTap: alarmProvider.isSyncing
                            ? null
                            : () {
                                alarmProvider.syncAlarms();
                              },
                      ),
                      const Divider(height: 1),
                      ListTile(
                        leading: const Icon(Icons.backup),
                        title: const Text('Backup Alarms'),
                        subtitle: const Text('Upload to cloud'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () {
                          alarmProvider.backupAlarms();
                        },
                      ),
                      const Divider(height: 1),
                      ListTile(
                        leading: const Icon(Icons.cloud_download),
                        title: const Text('Restore Alarms'),
                        subtitle: const Text('Download from cloud'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () {
                          _showRestoreDialog(context);
                        },
                      ),
                    ],
                  ),
                );
              },
            ),
            
            const SizedBox(height: AppTheme.spacingMedium),
            
            // Auto-sync toggle
            _AutoSyncSettings(),
            
            const SizedBox(height: AppTheme.spacingMedium),
            
            // About section
            Text(
              'About',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: AppTheme.spacingSmall),
            
            GlassCard(
              child: Column(
                children: [
                  const ListTile(
                    leading: Icon(Icons.info_outline),
                    title: Text('Version'),
                    subtitle: Text('1.0.0'),
                  ),
                  const Divider(height: 1),
                  ListTile(
                    leading: const Icon(Icons.description_outlined),
                    title: const Text('Privacy Policy'),
                    trailing: const Icon(Icons.open_in_new),
                    onTap: () {
                      // TODO: Open privacy policy
                    },
                  ),
                  const Divider(height: 1),
                  ListTile(
                    leading: const Icon(Icons.article_outlined),
                    title: const Text('Terms of Service'),
                    trailing: const Icon(Icons.open_in_new),
                    onTap: () {
                      // TODO: Open terms
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  String _getSyncStatusText(AlarmProvider provider) {
    if (provider.isSyncing) {
      return 'Syncing...';
    }
    return 'Tap to sync with cloud';
  }
  
  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              context.read<AuthProvider>().logout();
              Navigator.of(context).pushNamedAndRemoveUntil(
                '/login',
                (route) => false,
              );
            },
            child: const Text(
              'Logout',
              style: TextStyle(color: AppColors.alert),
            ),
          ),
        ],
      ),
    );
  }
  
  void _showRestoreDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Restore Alarms'),
        content: const Text(
          'This will replace your local alarms with data from the cloud. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              context.read<AlarmProvider>().restoreAlarms();
              Navigator.pop(context);
            },
            child: const Text('Restore'),
          ),
        ],
      ),
    );
  }
}

class _AutoSyncSettings extends StatefulWidget {
  @override
  State<_AutoSyncSettings> createState() => _AutoSyncSettingsState();
}

class _AutoSyncSettingsState extends State<_AutoSyncSettings> {
  late bool _autoSyncEnabled;
  late int _syncInterval;
  
  @override
  void initState() {
    super.initState();
    final storage = context.read<StorageService>();
    _autoSyncEnabled = storage.getAutoSync();
    _syncInterval = storage.getSyncInterval();
  }
  
  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: Column(
        children: [
          SwitchListTile(
            title: const Text('Auto Sync'),
            subtitle: const Text('Automatically sync with cloud'),
            value: _autoSyncEnabled,
            onChanged: (value) {
              setState(() {
                _autoSyncEnabled = value;
              });
              context.read<AlarmProvider>().setAutoSync(value);
            },
          ),
          if (_autoSyncEnabled) ...[
            const Divider(height: 1),
            ListTile(
              leading: const Icon(Icons.schedule),
              title: const Text('Sync Interval'),
              subtitle: Text('Every $_syncInterval minutes'),
              trailing: DropdownButton<int>(
                value: _syncInterval,
                underline: const SizedBox(),
                items: const [
                  DropdownMenuItem(value: 15, child: Text('15 min')),
                  DropdownMenuItem(value: 30, child: Text('30 min')),
                  DropdownMenuItem(value: 60, child: Text('1 hour')),
                  DropdownMenuItem(value: 120, child: Text('2 hours')),
                ],
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      _syncInterval = value;
                    });
                    context.read<AlarmProvider>().setSyncInterval(value);
                  }
                },
              ),
            ),
          ],
        ],
      ),
    );
  }
}
