import 'package:flutter/material.dart';

import 'screens/scan_setup_screen.dart';

void main() {
  runApp(const ShoeScannerApp());
}

class ShoeScannerApp extends StatelessWidget {
  const ShoeScannerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Shoe Scanner',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1F6F8B)),
        useMaterial3: true,
      ),
      home: const ScanSetupScreen(),
    );
  }
}
