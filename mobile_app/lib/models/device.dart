/// device.dart - Device information model
///
/// Represents a registered device in the cloud sync system

import 'package:json_annotation/json_annotation.dart';

part 'device.g.dart';

@JsonSerializable()
class Device {
  final String deviceId;
  final String deviceName;
  final String deviceType;  // 'windows', 'mac', 'linux', 'android', 'ios'
  final DateTime? registeredAt;
  final DateTime? lastSync;
  
  Device({
    required this.deviceId,
    required this.deviceName,
    required this.deviceType,
    this.registeredAt,
    this.lastSync,
  });
  
  factory Device.fromJson(Map<String, dynamic> json) => _$DeviceFromJson(json);
  
  Map<String, dynamic> toJson() => _$DeviceToJson(this);
  
  String get typeIcon {
    switch (deviceType.toLowerCase()) {
      case 'windows':
        return '🖥️';
      case 'mac':
        return '💻';
      case 'linux':
        return '🐧';
      case 'android':
        return '📱';
      case 'ios':
        return '📱';
      default:
        return '💾';
    }
  }
  
  String get lastSyncFormatted {
    if (lastSync == null) return 'Never synced';
    
    final now = DateTime.now();
    final difference = now.difference(lastSync!);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${(difference.inDays / 7).floor()}w ago';
    }
  }
  
  @override
  String toString() {
    return 'Device(id: $deviceId, name: $deviceName, type: $deviceType)';
  }
}
