# Bronze Tier File System Watcher

**Real-time file monitoring and processing system for Bronze Tier.**

## Quick Start

### 1. Install Dependencies
```bash
pip install watchdog
```

### 2. Start Watcher
```bash
python filesystem_watcher.py
```

Or on Windows, double-click: `START_WATCHER.bat`

### 3. Drop Files in /Inbox
Files are automatically:
- Copied to `/Needs_Action` with `FILE_` prefix
- Documented with `.md` metadata files
- Tagged with YAML frontmatter (type, size, status)

## Files in This Directory

| File | Purpose |
|------|---------|
| `filesystem_watcher.py` | Main watcher script |
| `START_WATCHER.bat` | Windows launcher |
| `WATCHER_SETUP.md` | Complete setup & testing guide |
| `README.md` | This file |

## What It Does

### Input
- Monitors `/Inbox` folder
- Triggers on new file creation
- Check interval: 5 seconds

### Processing
1. **Copy**: File → `/Needs_Action/FILE_[original_name]`
2. **Metadata**: Create `.md` with YAML frontmatter
3. **Status**: Mark as `pending` for task analysis

### Output
```
/Needs_Action/
├── FILE_document.pdf         ← Copied file
└── FILE_document.pdf.md      ← Metadata with YAML frontmatter
```

## Metadata File Example

```yaml
---
type: file_drop
original_name: report.xlsx
size: 24576
status: pending
created_at: 2026-02-11T14:30:22.123456
file_prefix: FILE_report.xlsx
---

# File Drop Metadata

**Original Name:** `report.xlsx`
**Size:** 24576 bytes
**Status:** pending
**Created:** 2026-02-11T14:30:22.123456
**Destination:** `/Needs_Action/FILE_report.xlsx`

## Actions Required

- [ ] Review original file
- [ ] Determine action type
- [ ] Update status to 'processed'
- [ ] Move to /Done when complete
```

## Testing

### Simple Test
```bash
# Terminal 1: Start watcher
python filesystem_watcher.py

# Terminal 2: Create test file
echo "test content" > Inbox/test.txt

# Check Terminal 1 for processing output
# Check Needs_Action folder for results
```

### Expected Result
- ✓ `FILE_test.txt` appears in `/Needs_Action`
- ✓ `FILE_test.txt.md` appears in `/Needs_Action`
- ✓ Console shows complete processing log
- ✓ Processing completes in <1 second

## Features

- ✅ Real-time monitoring (5-second checks)
- ✅ Automatic file copying with prefix
- ✅ YAML frontmatter metadata
- ✅ Error handling (graceful failure)
- ✅ Console logging
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Batch file processing
- ✅ No external dependencies besides watchdog

## Stopping the Watcher

Press `Ctrl+C` in the terminal.

## Troubleshooting

**watchdog not installed?**
```bash
pip install watchdog
```

**No files appearing in /Needs_Action?**
- Ensure watcher is running (should see startup message)
- Check file was dropped in /Inbox (not /Needs_Action)
- Wait 5+ seconds
- Check console for errors

**Permission denied?**
- Ensure you have write access to /Inbox and /Needs_Action
- Close other applications that might lock files

See `WATCHER_SETUP.md` for comprehensive troubleshooting.

## Integration with Bronze Tier

After files are processed by the watcher:

1. **Run Basic File Handler skill**
   ```
   @Basic File Handler
   ```

2. **Run Task Analyzer skill**
   ```
   @Task Analyzer
   ```

3. **Review in /Plans and /Pending_Approval**

## Performance

- Processing time: <100ms per file
- Memory usage: ~30MB
- CPU impact: Minimal
- Handles multiple files in batch
- Gracefully recovers from errors

## Console Output Example

```
======================================================================
🚀 BRONZE TIER FILE SYSTEM WATCHER - STARTING
======================================================================
📍 Project Root: C:\Users\14loa\Desktop\IT\GIAIC\Q4 spec kit\Hackathon0
📂 Monitoring: C:\...\Inbox
📤 Output: C:\...\Needs_Action
⏱️  Check Interval: 5 seconds
🔍 Event Handler: BronzeTierFileHandler
======================================================================
✓ Watcher initialized and ready
✓ Watching for new files in /Inbox...
✓ Press Ctrl+C to stop

======================================================================
📥 NEW FILE DETECTED IN /Inbox
======================================================================
⏰ Timestamp: 2026-02-11T14:35:45.123456
📄 Original Name: report.pdf
📊 Size: 1024567 bytes

📋 STEP 1: COPYING FILE
  From: C:\...\Inbox\report.pdf
  To:   C:\...\Needs_Action\FILE_report.pdf
  ✓ File copied successfully

📋 STEP 2: CREATING METADATA FILE
  Path: C:\...\Needs_Action\FILE_report.pdf.md
  ✓ Metadata file created successfully

======================================================================
✅ FILE PROCESSING COMPLETE
======================================================================
📁 Original file: C:\...\Inbox\report.pdf
📁 Copied to: C:\...\Needs_Action\FILE_report.pdf
📋 Metadata: C:\...\Needs_Action\FILE_report.pdf.md
======================================================================
```

## Need Help?

- See `WATCHER_SETUP.md` for detailed testing guide
- Check console output for error messages
- Verify folder structure: /Inbox, /Needs_Action, /Plans, /Done, /Logs
- Ensure watchdog is installed: `pip install watchdog`

---

**Watcher is part of the Bronze Tier automation suite.** 🚀
