/// sync_indicator.dart - Cloud sync status indicator
///
/// Shows sync status banner at top of screen

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/alarm_provider.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class SyncIndicator extends StatelessWidget {
  const SyncIndicator({Key? key}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Consumer<AlarmProvider>(
      builder: (context, alarmProvider, _) {
        final status = alarmProvider.syncStatus;
        final message = alarmProvider.syncMessage;
        
        if (status == SyncStatus.idle || message == null) {
          return const SizedBox.shrink();
        }
        
        Color backgroundColor;
        IconData icon;
        
        switch (status) {
          case SyncStatus.syncing:
            backgroundColor = AppColors.accent.withOpacity(0.2);
            icon = Icons.cloud_sync;
            break;
          case SyncStatus.success:
            backgroundColor = AppColors.success.withOpacity(0.2);
            icon = Icons.cloud_done;
            break;
          case SyncStatus.error:
            backgroundColor = AppColors.alert.withOpacity(0.2);
            icon = Icons.cloud_off;
            break;
          default:
            return const SizedBox.shrink();
        }
        
        return AnimatedContainer(
          duration: AppTheme.animationNormal,
          width: double.infinity,
          padding: const EdgeInsets.symmetric(
            horizontal: AppTheme.spacingMedium,
            vertical: AppTheme.spacingSmall,
          ),
          color: backgroundColor,
          child: Row(
            children: [
              if (status == SyncStatus.syncing)
                const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.accent),
                  ),
                )
              else
                Icon(
                  icon,
                  size: 16,
                  color: status == SyncStatus.success
                      ? AppColors.success
                      : status == SyncStatus.error
                          ? AppColors.alert
                          : AppColors.accent,
                ),
              const SizedBox(width: AppTheme.spacingSmall),
              Expanded(
                child: Text(
                  message,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.textPrimary,
                  ),
                ),
              ),
              if (status != SyncStatus.syncing)
                IconButton(
                  icon: const Icon(Icons.close, size: 16),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  onPressed: () {
                    alarmProvider.clearSyncMessage();
                  },
                ),
            ],
          ),
        );
      },
    );
  }
}
