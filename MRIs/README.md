# MRI Data Directory

This directory contains MRI data used for subject-specific model development and validation.

## File Organization

Organize MRI data by subject:
```
MRIs/
├── Subject01/
│   ├── raw/          # Raw DICOM files
│   ├── processed/    # Processed/segmented data
│   └── metadata.txt  # Subject information
├── Subject02/
└── ...
```

## Data Types

- **Raw DICOM files**: Original MRI scans
- **Processed data**: Segmented muscle volumes, bone geometry
- **Metadata**: Subject demographics, scan parameters

## Usage

MRI data is used for:
- Subject-specific model scaling
- Muscle volume estimation
- Validation of model predictions
- Anatomical reference

## Data Privacy

Ensure all MRI data is properly de-identified and complies with institutional privacy policies.