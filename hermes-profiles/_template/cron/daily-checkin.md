# Daily Check-In Cron Job — {{agent_name}}
#
# Runs daily to check on open {{case_noun}}s and remind the team of pending
# items. This is an example resident task — the factory generates
# vertical-specific cron jobs based on the workflow.
#
# Deploy: hermes cron create "0 9 * * *" --prompt-file cron/daily-checkin.md

---
schedule: "0 9 * * *"   # 9 AM daily
delivery: telegram       # send result to the team's Telegram channel
enabled: true
---

# Daily Check-In

It's 9 AM. Run the daily check-in for {{company_name}}:

1. **Review open {{case_noun}}s** — list anything pending, stalled, or overdue
2. **Flag deadlines** — any {{case_noun}} with a deadline in the next 48 hours
3. **Supplier follow-ups** — any outstanding quote requests > 24 hours old
4. **Escalation review** — any items that hit escalation triggers yesterday

Format the summary as a concise Telegram message. Lead with what needs
attention today. Don't list things that are on track — only exceptions.

If nothing needs attention, send: "✅ All clear — no action needed today."
