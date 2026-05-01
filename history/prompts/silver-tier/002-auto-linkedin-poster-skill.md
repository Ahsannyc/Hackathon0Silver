# PHR: Create Auto LinkedIn Poster Skill

**ID:** 002
**Stage:** implementation | silver-tier
**Date:** 2026-02-14
**Status:** COMPLETE ✅

---

## Task Summary

Create an agent skill that scans `/Needs_Action/` for sales/business leads, drafts LinkedIn posts, saves to `/Plans/` for HITL approval.

---

## Skill Details

**File:** `skills/auto_linkedin_poster.py` (15 KB)

**Purpose:** Convert sales leads from various sources into polished LinkedIn posts

**Input Source:** `/Needs_Action/` folder
- Accepts messages from Gmail, WhatsApp, LinkedIn
- Filters for keywords: sales, client, project

**Processing:**
1. Read task from `/Needs_Action/`
2. Extract key details (service, benefit, customer type)
3. Reference `Company_Handbook.md` for tone and language
4. Draft professional LinkedIn post
5. Add hashtags and call-to-action

**Output:** `/Plans/linkedin_post_[date]_[hash].md`
```markdown
---
type: linkedin_post
status: draft
created: 2026-02-14T10:30:45
service: [extracted]
benefit: [extracted]
target_segment: [extracted]
approval_required: true
---

# LinkedIn Post Draft

[Post content with proper formatting]
```

**HITL Integration:**
- Move to `/Pending_Approval/` for human review
- Await approval in `/Approved/` folder
- HITL Approval Handler executes via MCP

---

## Usage Example

**User Command:** `@Auto LinkedIn Poster process sales lead`

**Input File:** `Needs_Action/whatsapp_sales_2026-02-14_100000.md`
```yaml
---
type: message
from: John Smith
content: "We have a new sales opportunity for marketing consulting"
source: whatsapp
---
```

**Output Draft:** `Plans/linkedin_post_2026-02-14_abc123.md`
```markdown
---
type: linkedin_post
status: draft
service: Marketing Consulting
benefit: Increase brand visibility
target: Growing B2B companies
---

Excited to offer expert marketing consulting services that help growing B2B companies increase their brand visibility and market reach!

Perfect for companies looking to optimize their digital strategy.

Let's connect and discuss how we can accelerate your growth! 📈

#Marketing #Consulting #Business #Growth
```

---

## Integration Points

**Reads From:**
- `/Needs_Action/` - Source messages
- `Company_Handbook.md` - Tone and language guidelines

**Writes To:**
- `/Plans/` - Draft posts
- `/Pending_Approval/` - For HITL review
- `/Logs/auto_linkedin_poster_[date].md` - Execution logs

**Integrates With:**
- `HITL Approval Handler` - Approval workflow
- `LinkedIn Watcher` - Source of posts
- Email/WhatsApp Watchers - Customer leads

---

## Features

✅ Smart templating based on content
✅ Keyword extraction from messages
✅ Company handbook integration
✅ Professional tone enforcement
✅ HITL approval workflow
✅ Detailed logging
✅ Error handling with retry

---

## Related Documentation

**Files:**
- `SKILL_AUTO_LINKEDIN_POSTER.md` - Complete skill documentation
- `SKILL_QUICK_REFERENCE.md` - Quick reference for all skills

---

**Progress:** ✅ COMPLETE | Status: Ready for use
**Next:** HITL Approval Handler execution

