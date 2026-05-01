#!/usr/bin/env node

/**
 * Email MCP Server - Silver Tier
 *
 * Provides Model Context Protocol tools for Gmail email operations:
 * - Draft emails (saves to /Plans/email_draft_*.md)
 * - Send emails (requires HITL approval from /Approved/)
 * - List drafts
 * - Check approval status
 *
 * USAGE:
 * ======
 *
 * Start server:
 *   node mcp_servers/email-mcp/index.js
 *
 * Development mode (verbose):
 *   node mcp_servers/email-mcp/index.js --verbose
 *
 * Test draft:
 *   curl -X POST http://localhost:3000/draft \
 *     -H "Content-Type: application/json" \
 *     -d '{"to":"user@example.com","subject":"Test","body":"Test email"}'
 *
 * Configuration:
 *   - credentials.json (Gmail OAuth credentials in project root)
 *   - .env (optional: EMAIL_VAULT_PATH, GMAIL_SCOPES)
 *
 * HITL Workflow:
 *   1. Draft email → /Plans/email_draft_*.md
 *   2. Create approval request → /Pending_Approval/email_approval_*.md
 *   3. Human moves to /Approved/
 *   4. Send email via Gmail API
 *   5. Log to /Logs/
 */

import { Server } from "@anthropic-sdk/mcp";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  TextContent,
  ToolResultBlockParam,
} from "@anthropic-sdk/mcp/types";
import { google } from "googleapis";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { createReadStream } from "fs";
import { stat } from "fs/promises";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration
const CONFIG = {
  PROJECT_ROOT: join(__dirname, "../.."),
  CREDENTIALS_PATH: join(process.cwd(), "credentials.json"),
  TOKEN_PATH: join(__dirname, ".gmail_token.json"),
  VAULT_PATHS: {
    NEEDS_ACTION: join(process.cwd(), "Needs_Action"),
    PLANS: join(process.cwd(), "Plans"),
    PENDING_APPROVAL: join(process.cwd(), "Pending_Approval"),
    APPROVED: join(process.cwd(), "Approved"),
    DONE: join(process.cwd(), "Done"),
    LOGS: join(process.cwd(), "Logs"),
  },
  GMAIL_SCOPES: [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
  ],
  VERBOSE: process.argv.includes("--verbose"),
};

// Logger
const logger = {
  info: (msg) => {
    if (CONFIG.VERBOSE) console.log(`[INFO] ${msg}`);
  },
  error: (msg) => console.error(`[ERROR] ${msg}`),
  success: (msg) => {
    if (CONFIG.VERBOSE) console.log(`[✓] ${msg}`);
  },
  warn: (msg) => console.warn(`[⚠] ${msg}`),
};

// Gmail OAuth Handler
class GmailAuthHandler {
  constructor() {
    this.auth = null;
    this.gmail = null;
  }

  async initialize() {
    try {
      if (!existsSync(CONFIG.CREDENTIALS_PATH)) {
        throw new Error(
          `credentials.json not found at ${CONFIG.CREDENTIALS_PATH}`
        );
      }

      const credentials = JSON.parse(
        readFileSync(CONFIG.CREDENTIALS_PATH, "utf-8")
      );

      const { client_id, client_secret, redirect_uris } =
        credentials.installed || credentials;

      this.auth = new google.auth.OAuth2(
        client_id,
        client_secret,
        redirect_uris[0]
      );

      // Try to load saved token
      if (existsSync(CONFIG.TOKEN_PATH)) {
        const token = JSON.parse(readFileSync(CONFIG.TOKEN_PATH, "utf-8"));
        this.auth.setCredentials(token);
        logger.success("Gmail authenticated with saved token");
      } else {
        logger.warn(
          "No saved token found. First email operation will require browser auth."
        );
      }

      this.gmail = google.gmail({ version: "v1", auth: this.auth });
      return true;
    } catch (error) {
      logger.error(`Gmail auth initialization failed: ${error.message}`);
      throw error;
    }
  }

  async ensureAuthenticated() {
    if (!this.auth || !this.gmail) {
      await this.initialize();
    }
  }

  getAuthUrl() {
    if (!this.auth) {
      const credentials = JSON.parse(
        readFileSync(CONFIG.CREDENTIALS_PATH, "utf-8")
      );
      const { client_id, client_secret, redirect_uris } =
        credentials.installed || credentials;
      this.auth = new google.auth.OAuth2(
        client_id,
        client_secret,
        redirect_uris[0]
      );
    }

    return this.auth.generateAuthUrl({
      access_type: "offline",
      scope: CONFIG.GMAIL_SCOPES,
    });
  }

