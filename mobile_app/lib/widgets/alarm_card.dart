/// alarm_card.dart - Alarm display card widget
///
/// Shows alarm information with toggle and actions

import 'package:flutter/material.dart';
import '../models/alarm.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';
import 'glass_card.dart';

class AlarmCard extends StatelessWidget {
  final Alarm alarm;
  final VoidCallback? onTap;
  final VoidCallback? onToggle;
  final VoidCallback? onDelete;
  
  const AlarmCard({
    Key? key,
    required this.alarm,
    this.onTap,
    this.onToggle,
    this.onDelete,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return GlassCard(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacingMedium),
        child: Row(
          children: [
            // Time and info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Time
                  Text(
                    alarm.formattedTime,
                    style: Theme.of(context).textTheme.displaySmall?.copyWith(
                      fontFamily: 'JetBrainsMono',
                      fontSize: 40,
                      fontWeight: FontWeight.bold,
                      color: alarm.isActive
                          ? AppColors.textPrimary
                          : AppColors.textTertiary,
                    ),
                  ),
                  const SizedBox(height: AppTheme.spacingSmall),
                  
                  // Playlist
                  Row(
                    children: [
                      Icon(
                        Icons.music_note,
                        size: 16,
                        color: alarm.isActive
                            ? AppColors.accent
                            : AppColors.textTertiary,
                      ),
                      const SizedBox(width: AppTheme.spacingXSmall),
                      Expanded(
                        child: Text(
                          alarm.playlistName,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: alarm.isActive
                                ? AppColors.textSecondary
                                : AppColors.textTertiary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: AppTheme.spacingXSmall),
                  
                  // Days
                  Text(
                    alarm.dayAbbreviations,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      fontFamily: 'JetBrainsMono',
                      color: alarm.isActive
                          ? AppColors.textTertiary
                          : AppColors.textDisabled,
                      letterSpacing: 2,
                    ),
                  ),
                  
                  // Fade-in indicator
                  if (alarm.fadeInEnabled) ...[
                    const SizedBox(height: AppTheme.spacingXSmall),
                    Row(
                      children: [
                        Icon(
                          Icons.trending_up,
                          size: 12,
                          color: alarm.isActive
                              ? AppColors.textTertiary
                              : AppColors.textDisabled,
                        ),
                        const SizedBox(width: AppTheme.spacingXSmall),
                        Text(
                          'Fade-in ${alarm.fadeInDuration}min',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            fontSize: 10,
                            color: alarm.isActive
                                ? AppColors.textTertiary
                                : AppColors.textDisabled,
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            
            // Toggle switch
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Switch(
                  value: alarm.isActive,
                  onChanged: (_) => onToggle?.call(),
                ),
                
                // Delete button
                if (onDelete != null) ...[
                  const SizedBox(height: AppTheme.spacingSmall),
                  IconButton(
                    icon: const Icon(Icons.delete_outline),
                    color: AppColors.alert,
                    iconSize: 20,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                    onPressed: onDelete,
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}
