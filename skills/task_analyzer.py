#!/usr/bin/env python3
"""
Bronze Tier Skill: Task Analyzer
- Analyze files in /Needs_Action
- Identify task type (file drop, payment, etc.)
- Create simple action plan in Plan.md
- Flag sensitive/approval-needed items
- Write to /Pending_Approval if needed
- Use Ralph Wiggum loop for multi-step tasks
"""

import os
import re
from datetime import datetime
from pathlib import Path

class TaskAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.needs_action = self.project_root / "Needs_Action"
        self.plans = self.project_root / "Plans"
        self.pending_approval = self.project_root / "Pending_Approval"
        self.handbook = self.project_root / "Company_Handbook.md"

        # Ralph Wiggum Loop - "I'm helping" for multi-step tasks
        self.ralph_loop = """
        🎯 Ralph Wiggum Loop:
        Step 1: I'm helping (identify issue)
        Step 2: Let's solve this (break into steps)
        Step 3: I'm doing my best (execute steps)
        Step 4: It's working! (verify completion)
        """

    def detect_task_type(self, filename, content):
        """Identify task type from file"""
        indicators = {
            'payment': ['$', 'payment', 'invoice', 'bill', 'amount', 'cost'],
            'approval': ['approve', 'review', 'decision', 'authorization'],
            'file_drop': ['attached', 'enclosed', 'file', 'document'],
            'info': ['information', 'details', 'data', 'report'],
            'action': ['do', 'please', 'action required', 'urgent']
        }

        task_type = 'general'
        score = {'payment': 0, 'approval': 0, 'file_drop': 0, 'info': 0, 'action': 0}

        content_lower = content.lower()
        for type_name, keywords in indicators.items():
            for keyword in keywords:
                if keyword in content_lower:
                    score[type_name] += 1

        if score['payment'] > 0:
            task_type = 'payment'
        elif score['approval'] > 0:
            task_type = 'approval'
        elif score['file_drop'] > 0:
            task_type = 'file_drop'
        elif score['action'] > 0:
            task_type = 'action'

        return task_type, score

    def check_approval_needed(self, content):
        """Check if task needs approval"""
        rules = {
            'high_payment': lambda c: any(
                int(amount) > 500
                for amount in re.findall(r'\$\s*(\d+)', c)
            ) if re.findall(r'\$\s*(\d+)', c) else False,
            'sensitive_data': 'sensitive' in content.lower() or 'confidential' in content.lower(),
            'requires_approval': 'approval' in content.lower() or 'approve' in content.lower(),
        }

        reasons = []
        needs_approval = False

        for check_name, check_func in rules.items():
            try:
                if check_func(content):
                    needs_approval = True
                    reasons.append(f"  • {check_name.replace('_', ' ').title()}")
            except:
                pass

        return needs_approval, reasons

    def count_steps(self, content):
        """Count steps in task (simple heuristic)"""
        step_indicators = len(re.findall(r'^\d+\.|step|do |then |next', content.lower(), re.MULTILINE))
        return max(step_indicators, 1)  # At least 1 step

    def create_analysis_plan(self, tasks_data):
        """Create detailed analysis plan"""
        plan_content = f"""# Task Analysis Plan
Generated: {datetime.now().isoformat()}

## Summary
Total tasks analyzed: {len(tasks_data)}
Requiring approval: {sum(1 for t in tasks_data if t['needs_approval'])}
Multi-step tasks: {sum(1 for t in tasks_data if t['steps'] > 2)}

---

## Task Breakdown

"""

        for task in tasks_data:
            plan_content += f"### {task['filename']}\n"
            plan_content += f"**Type:** {task['type']}\n"
            plan_content += f"**Steps:** {task['steps']}\n"
            plan_content += f"**Approval Required:** {'❌ YES' if task['needs_approval'] else '✅ No'}\n"

            if task['needs_approval']:
                plan_content += f"**Reasons:**\n"
                for reason in task['approval_reasons']:
                    plan_content += f"{reason}\n"

            plan_content += "\n**Action Checklist:**\n"
            for i in range(task['steps']):
                plan_content += f"- [ ] Step {i+1}: {['Identify', 'Plan', 'Execute', 'Verify'][i % 4]}\n"

            if task['steps'] > 2:
                plan_content += "\n⚠️ Multi-step task - Using Ralph Wiggum Loop:\n"
                plan_content += "- [ ] I'm helping (understand)\n"
                plan_content += "- [ ] Let's solve this (plan)\n"
                plan_content += "- [ ] I'm doing my best (execute)\n"
                plan_content += "- [ ] It's working! (verify)\n"

            plan_content += "\n---\n\n"

        return plan_content

    def analyze_files(self):
        """Analyze all files in Needs_Action"""
        if not self.needs_action.exists():
            print("⚠️  /Needs_Action folder not found")
            return []

        md_files = list(self.needs_action.glob("*.md"))
        if not md_files:
            print("✓ No files to analyze")
            return []

        tasks_data = []

        for filepath in sorted(md_files):
            with open(filepath, 'r') as f:
                content = f.read()

            task_type, scores = self.detect_task_type(filepath.name, content)
            needs_approval, reasons = self.check_approval_needed(content)
            steps = self.count_steps(content)

            tasks_data.append({
                'filename': filepath.name,
                'filepath': str(filepath),
                'type': task_type,
                'needs_approval': needs_approval,
                'approval_reasons': reasons,
                'steps': steps,
                'content': content
            })

        return tasks_data

    def write_pending_approval(self, tasks_requiring_approval):
        """Write tasks needing approval to Pending_Approval folder"""
        self.pending_approval.mkdir(parents=True, exist_ok=True)

        approval_log = f"""# Pending Approval Log
Generated: {datetime.now().isoformat()}

## Tasks Requiring Approval

"""
        for task in tasks_requiring_approval:
            approval_log += f"### {task['filename']}\n"
            approval_log += f"**Type:** {task['type']}\n"
            approval_log += f"**Reasons for Approval:** \n"
            for reason in task['approval_reasons']:
                approval_log += f"{reason}\n"
            approval_log += f"\n**File Location:** {task['filepath']}\n\n---\n\n"

        approval_file = self.pending_approval / "approval_queue.md"
        with open(approval_file, 'w') as f:
            f.write(approval_log)

        return str(approval_file)

    def execute(self):
        """Execute full analysis workflow"""
        print("=" * 70)
        print("TASK ANALYZER - Bronze Tier Skill")
        print("=" * 70)

        # Step 1: Analyze files
        print("\n🔍 ANALYZING FILES IN /Needs_Action:")
        tasks = self.analyze_files()

        if not tasks:
            print("✓ No tasks to analyze")
            return

        print(f"✓ Analyzed {len(tasks)} task(s)")

        # Step 2: Categorize and display
        print("\n📊 TASK CATEGORIZATION:")
        type_counts = {}
        for task in tasks:
            task_type = task['type']
            type_counts[task_type] = type_counts.get(task_type, 0) + 1
            status = "🚫 APPROVAL NEEDED" if task['needs_approval'] else "✓ OK"
            print(f"  • {task['filename']:<30} | Type: {task_type:<10} | Steps: {task['steps']} | {status}")

        print("\n  Type Distribution:")
        for task_type, count in type_counts.items():
            print(f"    - {task_type}: {count}")

        # Step 3: Identify approval-needed tasks
        approval_tasks = [t for t in tasks if t['needs_approval']]
        if approval_tasks:
            print(f"\n⚠️  APPROVAL REQUIRED FOR {len(approval_tasks)} TASK(S):")
            for task in approval_tasks:
                print(f"  • {task['filename']}")
                for reason in task['approval_reasons']:
                    print(f"    {reason}")

        # Step 4: Create analysis plan
        print("\n✍️  CREATING ANALYSIS PLAN:")
        plan_content = self.create_analysis_plan(tasks)
        plan_file = self.plans / "Task_Analysis_Plan.md"
        plan_file.parent.mkdir(parents=True, exist_ok=True)

        with open(plan_file, 'w') as f:
            f.write(plan_content)
        print(f"✓ Plan created: {plan_file}")

        # Step 5: Write approval queue
        if approval_tasks:
            print("\n📋 WRITING APPROVAL QUEUE:")
            approval_file = self.write_pending_approval(approval_tasks)
            print(f"✓ Approval queue: {approval_file}")

        # Step 6: Ralph Wiggum Loop info
        print("\n🎯 RALPH WIGGUM LOOP (for multi-step tasks):")
        multi_step = [t for t in tasks if t['steps'] > 2]
        if multi_step:
            print(f"   Detected {len(multi_step)} multi-step task(s)")
            print("   - Step 1: I'm helping (identify issue)")
            print("   - Step 2: Let's solve this (break into steps)")
            print("   - Step 3: I'm doing my best (execute)")
            print("   - Step 4: It's working! (verify)")

        # Summary
        print("\n" + "=" * 70)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"Tasks analyzed: {len(tasks)}")
        print(f"Approval needed: {len(approval_tasks)}")
        print(f"Analysis plan: {plan_file}")

        return {
            'status': 'success',
            'tasks_analyzed': len(tasks),
            'approval_needed': len(approval_tasks),
            'plan_path': str(plan_file)
        }

if __name__ == "__main__":
    analyzer = TaskAnalyzer(".")
    analyzer.execute()
