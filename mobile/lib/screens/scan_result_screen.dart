import 'package:flutter/material.dart';

class ScanResultScreen extends StatelessWidget {
  const ScanResultScreen({
    required this.scanSessionId,
    required this.status,
    required this.processingStarted,
    super.key,
  });

  final String scanSessionId;
  final String status;
  final bool processingStarted;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan uploaded')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Scan session ID', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            SelectableText(scanSessionId),
            const SizedBox(height: 24),
            Text('Status', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Text(status),
            const SizedBox(height: 24),
            Text(
              processingStarted
                  ? 'Uploaded successfully. Backend processing has started.'
                  : 'Uploaded successfully. Processing has not started yet.',
            ),
            const Spacer(),
            FilledButton.icon(
              onPressed: () => Navigator.of(context).popUntil((route) => route.isFirst),
              icon: const Icon(Icons.add_a_photo_outlined),
              label: const Text('Scan another shoe'),
            ),
          ],
        ),
      ),
    );
  }
}
