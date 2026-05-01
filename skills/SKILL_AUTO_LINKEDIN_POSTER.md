# Agent Skill: Auto LinkedIn Poster

**Tier:** Silver
**Status:** Active
**Type:** Automated Agent / Scheduler

## Overview

Auto LinkedIn Poster is an intelligent agent skill that automatically scans sales/business leads and drafts professional LinkedIn posts for human review and approval (HITL workflow).

**Skill ID:** `@Auto LinkedIn Poster`

## Capabilities

✅ Scans `/Needs_Action` for unreviewed leads
✅ Detects sales/business keywords: `sales`, `client`, `project`
✅ Drafts LinkedIn posts with professional template
✅ References `Company_Handbook.md` for tone/language guidelines
✅ Implements HITL (Human In The Loop) approval workflow
✅ Saves drafts to `/Plans` with YAML metadata
✅ Moves approved content to `/Pending_Approval` for review

## Invocation Examples

### Agent Command
```bash
@Auto LinkedIn Poster process sales lead
@Auto LinkedIn Poster scan
@Auto LinkedIn Poster draft posts
```

### Direct Command Line
```bash
# Process leads and draft posts
python3 schedulers/auto_linkedin_poster.py --process

# Dry run (preview without creating files)
python3 schedulers/auto_linkedin_poster.py --dry-run

# Combined: dry run first, then process
python3 schedulers/auto_linkedin_poster.py --dry-run
python3 schedulers/auto_linkedin_poster.py --process
```

### PM2 Scheduling
```bash
# Run once per hour
pm2 start schedulers/auto_linkedin_poster.py --name auto_linkedin_poster --interpreter python3 --cron "0 * * * *"

# Run every 30 minutes
pm2 start schedulers/auto_linkedin_poster.py --name auto_linkedin_poster --interpreter python3 --cron "*/30 * * * *"

# Monitor logs
pm2 logs auto_linkedin_poster

# Delete scheduler
pm2 delete auto_linkedin_poster
```

## Workflow

```
1. SCAN
   └─ /Needs_Action for files with keywords: sales, client, project

2. EXTRACT
   └─ Parse YAML metadata and message content
   └─ Identify lead information (from, subject, priority)

3. REFERENCE
   └─ Load Company_Handbook.md guidelines
   └─ Apply polite, professional tone

4. DRAFT
   └─ Generate LinkedIn post from template:
      "Excited to offer [service] for [benefit]! DM for more."

5. SAVE
   └─ /Plans/linkedin_post_[date]_[hash].md
   └─ Include YAML: type, status, source_lead, priority, created_at

6. HITL APPROVAL
   └─ Move to /Pending_Approval for human review
   └─ Requires manual approval before publishing

7. APPROVED
   └─ Once approved, move to /Approved
   └─ Ready for manual LinkedIn publishing
```

## File Structure

**Input:** `/Needs_Action/*.md`
```yaml
---
type: email/whatsapp/linkedin
from: Contact Name
subject: Message Subject
priority: high/medium/low
source: gmail/whatsapp/linkedin
---
```

**Output (Draft):** `/Plans/linkedin_post_[date]_[hash]_[name].md`
```yaml
---
type: linkedin_post
from: Contact Name
source_lead: original_file.md
priority: high/medium/low
status: draft
requires_approval: true
---
```

**Approval:** `/Pending_Approval/linkedin_post_[date]_[hash]_[name].md`
```yaml
---
status: pending_approval
requires_approval: true
---
```

**Published:** `/Approved/linkedin_post_[date]_[hash]_[name].md`
```yaml
---
status: approved
published: true
---
```

## Configuration

Edit in `schedulers/auto_linkedin_poster.py`:

