import 'dart:async';
import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import '../models/scan_metadata.dart';
import '../widgets/scan_guide_overlay.dart';
import 'upload_progress_screen.dart';

class CameraScanScreen extends StatefulWidget {
  const CameraScanScreen({required this.metadata, super.key});

  final ScanMetadata metadata;

  @override
  State<CameraScanScreen> createState() => _CameraScanScreenState();
}

class _CameraScanScreenState extends State<CameraScanScreen> {
  CameraController? _controller;
  Timer? _timer;
  int _seconds = 0;
  bool _isRecording = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller?.dispose();
    super.dispose();
  }

  Future<void> _initializeCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        setState(() => _error = 'No camera found on this device.');
        return;
      }
      final controller = CameraController(cameras.first, ResolutionPreset.high);
      await controller.initialize();
      setState(() => _controller = controller);
    } catch (error) {
      setState(() => _error = 'Camera initialization failed: $error');
    }
  }

  @override
  Widget build(BuildContext context) {
    final controller = _controller;
    return Scaffold(
      appBar: AppBar(title: const Text('Guided scan')),
      body: SafeArea(
        child: _error != null
            ? Center(child: Text(_error!))
            : controller == null || !controller.value.isInitialized
                ? const Center(child: CircularProgressIndicator())
                : Stack(
                    children: [
                      Positioned.fill(child: CameraPreview(controller)),
                      Positioned.fill(
                        child: ScanGuideOverlay(
                          seconds: _seconds,
                          isRecording: _isRecording,
                        ),
                      ),
                      Positioned(
                        left: 16,
                        right: 16,
                        bottom: 24,
                        child: FilledButton.icon(
                          onPressed: _isRecording ? _stopRecording : _startRecording,
                          icon: Icon(_isRecording ? Icons.stop : Icons.fiber_manual_record),
                          label: Text(_isRecording ? 'Stop recording' : 'Start recording'),
                        ),
                      ),
                    ],
                  ),
      ),
    );
  }

  Future<void> _startRecording() async {
    final controller = _controller;
    if (controller == null || _isRecording) {
      return;
    }
    await controller.startVideoRecording();
    setState(() {
      _isRecording = true;
      _seconds = 0;
    });
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      setState(() => _seconds += 1);
    });
  }

  Future<void> _stopRecording() async {
    final controller = _controller;
    if (controller == null || !_isRecording) {
      return;
    }
    _timer?.cancel();
    final video = await controller.stopVideoRecording();
    setState(() => _isRecording = false);
    if (!mounted) {
      return;
    }
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => UploadProgressScreen(
          metadata: widget.metadata,
          videoFile: File(video.path),
        ),
      ),
    );
  }
}
