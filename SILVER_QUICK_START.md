# Silver Tier Quick Start Guide
**5-Minute Setup to Get Running**

---

## 🚀 **Step 1: Update Configuration (2 minutes)**

### Edit `orchestrator.py` - Set Your Vault Path

```bash
# Open orchestrator.py in your editor
nano orchestrator.py
# or code orchestrator.py
```

Find this line (around line 25):
```python
VAULT_PATH = Path.home() / "AI_Employee_Vault"
```

Change it to your actual vault path:
```python
VAULT_PATH = Path("C:/Users/YourName/Documents/AI_Employee_Vault")
# or for Mac/Linux:
VAULT_PATH = Path.home() / "my-obsidian-vault"
```

Save and close.

---

## 📋 **Step 2: Start Watchers (1 minute)**

Make sure your watchers are running via PM2:

```bash
# Check which watchers are running
pm2 list

# If not running, start them:
pm2 start watchers/gmail_watcher.py --name gmail --interpreter python3
pm2 start watchers/whatsapp_persistent.py --name whatsapp --interpreter python3
pm2 start watchers/linkedin_persistent.py --name linkedin --interpreter python3

# Save configuration for auto-start on reboot
pm2 save
pm2 startup
```

---

## 🏃 **Step 3: Start Orchestrator (1 minute)**

```bash
# Navigate to project
cd ~/Hackathon0Silver  # adjust path as needed

# Start orchestrator
python orchestrator.py

# You should see:
# ============================================================
# ORCHESTRATOR STARTED
# ============================================================
# Vault: /path/to/vault
# Watching: /path/to/Needs_Action
# ============================================================
```

Leave this running (open it in screen/tmux or separate terminal window).

---

## 📝 **Step 4: Create Test Task (1 minute)**

Open another terminal:

```bash
cd ~/Hackathon0Silver

# Create test email task
cat > Needs_Action/TEST_EMAIL.md << 'EOF'
---
type: email
from: client@example.com
subject: Test Email Request
priority: high
---

This is a test email task to verify the system is working.
EOF

# Create test WhatsApp task
cat > Needs_Action/TEST_WHATSAPP.md << 'EOF'
---
type: whatsapp
from: John Doe
message: "Hey, is the project ready?"
priority: normal
---

Simple acknowledgment message.
EOF
```

---

## ✅ **Step 5: Watch It Process (In Real-Time)**

### Terminal 1: Watch the Logs
```bash
tail -f Logs/$(date +%Y-%m-%d).log
```

You should see:
```
2026-01-07 10:30:45 - INFO - ✨ New task detected: TEST_EMAIL.md
2026-01-07 10:30:45 - INFO - 📌 Moved to In_Progress: TEST_EMAIL.md
2026-01-07 10:30:46 - INFO - 📋 Triggering Claude for: TEST_EMAIL.md
```

### Terminal 2: Check Dashboard
```bash
cat Dashboard.md
```

You'll see:
```
## Task Queue

### In Progress (1)
- TEST_EMAIL.md

### Pending Actions
- Check /Pending_Approval folder
```

### Terminal 3: Check Pending Approvals
```bash
# See what's waiting for approval
ls -la Pending_Approval/

# Read the approval request
cat Pending_Approval/EMAIL_test_email.md
```

---

## 🆗 **Step 6: Approve a Task (30 seconds)**

When you see a task in `/Pending_Approval/`:

```bash
# View the approval request
cat Pending_Approval/EMAIL_test_email.md

# Review the content, then approve:
mv Pending_Approval/EMAIL_test_email.md Approved/

# Watch the logs - execution happens automatically!
tail -f Logs/$(date +%Y-%m-%d).log
```

You'll see:
```
2026-01-07 10:31:15 - INFO - ✅ Executing approved action: EMAIL_test_email.md
2026-01-07 10:31:15 - INFO - 📧 Executing email action from EMAIL_test_email.md
2026-01-07 10:31:15 - INFO - ✓ Completed and moved to Done: EMAIL_test_email.md
```

---

## 📊 **Step 7: Check Completion**

```bash
# View completed tasks
ls -la Done/

# Check updated dashboard
cat Dashboard.md
# Should show: "Completed Today: 2"

# Check audit log
cat Logs/$(date +%Y-%m-%d).json | jq
```

---

## 🎯 **Normal Daily Usage**

Once running, here's your routine:

### **Every Morning**
```bash
# Check dashboard status
cat Dashboard.md

# Look for pending approvals
ls -la Pending_Approval/
```

### **When You See Something to Approve**
```bash
# Review the approval file
cat Pending_Approval/[FILENAME].md

# Approve (move to Approved folder)
mv Pending_Approval/[FILENAME].md Approved/

# Done! Orchestrator executes automatically
```

### **Monitor System Health**
```bash
# Check recent logs
tail -20 Logs/$(date +%Y-%m-%d).log

# Verify watchers are running
pm2 list

# View dashboard
cat Dashboard.md
```

---

## 🚨 **If Something Goes Wrong**

### **Orchestrator stopped?**
```bash
# Restart it
python orchestrator.py
```

### **Watcher crashed?**
```bash
# Restart it
pm2 restart gmail  # or whatsapp, linkedin

# Or restart all
pm2 restart all
```

### **Task stuck in /In_Progress/?**
```bash
# Move it back to /Needs_Action
mv In_Progress/[FILENAME].md Needs_Action/
```

### **Want to reject an approval?**
```bash
# Move from Pending_Approval to Rejected
mv Pending_Approval/[FILENAME].md Rejected/
```

### **Check what went wrong?**
```bash
# Read the detailed log
cat Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.status=="error")'

# Or read the log file
cat Logs/$(date +%Y-%m-%d).log | grep -i error
```

---

## 💡 **Pro Tips**

### **Keep Terminal Clean**
```bash
# Run orchestrator in background (use tmux or screen)
tmux new-session -d -s orchestrator "python orchestrator.py"

# Monitor from main terminal
tmux attach -t orchestrator
```

### **Watch Folder in Obsidian**
- Open Dashboard.md in Obsidian
- It auto-refreshes every 30 seconds
- You can see status without leaving Obsidian

### **Batch Approvals**
```bash
# Approve all waiting items at once
mv Pending_Approval/* Approved/

# Orchestrator processes them automatically
```

### **Debug a Specific Task**
```bash
# See what's in a task file
cat Needs_Action/[FILENAME].md

# Check its plan
cat Plans/PLAN_[FILENAME].md

# Check its approval request
cat Pending_Approval/[FILENAME].md
```

---

## 📚 **When You Need More Info**

| Question | Document |
|----------|----------|
| "How does Claude process tasks?" | CLAUDE_WORKFLOW.md |
| "What rules govern decisions?" | Company_Handbook.md |
| "How do the skills work together?" | AGENT_SKILLS_SILVER.md |
| "What's completed?" | SILVER_TIER_COMPLETE.md |
| "How do I troubleshoot?" | HOW_TO_RUN_PROJECT.md |

---

## ✨ **You're Ready!**

Your Silver Tier AI Employee is now running. It will:

✅ Monitor your inboxes (Gmail, WhatsApp, LinkedIn)  
✅ Create plans for tasks automatically  
✅ Request your approval when needed  
✅ Execute approved actions  
✅ Log everything for audit  
✅ Keep Dashboard updated in real-time  

**Just approve tasks as they come in!**

---

**Happy automating!** 🚀
