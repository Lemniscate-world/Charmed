/// gradient_button.dart - Gradient button with accent colors
///
/// Primary action button with smooth gradient effect

import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart';

class GradientButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final Widget child;
  final double? width;
  final double? height;
  
  const GradientButton({
    Key? key,
    required this.onPressed,
    required this.child,
    this.width,
    this.height,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height ?? 56,
      decoration: BoxDecoration(
        gradient: onPressed != null
            ? AppColors.accentGradient
            : const LinearGradient(
                colors: [AppColors.textTertiary, AppColors.textTertiary],
              ),
        borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
        boxShadow: onPressed != null
            ? [
                BoxShadow(
                  color: AppColors.accent.withOpacity(0.3),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
              ]
            : null,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
          child: Center(
            child: DefaultTextStyle(
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
                letterSpacing: 0.5,
              ),
              child: child,
            ),
          ),
        ),
      ),
    );
  }
}