  async setTokenFromCode(code) {
    if (!this.auth) {
      throw new Error("OAuth2 client not initialized");
    }

    const { tokens } = await this.auth.getToken(code);
    this.auth.setCredentials(tokens);

    // Save token for future use
    writeFileSync(CONFIG.TOKEN_PATH, JSON.stringify(tokens, null, 2));
    logger.success("Token saved");

    this.gmail = google.gmail({ version: "v1", auth: this.auth });
  }
}

// Email Service
class EmailService {
  constructor(authHandler) {
    this.auth = authHandler;
    this.ensureVaultDirs();
  }

  ensureVaultDirs() {
    Object.values(CONFIG.VAULT_PATHS).forEach((dir) => {
      mkdirSync(dir, { recursive: true });
    });
  }

  async draftEmail({ to, cc, bcc, subject, body, attachments = [] }) {
    try {
      logger.info(`Drafting email to: ${to}`);

      // Create email metadata
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const hash = Math.random().toString(36).substring(7);
      const safeTo = to.replace(/[@.]/g, "_");
      const draftFilename = `email_draft_${timestamp}_${hash}_${safeTo}.md`;
      const draftPath = join(CONFIG.VAULT_PATHS.PLANS, draftFilename);

      // Create markdown draft with YAML frontmatter
      const draftContent = this.createDraftMarkdown({
        to,
        cc,
        bcc,
        subject,
        body,
        attachments,
        timestamp,
      });

      writeFileSync(draftPath, draftContent, "utf-8");
      logger.success(`Draft saved: ${draftPath}`);

      // Create approval request
      const approvalFilename = `email_approval_${timestamp}_${hash}_${safeTo}.md`;
      const approvalPath = join(
        CONFIG.VAULT_PATHS.PENDING_APPROVAL,
        approvalFilename
      );

      const approvalContent = this.createApprovalRequest({
        to,
        cc,
        bcc,
        subject,
        body,
        draftFilename,
        timestamp,
      });

      writeFileSync(approvalPath, approvalContent, "utf-8");
      logger.success(`Approval request created: ${approvalPath}`);

      return {
        success: true,
        draftPath,
        approvalPath,
        message: `Email draft created. Review and approve in /Pending_Approval`,
        requires_approval: true,
      };
    } catch (error) {
      logger.error(`Draft email failed: ${error.message}`);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  createDraftMarkdown({
    to,
    cc,
    bcc,
    subject,
    body,
    attachments,
    timestamp,
  }) {
    const frontmatter = `---
type: email_draft
to: ${to}
${cc ? `cc: ${cc}` : ""}
${bcc ? `bcc: ${bcc}` : ""}
subject: ${subject}
status: draft
created_at: ${timestamp}
requires_approval: true
${attachments.length > 0 ? `attachments: ${attachments.join(", ")}` : ""}
---`;

    const content = `# Email Draft: ${subject}

**To:** ${to}
${cc ? `**CC:** ${cc}` : ""}
${bcc ? `**BCC:** ${bcc}` : ""}

**Subject:** ${subject}

---

## Email Body

${body}

---

## Attachments

${attachments.length > 0 ? attachments.map((a) => `- ${a}`).join("\n") : "None"}

---

## Action Required

This email draft requires approval before sending.

1. **Review** the content above
2. **Approve** by moving to /Approved/ folder
3. **Reject** by moving to /Rejected/ folder

Once approved, the email will be sent via Gmail.

**Note:** Do not edit this file after moving to /Approved/.
The approval detection looks for the filename in /Approved/.
`;

    return frontmatter + "\n\n" + content;
  }

  createApprovalRequest({
    to,
    cc,
    bcc,
    subject,
    body,
    draftFilename,
    timestamp,
  }) {
    const frontmatter = `---
type: email_approval
action: send_email
to: ${to}
${cc ? `cc: ${cc}` : ""}
${bcc ? `bcc: ${bcc}` : ""}
subject: ${subject}
created_at: ${timestamp}
status: pending_approval
requires_approval: true
draft_file: ${draftFilename}
---`;

    const content = `# Email Approval Request

**Action:** Send Email

**Recipient:** ${to}
${cc ? `**CC:** ${cc}` : ""}
${bcc ? `**BCC:** ${bcc}` : ""}

**Subject:** ${subject}

---

## Email Content

${body}

---

## To Approve

Move this file to the **/Approved/** folder:

\`\`\`bash
mv Pending_Approval/${draftFilename.replace("draft", "approval")} Approved/
\`\`\`

Or drag-and-drop in Obsidian.

## To Reject

Move this file to the **/Rejected/** folder:

\`\`\`bash
mv Pending_Approval/${draftFilename.replace("draft", "approval")} Rejected/
\`\`\`

---

**Created:** ${timestamp}
`;

    return frontmatter + "\n\n" + content;
  }

  async checkApprovalAndSend({ to, cc, bcc, subject, body, approvalPath }) {
    try {
      // Check if approval exists in /Approved/
      const approvalFilename = approvalPath.split("/").pop();
      const approvedPath = join(
        CONFIG.VAULT_PATHS.APPROVED,
        approvalFilename
      );

      if (!existsSync(approvedPath)) {
        return {
          success: false,
          approved: false,
          message: `Approval not found in /Approved/. Waiting for HITL review.`,
        };
      }

      logger.info(`Approval detected: ${approvalFilename}`);

      // Send email via Gmail API
      await this.auth.ensureAuthenticated();

      const messageBody = this.createEmailMessage({
        to,
        cc,
        bcc,
        subject,
        body,
      });

      const response = await this.auth.gmail.users.messages.send({
        userId: "me",
        requestBody: {
          raw: messageBody,
        },
      });

      logger.success(`Email sent! Message ID: ${response.data.id}`);

      // Log the send
      this.logEmailAction({
        action: "send",
        to,
        subject,
        messageId: response.data.id,
        status: "success",
      });

      // Move approval to done
      const doneApprovalPath = join(
        CONFIG.VAULT_PATHS.DONE,
        `sent_${approvalFilename}`
      );
      const approvedContent = readFileSync(approvedPath, "utf-8");
      writeFileSync(doneApprovalPath, approvedContent, "utf-8");

      return {
        success: true,
        approved: true,
        messageId: response.data.id,
        message: `Email sent successfully to ${to}`,
      };
    } catch (error) {
      logger.error(`Send email failed: ${error.message}`);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  createEmailMessage({ to, cc, bcc, subject, body }) {
    const utf8Subject = `=?utf-8?B?${Buffer.from(subject).toString("base64")}?=`;

    let message = `From: me\r\nTo: ${to}\r\n`;
    if (cc) message += `Cc: ${cc}\r\n`;
    if (bcc) message += `Bcc: ${bcc}\r\n`;
    message += `Subject: ${utf8Subject}\r\n\r\n${body}`;

    return Buffer.from(message)
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");
  }

  logEmailAction({ action, to, subject, messageId, status }) {
    try {
      const logsDir = CONFIG.VAULT_PATHS.LOGS;
      mkdirSync(logsDir, { recursive: true });

      const timestamp = new Date().toISOString();
      const logEntry = {
        timestamp,
        action,
        to,
        subject,
        messageId,
        status,
      };

      const logFile = join(logsDir, `email_${action}_${new Date().toISOString().split("T")[0]}.json`);

      let logs = [];
      if (existsSync(logFile)) {
        logs = JSON.parse(readFileSync(logFile, "utf-8"));
      }

      logs.push(logEntry);
      writeFileSync(logFile, JSON.stringify(logs, null, 2), "utf-8");

      logger.success(`Logged: ${action} to ${to}`);
    } catch (error) {
      logger.error(`Log failed: ${error.message}`);
    }
  }

  async getStatus() {
    try {
      const pendingCount = this._countFiles(CONFIG.VAULT_PATHS.PENDING_APPROVAL);
      const approvedCount = this._countFiles(CONFIG.VAULT_PATHS.APPROVED);
      const doneCount = this._countFiles(CONFIG.VAULT_PATHS.DONE);

      return {
        pending_approvals: pendingCount,
        approved: approvedCount,
        completed: doneCount,
      };
    } catch (error) {
      logger.error(`Status check failed: ${error.message}`);
      return {};
    }
  }

  _countFiles(dirPath) {
    if (!existsSync(dirPath)) return 0;
    const fs = require("fs");
    return fs
      .readdirSync(dirPath)
      .filter((f) => f.endsWith(".md")).length;
  }
}

// MCP Server Implementation
class EmailMCPServer {
  constructor() {
    this.server = new Server({
      name: "email-mcp",
      version: "1.0.0",
    });

    this.authHandler = new GmailAuthHandler();
    this.emailService = new EmailService(this.authHandler);

    this.setupTools();
  }

  setupTools() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "draft_email",
          description:
            "Draft an email and save to /Plans for HITL approval. Does not send until approved in /Approved/",
          inputSchema: {
            type: "object",
            properties: {
              to: {
                type: "string",
                description: "Recipient email address",
              },
              cc: {
                type: "string",
                description: "CC recipients (optional, comma-separated)",
              },
              bcc: {
                type: "string",
                description: "BCC recipients (optional, comma-separated)",
              },
              subject: {
                type: "string",
                description: "Email subject",
              },
              body: {
                type: "string",
                description: "Email body (supports markdown)",
              },
              attachments: {
                type: "array",
                items: { type: "string" },
                description: "Attachment file paths (optional)",
              },
            },
            required: ["to", "subject", "body"],
          },
        },
        {
          name: "send_email",
          description:
            "Send an approved email via Gmail API. Requires approval file in /Approved/ first.",
          inputSchema: {
            type: "object",
            properties: {
              to: {
                type: "string",
                description: "Recipient email address",
              },
              cc: {
                type: "string",
                description: "CC recipients (optional)",
              },
              bcc: {
                type: "string",
                description: "BCC recipients (optional)",
              },
              subject: {
                type: "string",
                description: "Email subject",
              },
              body: {
                type: "string",
                description: "Email body",
              },
              approval_file: {
                type: "string",
                description: "Path to approval file in /Approved/",
              },
            },
            required: ["to", "subject", "body", "approval_file"],
          },
        },
        {
          name: "get_email_status",
          description:
            "Get current status of emails: pending approvals, approved, completed",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "authenticate_gmail",
          description:
            "Authenticate with Gmail API using OAuth2. Requires browser interaction.",
          inputSchema: {
            type: "object",
            properties: {
              auth_code: {
                type: "string",
                description:
                  "Authorization code from browser (after clicking auth URL)",
              },
            },
          },
        },
      ],
    }));

    this.server.setRequestHandler(
      CallToolRequestSchema,
      async (request) => {
        logger.info(`Tool called: ${request.params.name}`);

        try {
          let result;

          switch (request.params.name) {
            case "draft_email":
              result = await this.handleDraftEmail(request.params.arguments);
              break;
            case "send_email":
              result = await this.handleSendEmail(request.params.arguments);
              break;
            case "get_email_status":
              result = await this.handleGetStatus();
              break;
            case "authenticate_gmail":
              result = await this.handleAuthenticateGmail(
                request.params.arguments
              );
              break;
            default:
              result = { error: `Unknown tool: ${request.params.name}` };
          }

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        } catch (error) {
          logger.error(`Tool execution failed: ${error.message}`);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(
                  { error: error.message },
                  null,
                  2
                ),
              },
            ],
            isError: true,
          };
        }
      }
    );
  }

  async handleDraftEmail(args) {
    return await this.emailService.draftEmail(args);
  }

  async handleSendEmail(args) {
    return await this.emailService.checkApprovalAndSend(args);
  }

  async handleGetStatus(args) {
    return await this.emailService.getStatus();
  }

  async handleAuthenticateGmail(args) {
    try {
      if (args.auth_code) {
        await this.authHandler.setTokenFromCode(args.auth_code);
        return {
          success: true,
          message: "Gmail authentication successful",
        };
      } else {
        const authUrl = this.authHandler.getAuthUrl();
        return {
          success: false,
          message: "Visit this URL to authenticate:",
          auth_url: authUrl,
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async start() {
    try {
      // Initialize Gmail auth
      await this.authHandler.initialize();
      logger.success("Gmail auth initialized");

      // Start MCP server
      const transport = this.server.createLoopbackTransport();
      console.log(
        JSON.stringify({
          jsonrpc: "2.0",
          method: "initialize",
          params: {
            name: "email-mcp",
            version: "1.0.0",
            capabilities: {},
          },
        })
      );

      logger.success("Email MCP Server running");
      return transport;
    } catch (error) {
      logger.error(`Server startup failed: ${error.message}`);
      process.exit(1);
    }
  }
}

// Main
async function main() {
  const server = new EmailMCPServer();
  await server.start();

  // Keep server running
  process.on("SIGINT", () => {
    logger.info("Server shutting down");
    process.exit(0);
  });
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
