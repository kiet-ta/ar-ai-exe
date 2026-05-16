class ScanMetadata {
  ScanMetadata({
    required this.sizeSystem,
    required this.size,
    required this.side,
    required this.type,
    required this.material,
    required this.condition,
    required this.lengthCm,
    required this.widthCm,
    required this.calibrationReference,
    required this.lighting,
    required this.background,
    required this.customizationGoal,
  });

  final String sizeSystem;
  final String size;
  final String side;
  final String type;
  final String material;
  final String condition;
  final double lengthCm;
  final double widthCm;
  final String calibrationReference;
  final String lighting;
  final String background;
  final List<String> customizationGoal;

  Map<String, dynamic> toJson() {
    return {
      'shoe': {
        'sizeSystem': sizeSystem,
        'size': size,
        'side': side,
        'type': type,
        'material': material,
        'condition': condition,
      },
      'measurements': {
        'lengthCm': lengthCm,
        'widthCm': widthCm,
      },
      'scanSetup': {
        'calibrationReference': calibrationReference,
        'lighting': lighting,
        'background': background,
      },
      'customizationGoal': customizationGoal,
    };
  }
}
