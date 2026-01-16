/// alarm_edit_screen.dart - Create/edit alarm screen
///
/// Provides full alarm editing with time, playlist, volume, fade-in, and days

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/alarm.dart';
import '../providers/alarm_provider.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/gradient_button.dart';
import '../widgets/day_selector.dart';
import 'package:intl/intl.dart';

class AlarmEditScreen extends StatefulWidget {
  final Alarm? alarm;
  
  const AlarmEditScreen({Key? key, this.alarm}) : super(key: key);
  
  @override
  State<AlarmEditScreen> createState() => _AlarmEditScreenState();
}

class _AlarmEditScreenState extends State<AlarmEditScreen> {
  late TimeOfDay _selectedTime;
  late String _playlistName;
  late String _playlistUri;
  late int _volume;
  late bool _fadeInEnabled;
  late int _fadeInDuration;
  late List<String> _selectedDays;
  late bool _isActive;
  
  bool get _isEditMode => widget.alarm != null;
  
  @override
  void initState() {
    super.initState();
    
    if (_isEditMode) {
      final alarm = widget.alarm!;
      final timeParts = alarm.time.split(':');
      _selectedTime = TimeOfDay(
        hour: int.parse(timeParts[0]),
        minute: int.parse(timeParts[1]),
      );
      _playlistName = alarm.playlistName;
      _playlistUri = alarm.playlistUri;
      _volume = alarm.volume;
      _fadeInEnabled = alarm.fadeInEnabled;
      _fadeInDuration = alarm.fadeInDuration;
      _selectedDays = List.from(alarm.days);
      _isActive = alarm.isActive;
    } else {
      _selectedTime = TimeOfDay.now();
      _playlistName = 'Morning Vibes';
      _playlistUri = 'spotify:playlist:example';
      _volume = 80;
      _fadeInEnabled = false;
      _fadeInDuration = 10;
      _selectedDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
      _isActive = true;
    }
  }
  
  Future<void> _selectTime() async {
    final TimeOfDay? time = await showTimePicker(
      context: context,
      initialTime: _selectedTime,
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            timePickerTheme: TimePickerThemeData(
              backgroundColor: AppColors.card,
              dialBackgroundColor: AppColors.surface,
              hourMinuteTextColor: AppColors.textPrimary,
              dayPeriodTextColor: AppColors.textPrimary,
            ),
          ),
          child: child!,
        );
      },
    );
    
    if (time != null) {
      setState(() {
        _selectedTime = time;
      });
    }
  }
  
  void _saveAlarm() {
    final timeString = '${_selectedTime.hour.toString().padLeft(2, '0')}:${_selectedTime.minute.toString().padLeft(2, '0')}';
    
    final alarm = Alarm(
      id: _isEditMode ? widget.alarm!.id : DateTime.now().millisecondsSinceEpoch.toString(),
      time: timeString,
      playlistName: _playlistName,
      playlistUri: _playlistUri,
      volume: _volume,
      fadeInEnabled: _fadeInEnabled,
      fadeInDuration: _fadeInDuration,
      days: _selectedDays,
      isActive: _isActive,
      lastModified: DateTime.now(),
      createdAt: _isEditMode ? widget.alarm!.createdAt : DateTime.now(),
    );
    
    final alarmProvider = context.read<AlarmProvider>();
    
    if (_isEditMode) {
      alarmProvider.updateAlarm(widget.alarm!.id, alarm);
    } else {
      alarmProvider.addAlarm(alarm);
    }
    
    Navigator.pop(context);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditMode ? 'Edit Alarm' : 'New Alarm'),
        actions: [
          TextButton(
            onPressed: _saveAlarm,
            child: Text(
              'Save',
              style: TextStyle(
                color: AppColors.accent,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppTheme.spacingMedium),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Time picker
            GlassCard(
              child: InkWell(
                onTap: _selectTime,
                borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
                child: Padding(
                  padding: const EdgeInsets.all(AppTheme.spacingLarge),
                  child: Column(
                    children: [
                      Text(
                        'Alarm Time',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: AppTheme.spacingSmall),
                      Text(
                        _formatTime(_selectedTime),
                        style: Theme.of(context).textTheme.displayLarge?.copyWith(
                          fontFamily: 'JetBrainsMono',
                          fontSize: 64,
                          fontWeight: FontWeight.bold,
                          color: AppColors.accent,
                        ),
                      ),
                      const SizedBox(height: AppTheme.spacingSmall),
                      Text(
                        'Tap to change',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),
            ),
            
            const SizedBox(height: AppTheme.spacingMedium),
            
            // Days selector
            GlassCard(
              child: Padding(
                padding: const EdgeInsets.all(AppTheme.spacingLarge),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Repeat',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: AppTheme.spacingMedium),
                    DaySelector(
                      selectedDays: _selectedDays,
                      onDaysChanged: (days) {
                        setState(() {
                          _selectedDays = days;
                        });
                      },
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: AppTheme.spacingMedium),
            
            // Playlist (placeholder - would integrate with Spotify API)
            GlassCard(
              child: ListTile(
                leading: const Icon(Icons.music_note, color: AppColors.accent),
                title: const Text('Playlist'),
                subtitle: Text(_playlistName),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  // TODO: Open playlist selector
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Playlist selection coming soon'),
                    ),
                  );
                },
              ),
            ),
            
            const SizedBox(height: AppTheme.spacingMedium),
            
            // Volume control
            GlassCard(
              child: Padding(
                padding: const EdgeInsets.all(AppTheme.spacingLarge),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Volume',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        Text(
                          '$_volume%',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: AppColors.accent,
                            fontFamily: 'JetBrainsMono',
                          ),
                        ),
                      ],
                    ),
                    Slider(
                      value: _volume.toDouble(),
                      min: 0,
                      max: 100,
                      divisions: 20,
                      onChanged: (value) {
                        setState(() {
                          _volume = value.toInt();
                        });
                      },
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: AppTheme.spacingMedium),
            
            // Fade-in settings
            GlassCard(
              child: Column(
                children: [
                  SwitchListTile(
                    title: const Text('Fade-in'),
                    subtitle: const Text('Gradually increase volume'),
                    value: _fadeInEnabled,
                    onChanged: (value) {
                      setState(() {
                        _fadeInEnabled = value;
                      });
                    },
                  ),
                  if (_fadeInEnabled) ...[
                    const Divider(height: 1),
                    Padding(
                      padding: const EdgeInsets.all(AppTheme.spacingLarge),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Duration',
                                style: Theme.of(context).textTheme.titleSmall,
                              ),
                              Text(
                                '$_fadeInDuration min',
                                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  color: AppColors.accent,
                                  fontFamily: 'JetBrainsMono',
                                ),
                              ),
                            ],
                          ),
                          Slider(
                            value: _fadeInDuration.toDouble(),
                            min: 5,
                            max: 30,
                            divisions: 5,
                            onChanged: (value) {
                              setState(() {
                                _fadeInDuration = value.toInt();
                              });
                            },
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  String _formatTime(TimeOfDay time) {
    final hour = time.hourOfPeriod == 0 ? 12 : time.hourOfPeriod;
    final minute = time.minute.toString().padLeft(2, '0');
    final period = time.period == DayPeriod.am ? 'AM' : 'PM';
    return '$hour:$minute $period';
  }
}
