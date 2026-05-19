import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../models/reconstruction_readiness.dart';
import '../models/scan_metadata.dart';
import '../models/scan_upload_result.dart';

class BackendApi {
  BackendApi({
    Dio? dio,
    FlutterSecureStorage? secureStorage,
    String? baseUrl,
  })  : _baseUrl = baseUrl ?? const String.fromEnvironment(
          'BACKEND_BASE_URL',
          defaultValue: 'http://127.0.0.1:8000',
        ),
        _secureStorage = secureStorage ?? const FlutterSecureStorage(),
        _dio = dio ?? Dio();

  static const _tokenKey = 'shoe_customizer_access_token';

  final Dio _dio;
  final FlutterSecureStorage _secureStorage;
  final String _baseUrl;
  String? _accessToken;

  Future<bool> hasStoredToken() async {
    _accessToken ??= await _secureStorage.read(key: _tokenKey);
    return _accessToken != null;
  }

  Future<void> register({
    required String name,
    required String email,
    required String password,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '$_baseUrl/api/auth/register',
      data: {
        'name': name,
        'email': email,
        'password': password,
      },
    );
    await _storeToken(response.data?['accessToken'] as String?);
  }

  Future<void> login({required String email, required String password}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '$_baseUrl/api/auth/login',
      data: {
        'email': email,
        'password': password,
      },
    );
    await _storeToken(response.data?['accessToken'] as String?);
  }

  Future<void> demoLogin() async {
    final response = await _dio.post<Map<String, dynamic>>('$_baseUrl/api/auth/demo-login');
    await _storeToken(response.data?['accessToken'] as String?);
  }

  Future<void> logout() async {
    _accessToken = null;
    await _secureStorage.delete(key: _tokenKey);
  }

  Future<String> createScanSession({required ScanMetadata metadata}) async {
    await _ensureToken();
    final response = await _dio.post<Map<String, dynamic>>(
      '$_baseUrl/api/scan-sessions',
      data: {'metadata': metadata.toJson()},
      options: _authOptions(),
    );
    return response.data?['id'] as String;
  }

  Future<ReconstructionReadiness> getReconstructionReadiness() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '$_baseUrl/api/system/reconstruction-readiness',
    );
    return ReconstructionReadiness.fromJson(response.data ?? const <String, dynamic>{});
  }

  Future<ScanUploadResult> uploadScanPass({
    required String scanSessionId,
    required String passType,
    required File videoFile,
    required void Function(int sent, int total) onProgress,
  }) async {
    await _ensureToken();
    final formData = FormData.fromMap({
      'video': await MultipartFile.fromFile(
        videoFile.path,
        filename: '$passType.mp4',
      ),
    });

    final response = await _dio.post<Map<String, dynamic>>(
      '$_baseUrl/api/scan-sessions/$scanSessionId/videos/$passType',
      data: formData,
      options: _authOptions(contentType: 'multipart/form-data'),
      onSendProgress: onProgress,
    );

    return ScanUploadResult.fromJson(response.data!);
  }

  Future<String> startProcessing({required String scanSessionId}) async {
    await _ensureToken();
    final response = await _dio.post<Map<String, dynamic>>(
      '$_baseUrl/api/scan-sessions/$scanSessionId/process',
      data: <String, dynamic>{},
      options: _authOptions(),
    );
    return response.data?['status'] as String? ?? 'uploaded';
  }

  Future<void> _storeToken(String? token) async {
    if (token == null) {
      throw Exception('Backend did not return an access token.');
    }
    _accessToken = token;
    await _secureStorage.write(key: _tokenKey, value: token);
  }

  Future<void> _ensureToken() async {
    _accessToken ??= await _secureStorage.read(key: _tokenKey);
    if (_accessToken == null) {
      throw Exception('Sign in before uploading a scan.');
    }
  }

  Options _authOptions({String? contentType}) {
    return Options(
      contentType: contentType,
      headers: {
        'Authorization': 'Bearer $_accessToken',
      },
    );
  }
}
