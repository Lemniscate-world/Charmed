/// day_selector.dart - Day of week selector widget
///
/// Allows selection of active days for recurring alarms

import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class DaySelector extends StatelessWidget {
  final List<String> selectedDays;
  final ValueChanged<List<String>> onDaysChanged;
  
  const DaySelector({
    Key? key,
    required this.selectedDays,
    required this.onDaysChanged,
  }) : super(key: key);
  
  static const List<Map<String, String>> _days = [
    {'name': 'Monday', 'abbr': 'M'},
    {'name': 'Tuesday', 'abbr': 'T'},
    {'name': 'Wednesday', 'abbr': 'W'},
    {'name': 'Thursday', 'abbr': 'T'},
    {'name': 'Friday', 'abbr': 'F'},
    {'name': 'Saturday', 'abbr': 'S'},
    {'name': 'Sunday', 'abbr': 'S'},
  ];
  
  void _toggleDay(String day) {
    final newDays = List<String>.from(selectedDays);
    
    if (newDays.contains(day)) {
      newDays.remove(day);
    } else {
      newDays.add(day);
    }
    
    onDaysChanged(newDays);
  }
  
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: _days.map((day) {
        final dayName = day['name']!;
        final isSelected = selectedDays.contains(dayName);
        
        return _DayChip(
          label: day['abbr']!,
          selected: isSelected,
          onTap: () => _toggleDay(dayName),
        );
      }).toList(),
    );
  }
}

class _DayChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  
  const _DayChip({
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
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: selected ? AppColors.accent : AppColors.surface,
          shape: BoxShape.circle,
          border: Border.all(
            color: selected ? AppColors.accent : AppColors.border,
            width: 2,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              fontFamily: 'JetBrainsMono',
              color: selected ? AppColors.textPrimary : AppColors.textTertiary,
            ),
          ),
        ),
      ),
    );
  }
}
