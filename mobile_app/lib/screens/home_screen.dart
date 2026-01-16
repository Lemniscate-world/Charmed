/// home_screen.dart - Main alarm list screen
///
/// Displays all alarms with filtering and provides navigation to edit/add

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/alarm_provider.dart';
import '../providers/auth_provider.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';
import '../widgets/alarm_card.dart';
import '../widgets/sync_indicator.dart';
import 'alarm_edit_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);
  
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _showInactive = false;
  
  @override
  void initState() {
    super.initState();
    // Trigger initial sync if needed
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final alarmProvider = context.read<AlarmProvider>();
      if (alarmProvider.alarms.isEmpty) {
        alarmProvider.syncAlarms();
      }
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Alarmify'),
        actions: [
          // Sync button
          IconButton(
            icon: const Icon(Icons.cloud_sync_outlined),
            onPressed: () {
              context.read<AlarmProvider>().syncAlarms();
            },
          ),
          
          // Settings button
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const SettingsScreen(),
                ),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Sync indicator
          const SyncIndicator(),
          
          // Filter tabs
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppTheme.spacingMedium,
              vertical: AppTheme.spacingSmall,
            ),
            child: Row(
              children: [
                Expanded(
                  child: _FilterChip(
                    label: 'Active',
                    selected: !_showInactive,
                    onTap: () {
                      setState(() {
                        _showInactive = false;
                      });
                    },
                  ),
                ),
                const SizedBox(width: AppTheme.spacingSmall),
                Expanded(
                  child: _FilterChip(
                    label: 'Inactive',
                    selected: _showInactive,
                    onTap: () {
                      setState(() {
                        _showInactive = true;
                      });
                    },
                  ),
                ),
              ],
            ),
          ),
          
          // Alarm list
          Expanded(
            child: Consumer<AlarmProvider>(
              builder: (context, alarmProvider, _) {
                final alarms = _showInactive
                    ? alarmProvider.inactiveAlarms
                    : alarmProvider.activeAlarms;
                
                if (alarms.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          _showInactive
                              ? Icons.alarm_off_outlined
                              : Icons.alarm_add_outlined,
                          size: 80,
                          color: AppColors.textTertiary,
                        ),
                        const SizedBox(height: AppTheme.spacingMedium),
                        Text(
                          _showInactive
                              ? 'No inactive alarms'
                              : 'No alarms yet',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: AppTheme.spacingSmall),
                        Text(
                          _showInactive
                              ? 'Disabled alarms will appear here'
                              : 'Tap + to create your first alarm',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppColors.textTertiary,
                          ),
                        ),
                      ],
                    ),
                  );
                }
                
                return ListView.separated(
                  padding: const EdgeInsets.all(AppTheme.spacingMedium),
                  itemCount: alarms.length,
                  separatorBuilder: (context, index) => const SizedBox(
                    height: AppTheme.spacingMedium,
                  ),
                  itemBuilder: (context, index) {
                    final alarm = alarms[index];
                    return AlarmCard(
                      alarm: alarm,
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => AlarmEditScreen(alarm: alarm),
                          ),
                        );
                      },
                      onToggle: () {
                        alarmProvider.toggleAlarm(alarm.id);
                      },
                      onDelete: () {
                        _showDeleteDialog(context, alarm.id);
                      },
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const AlarmEditScreen(),
            ),
          );
        },
        backgroundColor: AppColors.accent,
        child: const Icon(Icons.add, color: AppColors.textPrimary),
      ),
    );
  }
  
  void _showDeleteDialog(BuildContext context, String alarmId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Alarm'),
        content: const Text('Are you sure you want to delete this alarm?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              context.read<AlarmProvider>().deleteAlarm(alarmId);
              Navigator.pop(context);
            },
            child: const Text(
              'Delete',
              style: TextStyle(color: AppColors.alert),
            ),
          ),
        ],
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  
  const _FilterChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });
  
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: AppTheme.animationNormal,
        padding: const EdgeInsets.symmetric(
          horizontal: AppTheme.spacingMedium,
          vertical: AppTheme.spacingSmall,
        ),
        decoration: BoxDecoration(
          color: selected ? AppColors.accent : AppColors.surface,
          borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
          border: Border.all(
            color: selected ? AppColors.accent : AppColors.border,
            width: 2,
          ),
        ),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            color: selected ? AppColors.textPrimary : AppColors.textSecondary,
            fontWeight: selected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}
