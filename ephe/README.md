# Swiss Ephemeris Data Directory

This directory should contain the Swiss Ephemeris data files for astronomical calculations.

## Required Files:
- `semo_18.se1` - Main ephemeris file for planets (1800-2399)
- `seas_18.se1` - Asteroid ephemeris file  
- `semo_xx.se1` - Additional century files as needed
- `fixstars.cat` - Fixed stars catalog

## Download Instructions:

1. **Option 1: Download from Swiss Ephemeris official site**
   - Visit: https://www.astro.com/ftp/swisseph/ephe/
   - Download required .se1 files for your date range
   - Most common: `semo_18.se1` (covers 1800-2399)

2. **Option 2: Automatic download via pyephem**
   ```python
   import swisseph as swe
   swe.set_ephe_path('./ephe')  # Will auto-download needed files
   ```

## File Descriptions:

- **semo_18.se1**: Main planetary ephemeris (18th to 24th century)
- **semo_xx.se1**: Century-specific files (xx = century number)
- **seas_18.se1**: Asteroid and lunar apogee data
- **fixstars.cat**: Fixed star positions catalog

## Size Information:
- Main files are typically 5-50MB each
- Total recommended download: ~200MB for comprehensive coverage
- Minimum required: semo_18.se1 (~45MB) for basic planetary calculations

## Usage:
The Swiss Ephemeris will automatically locate and use these files when calculating planetary positions, houses, and other astronomical data for chart generation.

## Note:
Without these files, the API will not be able to perform accurate astronomical calculations. Ensure at least `semo_18.se1` is present for the API to function properly.