#!/usr/bin/env python3
"""
Bronze Tier File System Watcher - SIMPLE POLLING VERSION
=========================================================

This is a simplified version using PURE POLLING (no watchdog complexity).
It checks the /Inbox folder every 5 seconds and processes any new files.

INSTALLATION:
    pip install watchdog

USAGE:
    python watchers/filesystem_watcher_simple.py
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime


def process_file(filepath, needs_action_path):
    """Process a file: copy it and create metadata"""
    filename = filepath.name
    timestamp = datetime.now().isoformat()

    try:
        # Step 1: Copy file with prefix
        new_filename = f"FILE_{filename}"
        destination = needs_action_path / new_filename

        print(f"\n{'='*70}")
        print(f"📥 NEW FILE DETECTED IN /Inbox")
        print(f"{'='*70}")
        print(f"⏰ Timestamp: {timestamp}")
        print(f"📄 Original Name: {filename}")

        try:
            file_size = filepath.stat().st_size
            print(f"📊 Size: {file_size} bytes")
        except:
            file_size = 0

        print(f"\n📋 STEP 1: COPYING FILE")
        print(f"  From: {filepath}")
        print(f"  To:   {destination}")

        shutil.copy2(filepath, destination)
        print(f"  ✓ File copied successfully")

        # Step 2: Create metadata file
        metadata_filename = f"FILE_{filename}.md"
        metadata_path = needs_action_path / metadata_filename

        print(f"\n📋 STEP 2: CREATING METADATA FILE")
        print(f"  Filename: {metadata_filename}")
        print(f"  Path: {metadata_path}")

        yaml_frontmatter = f"""---
type: file_drop
original_name: {filename}
size: {file_size}
status: pending
created_at: {timestamp}
file_prefix: FILE_{filename}
---

# File Drop Metadata

**Original Name:** `{filename}`
**Size:** {file_size} bytes
**Status:** pending
**Created:** {timestamp}
**Destination:** `/Needs_Action/{new_filename}`

## Actions Required

- [ ] Review original file
- [ ] Determine action type
- [ ] Update status to 'processed'
- [ ] Move to /Done when complete
"""

        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(yaml_frontmatter)
            print(f"  ✓ Metadata file created successfully")
            print(f"  ✓ Size: {len(yaml_frontmatter)} bytes")
        except Exception as meta_error:
            print(f"  ❌ METADATA ERROR: {str(meta_error)}")
            raise

        # Verify files were created
        copy_exists = destination.exists()
        metadata_exists = metadata_path.exists()

        # Summary
        print(f"\n{'='*70}")
        print(f"✅ FILE PROCESSING COMPLETE")
        print(f"{'='*70}")
        print(f"📁 Original:  {filepath} (exists: {filepath.exists()})")
        print(f"📁 Copied:    {destination} (exists: {copy_exists})")
        print(f"📋 Metadata:  {metadata_path} (exists: {metadata_exists})")
        print(f"{'='*70}\n")

        if not copy_exists:
            print(f"⚠️  WARNING: Copy file was not created!\n")
        if not metadata_exists:
            print(f"⚠️  WARNING: Metadata file was not created!\n")

        return copy_exists and metadata_exists

    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERROR processing {filename}")
        print(f"{'='*70}")
        print(f"Error message: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Full traceback:")
        traceback.print_exc()
        print(f"{'='*70}\n")
        return False


def main():
    """Main polling loop"""
    # Get project root
    script_path = Path(__file__)
    project_root = script_path.parent.parent

    inbox = project_root / "Inbox"
    needs_action = project_root / "Needs_Action"

    # Create folders if missing
    inbox.mkdir(parents=True, exist_ok=True)
    needs_action.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print("🚀 BRONZE TIER FILE SYSTEM WATCHER - SIMPLE POLLING VERSION")
    print("="*70)
    print(f"📍 Project Root: {project_root}")
    print(f"📂 Monitoring: {inbox}")
    print(f"📤 Output: {needs_action}")
    print(f"⏱️  Check Interval: 5 seconds")
    print(f"🔍 Method: POLLING (checks folder every 5 seconds)")
    print("="*70)
    print(f"✓ Watcher initialized and ready")
    print(f"✓ Watching for new files in /Inbox...")
    print(f"✓ Press Ctrl+C to stop\n")

    # Track files we've already processed
    processed_files = set()

    try:
        while True:
            try:
                # Get all files in Inbox
                if inbox.exists():
                    inbox_files = [f for f in inbox.glob('*') if f.is_file()]

                    # Process new files
                    for filepath in inbox_files:
                        file_id = str(filepath)

                        # Skip if already processed
                        if file_id in processed_files:
                            continue

                        # Process the file
                        if process_file(filepath, needs_action):
                            processed_files.add(file_id)

                # Wait before checking again
                time.sleep(5)

            except Exception as e:
                print(f"⚠️  Polling error: {str(e)}")
                time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 WATCHER STOPPED BY USER")
        print("="*70)
        print(f"✓ Watcher stopped")
        print(f"✓ Farewell!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
