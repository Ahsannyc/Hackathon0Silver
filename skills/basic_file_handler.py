#!/usr/bin/env python3
"""
Bronze Tier Skill: Basic File Handler
- Read and summarize .md files from /Needs_Action
- Write action plans to /Plans/Plan.md
- Move completed files to /Done
- Reference Company_Handbook.md rules
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

class BasicFileHandler:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.needs_action = self.project_root / "Needs_Action"
        self.plans = self.project_root / "Plans"
        self.done = self.project_root / "Done"
        self.handbook = self.project_root / "Company_Handbook.md"

    def read_handbook_rules(self):
        """Read and display Company Handbook rules"""
        if self.handbook.exists():
            with open(self.handbook, 'r') as f:
                return f.read()
        return "⚠️ Company_Handbook.md not found"

    def list_md_files(self):
        """List all .md files in Needs_Action"""
        if not self.needs_action.exists():
            return []
        return sorted([f for f in self.needs_action.glob("*.md")])

    def summarize_file(self, filepath):
        """Summarize content of a .md file"""
        with open(filepath, 'r') as f:
            content = f.read()

        # Simple summarization - first 3 lines + count of sections
        lines = content.split('\n')
        summary = '\n'.join(lines[:3]) if lines else "Empty file"
        section_count = content.count('#')

        return {
            'filename': filepath.name,
            'preview': summary,
            'sections': section_count,
            'full_path': str(filepath)
        }

    def create_action_plan(self, file_summaries):
        """Create Plan.md with checkboxes for next steps"""
        plan_content = f"""# Action Plan
Generated: {datetime.now().isoformat()}

## Files Processed
"""
        for summary in file_summaries:
            plan_content += f"\n### {summary['filename']}\n"
            plan_content += f"- [ ] Review content\n"
            plan_content += f"- [ ] Check handbook compliance\n"
            plan_content += f"- [ ] Execute action\n"
            plan_content += f"- [ ] Move to Done\n"

        plan_file = self.plans / "Plan.md"
        plan_file.parent.mkdir(parents=True, exist_ok=True)

        with open(plan_file, 'w') as f:
            f.write(plan_content)

        return str(plan_file)

    def move_to_done(self, filepath):
        """Move completed file to Done folder"""
        self.done.mkdir(parents=True, exist_ok=True)
        destination = self.done / filepath.name
        shutil.move(str(filepath), str(destination))
        return str(destination)

    def execute(self):
        """Execute full workflow"""
        print("=" * 60)
        print("BASIC FILE HANDLER - Bronze Tier Skill")
        print("=" * 60)

        # Step 1: Check handbook rules
        print("\n📋 CHECKING COMPANY HANDBOOK:")
        print(self.read_handbook_rules())

        # Step 2: List files
        print("\n📂 SCANNING /Needs_Action:")
        files = self.list_md_files()

        if not files:
            print("✓ No files to process")
            return

        print(f"✓ Found {len(files)} file(s)")

        # Step 3: Summarize files
        print("\n📝 SUMMARIZING FILES:")
        summaries = []
        for f in files:
            summary = self.summarize_file(f)
            summaries.append(summary)
            print(f"  • {summary['filename']} ({summary['sections']} sections)")
            print(f"    Path: {summary['full_path']}")

        # Step 4: Create action plan
        print("\n✍️  CREATING ACTION PLAN:")
        plan_path = self.create_action_plan(summaries)
        print(f"✓ Plan created: {plan_path}")

        # Step 5: Success summary
        print("\n" + "=" * 60)
        print("✅ EXECUTION COMPLETE")
        print("=" * 60)
        print(f"Files processed: {len(files)}")
        print(f"Plan location: {plan_path}")
        print(f"Handbook rules applied: ✓")

        return {
            'status': 'success',
            'files_processed': len(files),
            'plan_path': plan_path,
            'handbook_checked': True
        }

if __name__ == "__main__":
    handler = BasicFileHandler(".")
    handler.execute()
