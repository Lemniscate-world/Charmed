/// user.dart - User account data model
///
/// Represents authenticated user with cloud sync credentials

import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String userId;
  final String email;
  final String displayName;
  final DateTime? createdAt;
  final DateTime? lastLogin;
  
  User({
    required this.userId,
    required this.email,
    required this.displayName,
    this.createdAt,
    this.lastLogin,
  });
  
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  
  Map<String, dynamic> toJson() => _$UserToJson(this);
  
  @override
  String toString() {
    return 'User(userId: $userId, email: $email, displayName: $displayName)';
  }
}

@JsonSerializable()
class AuthTokens {
  final String accessToken;
  final String refreshToken;
  final DateTime? expiresAt;
  
  AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    this.expiresAt,
  });
  
  factory AuthTokens.fromJson(Map<String, dynamic> json) => _$AuthTokensFromJson(json);
  
  Map<String, dynamic> toJson() => _$AuthTokensToJson(this);
  
  bool get isExpired {
    if (expiresAt == null) return false;
    return DateTime.now().isAfter(expiresAt!);
  }
}
