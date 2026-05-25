# BIOS Repair Tool - GUI Application

**For ideapad/thinkbook BIOS repair and extraction**

## Features

- File selection (EXE/BIN)
- Multiple repair methods (HnO, Z6, Temp, Auto)
- DMI detection and extraction
- Automatic backup before repair
- Padding support
- File output management
- Detailed progress logging
- Results table with file info

## Installation

### Requirements
- Python 3.6+
- tkinter (usually included with Python)

### Install Dependencies
```bash
# No external dependencies needed!
# tkinter comes with Python by default
```

## Usage

### Run the Tool
```bash
python bios_repair_tool.py
```

### Steps

1. **Select BIOS File**
   - Click "EXE" or "BIN" button
   - Choose your BIOS file

2. **Configure Options**
   - Select repair method (HnO/Z6/Temp/Auto)
   - Enable padding if needed
   - Set timeout value

3. **Set Output Directory**
   - Default: ~/BIOS_Repair_Output
   - Click "Browse" to change location

4. **Run Repair**
   - Click "Repair Original File" or "Extract Only"
   - Monitor progress in log

5. **Check Results**
   - View all output files in results table
   - Double-click to open files
   - Files saved with timestamps

## File Output

All files are saved in output directory:

- `FILENAME_BACKUP_YYYYMMDD_HHMMSS.bin` - Backup of original
- `FILENAME_REPAIRED_YYYYMMDD_HHMMSS.bin` - Repaired BIOS
- `FILENAME_EXTRACTED_YYYYMMDD_HHMMSS.bin` - Extracted data
- `DMI_DATA_YYYYMMDD_HHMMSS.json` - DMI information

## Options

### Repair Methods
- **HnO Extract**: Standard extraction algorithm
- **Z6 Extract**: Z6 extraction algorithm
- **Temp Extract**: Temporary extraction algorithm
- **Auto Process**: Automatic selection

### Features
- **Use Padding**: Add padding to file size
- **Detect DMI**: Extract DMI data from BIOS
- **Move DMI**: Transfer DMI to repaired file
- **TimeOut**: Set processing timeout

## Screenshots

- File Selection Section
- Repair Options with multiple methods
- DMI Management
- Progress Logging
- File Results Table

## Keyboard Shortcuts

- Double-click on result table to open file
- "Open Output Folder" button to access saved files

## Troubleshooting

### File not copying
- Save the raw file from GitHub
- Use right-click "Save As"

### Permission denied
- Run as administrator (Windows)
- Check folder permissions (Linux/Mac)

### DMI not detected
- Verify BIOS file format
- Try different repair method

## Support

For issues or questions, please contact the developer.

## License

This tool is provided as-is for educational purposes.

## Version

Current Version: 1.0.0
Last Updated: 2026-05-25

---

**Author**: hariszubaida47-sudo  
**Repository**: https://github.com/hariszubaida47-sudo/bios