```python
KEYWORDS = ['sales', 'client', 'project']  # Search terms
POST_TEMPLATES = [...]                      # LinkedIn post templates
NEEDS_ACTION_DIR = Path("Needs_Action")    # Input directory
PLANS_DIR = Path("Plans")                   # Draft output
PENDING_APPROVAL_DIR = Path("Pending_Approval")  # Approval queue
APPROVED_DIR = Path("Approved")             # Published posts
HANDBOOK_PATH = Path("Company_Handbook.md") # Tone guidelines
```

## Company Handbook Integration

The skill automatically references `Company_Handbook.md` for tone guidelines:

- **Rule:** "Always be polite in replies"
- **Implementation:** Ensures all drafted posts use professional, polite language
- **Examples:**
  - "need" → "would appreciate"
  - "must" → "should"
  - "can't" → "unable to"

## Testing

### 1. Dry Run (No Files Created)
```bash
python3 schedulers/auto_linkedin_poster.py --dry-run
# Output: Preview of what would be processed
```

### 2. Create Test Lead
```bash
# Create test file in /Needs_Action
cat > Needs_Action/test_sales_lead.md << 'EOF'
---
type: email
from: John Sales
subject: Interested in project collaboration
priority: high
source: gmail
received: 2026-02-14T10:00:00
---

We have a sales project that needs immediate attention. Looking for partnership opportunities.
EOF
```

### 3. Process Test Lead
```bash
python3 schedulers/auto_linkedin_poster.py --process
```

### 4. Verify Output
```bash
# Check draft created
ls -la Plans/linkedin_post_*.md

# Review draft content
cat Plans/linkedin_post_*.md

# Verify moved to approval queue
ls -la Pending_Approval/linkedin_post_*.md
```

## HITL Approval Process

1. **Review Draft** in `/Pending_Approval`
   - Read generated post
   - Verify tone and accuracy
   - Check keywords match lead

2. **Approve** by moving to `/Approved`
   ```bash
   mv Pending_Approval/linkedin_post_*.md Approved/
   ```

3. **Publish** to LinkedIn
   - Copy post content
   - Post to LinkedIn
   - Archive original file

4. **Track** in audit logs
   - `schedulers/logs/auto_linkedin_poster.log`

## Logs & Troubleshooting

**Log Location:** `schedulers/logs/auto_linkedin_poster.log`

**Enable Debug Mode:**
```python
# In auto_linkedin_poster.py, change:
logging.basicConfig(level=logging.DEBUG)
```

**Common Issues:**

| Issue | Solution |
|-------|----------|
| No leads detected | Verify files in `/Needs_Action` have keywords: sales, client, project |
| YAML parse errors | Ensure valid YAML in markdown frontmatter |
| Company_Handbook.md not found | Create file or provide path in code |
| Approval not moving files | Check file permissions in `/Pending_Approval` |

## Dependencies

```bash
pip install pyyaml
```

## Integration Points

- **Input:** Gmail/WhatsApp/LinkedIn Watchers → `/Needs_Action`
- **Reference:** `Company_Handbook.md`
- **Output:** `/Plans` → `/Pending_Approval` → `/Approved`
- **Related Skills:** `@LinkedIn Watcher`, `@Gmail Watcher`, `@WhatsApp Watcher`

## Success Metrics

✅ **Input Processing:** Files scanned from `/Needs_Action`
✅ **Lead Detection:** Correctly identifies sales/client/project keywords
✅ **Draft Quality:** Posts follow Company_Handbook tone guidelines
✅ **Workflow Compliance:** All drafts moved to `/Pending_Approval`
✅ **HITL Ready:** Human approval required before publishing

## Next Steps

1. Run first test: `python3 schedulers/auto_linkedin_poster.py --dry-run`
2. Create test lead in `/Needs_Action`
3. Process leads: `python3 schedulers/auto_linkedin_poster.py --process`
4. Review drafts in `/Pending_Approval`
5. Approve and move to `/Approved`
6. Schedule with PM2 for automated hourly runs

---

**Created:** 2026-02-14
**Skill Type:** Agent / Scheduler
**Tier:** Silver
**Status:** ✅ Active
