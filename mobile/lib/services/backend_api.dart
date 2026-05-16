import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';

import '../models/scan_metadata.dart';
import '../models/scan_upload_result.dart';

class BackendApi {
  BackendApi({
    Dio? dio,
    String? baseUrl,
  })  : _baseUrl = baseUrl ?? const String.fromEnvironment(
          'BACKEND_BASE_URL',
          defaultValue: 'http://127.0.0.1:8000',
        ),
        _dio = dio ?? Dio();

  final Dio _dio;
  final String _baseUrl;
  String? _accessToken;

  Future<void> demoLogin() async {
    final response = await _dio.post<Map<String, dynamic>>('$_baseUrl/api/auth/demo-login');
    _accessToken = response.data?['accessToken'] as String?;
    if (_accessToken == null) {
      throw Exception('Backend did not return a demo access token.');
    }
  }

  Future<String> createScanSession() async {
    await _ensureToken();
    final response = await _dio.post<Map<String, dynamic>>(
      '$_baseUrl/api/scan-sessions',
      data: <String, dynamic>{},
      options: _authOptions(),
    );
    return response.data?['id'] as String;
  }

  Future<ScanUploadResult> uploadScan({
    required String scanSessionId,
    required File videoFile,
    required ScanMetadata metadata,
    required void Function(int sent, int total) onProgress,
  }) async {
    await _ensureToken();
    final formData = FormData.fromMap({
      'metadata': jsonEncode(metadata.toJson()),
      'video': await MultipartFile.fromFile(
        videoFile.path,
        filename: 'raw_video.mp4',
      ),
    });

    final response = await _dio.post<Map<String, dynamic>>(
      '$_baseUrl/api/scan-sessions/$scanSessionId/upload-video',
      data: formData,
      options: _authOptions(contentType: 'multipart/form-data'),
      onSendProgress: onProgress,
    );

    return ScanUploadResult.fromJson(response.data!);
  }

  Future<void> _ensureToken() async {
    if (_accessToken == null) {
      await demoLogin();
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
