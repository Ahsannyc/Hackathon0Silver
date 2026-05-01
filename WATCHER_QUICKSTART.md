# 🚀 File System Watcher - Quick Start (5 Minutes)

## ⚡ Installation (1 minute)

```bash
pip install watchdog
```

Verify:
```bash
python -c "import watchdog; print('✓ Ready!')"
```

---

## 🎯 Start the Watcher (30 seconds)

**Option 1: Command Line**
```bash
python watchers/filesystem_watcher.py
```

**Option 2: Windows Double-Click**
```
Double-click: watchers/START_WATCHER.bat
```

**Expected Output:**
```
======================================================================
🚀 BRONZE TIER FILE SYSTEM WATCHER - STARTING
======================================================================
📍 Project Root: C:\Users\14loa\...\Hackathon0
📂 Monitoring: C:\...\Inbox
📤 Output: C:\...\Needs_Action
⏱️  Check Interval: 5 seconds
...
✓ Watcher initialized and ready
✓ Watching for new files in /Inbox...
✓ Press Ctrl+C to stop
```

---

## 🧪 Test It (2 minutes)

**Keep the watcher running** in terminal, then open another terminal/file explorer.

### Test 1: Text File

**Create a test file in /Inbox:**
```bash
# Windows Command Prompt:
echo Hello World > Inbox\hello.txt

# Linux/Mac:
echo "Hello World" > Inbox/hello.txt
```

**Watch for output in watcher terminal** (should appear within 5 seconds):

```
======================================================================
📥 NEW FILE DETECTED IN /Inbox
======================================================================
⏰ Timestamp: 2026-02-11T14:45:22.123456
📄 Original Name: hello.txt
📊 Size: 11 bytes

📋 STEP 1: COPYING FILE
  From: C:\...\Inbox\hello.txt
  To:   C:\...\Needs_Action\FILE_hello.txt
  ✓ File copied successfully

📋 STEP 2: CREATING METADATA FILE
  Path: C:\...\Needs_Action\FILE_hello.txt.md
  ✓ Metadata file created successfully

======================================================================
✅ FILE PROCESSING COMPLETE
======================================================================
```

**Check /Needs_Action folder:**

You should see:
1. ✅ `FILE_hello.txt` (copy of your file)
2. ✅ `FILE_hello.txt.md` (metadata file)

---

### Test 2: Check Metadata File

**Open:** `Needs_Action/FILE_hello.txt.md`

**Should contain:**
```yaml
---
type: file_drop
original_name: hello.txt
size: 11
status: pending
created_at: 2026-02-11T14:45:22.123456
file_prefix: FILE_hello.txt
---

# File Drop Metadata

**Original Name:** `hello.txt`
**Size:** 11 bytes
**Status:** pending
...
```

✅ **If you see this, the watcher is working perfectly!**

---

### Test 3: Multiple Files (Bonus)

Drop 3 files rapidly:
```bash
echo file1 > Inbox\file1.txt
echo file2 > Inbox\file2.txt
echo file3 > Inbox\file3.txt
```

Watch the console process each one independently with clear separation.

---

## 📊 Expected File System After Tests

```
Project Root/
├── Inbox/                          (drop files here)
│   ├── hello.txt                   (original)
│   ├── file1.txt                   (original)
│   ├── file2.txt                   (original)
│   └── file3.txt                   (original)
│
└── Needs_Action/                   (processed files appear here)
    ├── FILE_hello.txt              ← COPY (step 1)
    ├── FILE_hello.txt.md           ← METADATA (step 2)
    ├── FILE_file1.txt
    ├── FILE_file1.txt.md
    ├── FILE_file2.txt
    ├── FILE_file2.txt.md
    ├── FILE_file3.txt
    └── FILE_file3.txt.md
```

---

## 🎯 What Happens at Each Step

| Step | Action | Result |
|------|--------|--------|
| 1 | File dropped in `/Inbox` | Watcher detects (within 5 sec) |
| 2 | Copy to `/Needs_Action` | File renamed with `FILE_` prefix |
| 3 | Create `.md` metadata | YAML frontmatter + markdown content |
| 4 | Log to console | Full processing details shown |

---

## 🛑 Stopping the Watcher

Press `Ctrl+C` in the watcher terminal:

```
======================================================================
🛑 WATCHER STOPPED BY USER
======================================================================
✓ Watcher stopped
✓ Farewell!
```

---

## ✅ Success Checklist

After completing the tests:

- [x] Watcher started without errors
- [x] Console showed startup message
- [x] Created test file in /Inbox
- [x] File appeared in /Needs_Action with FILE_ prefix (within 5 sec)
- [x] Metadata .md file was created
- [x] Metadata contains YAML frontmatter
- [x] Metadata type: `file_drop`
- [x] Console showed processing output
- [x] No errors in console

**If all checked: Watcher is working! 🎉**

---

## 📚 For More Details

- **Full setup guide:** `watchers/WATCHER_SETUP.md`
- **README:** `watchers/README.md`
- **Script source:** `watchers/filesystem_watcher.py`

---

## 🔗 Integration with Bronze Tier

After the watcher processes files, you can:

1. **Analyze files with Task Analyzer**
   ```
   @Task Analyzer
   ```

2. **Process with Basic File Handler**
   ```
   @Basic File Handler
   ```

3. **Review results in /Plans and /Pending_Approval**

---

## ⚠️ Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `watchdog not installed` | Run: `pip install watchdog` |
| Files not appearing | Wait 5 seconds, check watcher is running |
| Permission error | Check folder permissions, close locked files |
| Watcher crashes | Check Python version (3.6+), see WATCHER_SETUP.md |

---

## 🎬 You're Ready!

The File System Watcher is now:
- ✅ Installed
- ✅ Tested
- ✅ Working
- ✅ Ready for production use

**Happy monitoring! 🚀**
