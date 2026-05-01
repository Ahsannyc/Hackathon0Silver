# Silver Tier Agent Skills - Quick Reference

## 🚀 Active Skills

### 1. Auto LinkedIn Poster
**Skill ID:** `@Auto LinkedIn Poster`

**Purpose:** Scan sales leads and draft LinkedIn posts with HITL approval

**Quick Start:**
```bash
# Test (dry run - no files created)
python3 skills/auto_linkedin_poster.py --dry-run

# Process leads
python3 skills/auto_linkedin_poster.py --process

# Schedule hourly
pm2 start skills/auto_linkedin_poster.py --name auto_linkedin_poster --interpreter python3 --cron "0 * * * *"
```

**Example Agent Commands:**
```
@Auto LinkedIn Poster process sales lead
@Auto LinkedIn Poster scan
@Auto LinkedIn Poster draft posts
```

**Workflow:**
```
/Needs_Action (scan for sales/client/project keywords)
    ↓
Parse YAML & Extract Lead Info
    ↓
Reference Company_Handbook.md (polite tone)
    ↓
Draft LinkedIn Post (template-based)
    ↓
/Plans (save draft with YAML metadata)
    ↓
/Pending_Approval (HITL approval required)
    ↓
/Approved (after human review)
```

**Input Files:** `/Needs_Action/*.md` with keywords: `sales`, `client`, `project`

**Output Files:**
- Drafts: `/Plans/linkedin_post_[date]_[hash]_[name].md`
- Pending: `/Pending_Approval/linkedin_post_[date]_[hash]_[name].md`
- Approved: `/Approved/linkedin_post_[date]_[hash]_[name].md`

**YAML Metadata in Drafts:**
```yaml
---
type: linkedin_post
from: Contact Name
subject: LinkedIn Post Draft
source_lead: original_file.md
priority: high/medium/low
status: draft
requires_approval: true
created_at: ISO timestamp
keywords: sales, client, project
---
```

**Documentation:** See `skills/SKILL_AUTO_LINKEDIN_POSTER.md`

**Logs:** `schedulers/logs/auto_linkedin_poster.log`

---

## 📋 Watcher Agents (Related)

### Gmail Watcher
**Path:** `watchers/gmail_watcher.py`
- Monitors unread important emails
- Keywords: urgent, invoice, payment, sales
- Check interval: 120 seconds
- Output: `/Needs_Action/*.md`

### WhatsApp Watcher
**Path:** `watchers/whatsapp_watcher.py`
- Monitors unread messages (Playwright)
- Keywords: urgent, invoice, payment, sales
- Check interval: 30 seconds
- Session: `session/whatsapp/` (persistent)
- Output: `/Needs_Action/*.md`

### LinkedIn Watcher
**Path:** `watchers/linkedin_watcher.py`
- Monitors messages & notifications
- Keywords: sales, client, project
- Check interval: 60 seconds
- Session: `session/linkedin/` (persistent)
- Output: `/Needs_Action/*.md`

---

## 📁 Silver Tier Folder Structure

```
Hackathon0Silver/
├── watchers/                      # Input watchers (scan for leads)
│   ├── gmail_watcher.py          # → outputs to /Needs_Action
│   ├── whatsapp_watcher.py       # → outputs to /Needs_Action
│   ├── linkedin_watcher.py       # → outputs to /Needs_Action
│   └── logs/
├── skills/                        # Agent skills (process leads)
│   ├── auto_linkedin_poster.py   # Main skill
│   ├── SKILL_AUTO_LINKEDIN_POSTER.md
│   └── SKILLS_MANIFEST.md
├── schedulers/                    # Scheduled tasks & cron jobs
│   └── logs/
├── Needs_Action/                  # Lead queue (from watchers)
├── Pending_Approval/              # HITL approval queue
├── Approved/                       # Approved posts (ready to publish)
├── Plans/                          # Draft posts (from auto_linkedin_poster)
├── Rejected/                       # Rejected content
├── mcp_servers/                    # MCP server configs
├── Done/                           # Completed items
├── Inbox/                          # General inbox
├── Logs/                           # System logs
└── Company_Handbook.md             # Tone/language guidelines
```

---

## 🔄 Suggested Workflow

1. **Enable Watchers** (continuous monitoring)
   ```bash
   pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python3
   pm2 start watchers/whatsapp_watcher.py --name whatsapp_watcher --interpreter python3
   pm2 start watchers/linkedin_watcher.py --name linkedin_watcher --interpreter python3
   ```

2. **Schedule Auto LinkedIn Poster** (hourly processing)
   ```bash
   pm2 start skills/auto_linkedin_poster.py --name auto_linkedin_poster --interpreter python3 --cron "0 * * * *"
   ```

3. **Monitor Pending Approvals** (human review queue)
   ```bash
   # Check /Pending_Approval for drafts
   ls -la Pending_Approval/
   ```

4. **Approve Posts** (move to published)
   ```bash
   # Review draft content
   cat Pending_Approval/linkedin_post_*.md

   # Approve and move
   mv Pending_Approval/linkedin_post_*.md Approved/
   ```

5. **Publish to LinkedIn** (manual step)
   - Copy approved post content
   - Publish to LinkedIn
   - Archive completed files

---

## 🧪 Testing Auto LinkedIn Poster

### 1. Dry Run (Preview)
```bash
python3 skills/auto_linkedin_poster.py --dry-run
```

### 2. Create Test Lead
```bash
cat > Needs_Action/test_sales_lead.md << 'EOF'
---
type: email
from: John Sales
subject: Interested in project collaboration
priority: high
source: gmail
received: 2026-02-14T10:00:00
---

We have a sales project that needs immediate attention.
Looking for partnership opportunities with your team.
EOF
```

### 3. Process
```bash
python3 skills/auto_linkedin_poster.py --process
```

### 4. Verify
```bash
# Check draft
ls -la Plans/linkedin_post_*.md
cat Plans/linkedin_post_*.md

# Check approval queue
ls -la Pending_Approval/linkedin_post_*.md
```

---

## 📚 Dependencies

**Gmail Watcher:**
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**WhatsApp & LinkedIn Watchers:**
```bash
pip install playwright
playwright install chromium
```

**Auto LinkedIn Poster:**
```bash
pip install pyyaml
```

**All:**
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright pyyaml
playwright install chromium
```

---

## 📊 Monitoring

**View All PM2 Services:**
```bash
pm2 list
```

**Monitor Logs:**
```bash
pm2 logs gmail_watcher
pm2 logs whatsapp_watcher
pm2 logs linkedin_watcher
pm2 logs auto_linkedin_poster
```

**Check Skill Logs:**
```bash
tail -f skills/logs/auto_linkedin_poster.log
tail -f watchers/logs/gmail_watcher.log
tail -f watchers/logs/whatsapp_watcher.log
tail -f watchers/logs/linkedin_watcher.log
```

---

**Last Updated:** 2026-02-14
**Status:** ✅ All systems active
