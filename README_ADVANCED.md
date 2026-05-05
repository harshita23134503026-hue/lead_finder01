# Advanced LinkedIn Lead Finder with AIML & Email Campaigns

A sophisticated system for finding LinkedIn leads and running targeted email campaigns with intelligent agent rotation, AIML-based lead scoring, and advanced anti-spam measures.

## 🚀 Key Features

### AIML/Machine Learning
- ✅ **Lead Quality Scoring** - ML-based scoring (0-100) based on job title, company, industry
- ✅ **Personalized Email Generation** - Dynamic email creation with context extraction
- ✅ **Send Time Optimization** - Predict optimal send time by timezone and industry
- ✅ **Subject Line Optimization** - Generate multiple high-CTR subject lines

### Advanced Email Campaigns
- ✅ **Multi-Agent System** - Rotate between multiple Gmail accounts & SendGrid
- ✅ **Automatic Failover** - Switch agents when one gets banned or fails
- ✅ **Email Deduplication** - Never send twice to same address
- ✅ **Bulk Campaign Send** - Send to hundreds of leads in one go
- ✅ **Hybrid Email Service** - Gmail + SendGrid with automatic fallback

### Anti-Spam/Ban Prevention
- ✅ **Rate Limiting** - 50 emails/hour per agent, 400/day limit
- ✅ **Human-like Behavior** - Random delays (5-15s), variable patterns
- ✅ **Agent Health Monitoring** - Track bounce rates, auto-disable if >5%
- ✅ **IP Rotation** - Optional proxy rotation to prevent IP blocking
- ✅ **Bounce Handling** - Track and respond to hard/soft bounces

### Credit System & Tracking
- ✅ **API Credit Tracking** - Monitor credits for LinkedIn searches and emails
- ✅ **Real-time Balance** - See remaining credits anytime
- ✅ **Operation Costs** - Clear pricing for each operation type
- ✅ **Usage Reports** - Daily/weekly/monthly breakdowns
- ✅ **Alerts** - Warnings when credits run low

### Database & Analytics
- ✅ **SQLite Storage** - Email history, agent status, lead quality scores
- ✅ **Campaign Tracking** - Track sends, opens, clicks, bounces per campaign
- ✅ **Duplicate Prevention** - Permanent record prevents re-sends
- ✅ **Agent Analytics** - Monitor each agent's performance and reputation

## 📋 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your_token_here

# Gmail (Optional - for sending emails)
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# SendGrid (Optional - for backup email sending)
SENDGRID_API_KEY=SG.your_key_here

# Credits
INITIAL_CREDITS=1000
```

### 3. Get Gmail App Password

If using Gmail for sending:
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Generate password (16 characters with spaces)
4. Add to `.env` as `GMAIL_APP_PASSWORD`

### 4. Get SendGrid API Key

If using SendGrid:
1. Sign up at https://sendgrid.com/
2. Go to Settings → API Keys
3. Create new API key
4. Add to `.env` as `SENDGRID_API_KEY`

## 🎯 Usage Workflow

### Step 1: Search and Extract Leads

```bash
python lead.py --keywords "Manager" --location "USA" --limit 100 --output "managers.csv"
```

This exports leads to CSV with: Name, LinkedIn URL, Email, Phone, Job Title, Company, Location

### Step 2: Check Credit Balance

```bash
python campaign_cli.py status
```

Shows available credits for remaining operations.

### Step 3: Configure Email Agents

```bash
python campaign_cli.py configure --add-gmail
```

This registers your Gmail account as an email agent.

### Step 4: Send Email Campaign

```bash
python campaign_cli.py send --csv managers.csv --campaign "Q1 Manager Outreach" --min-score 75
```

Options:
- `--csv` - Path to leads CSV file
- `--campaign` - Campaign name (for tracking)
- `--min-score` - Minimum quality score (0-100, default: 60)
- `--batch-size` - Emails per batch (default: 10)
- `--template` - Custom email template file

### Complete Example Workflow

```bash
# 1. Search for video editors in USA
python lead.py --keywords "Video Editor" --location "USA" --limit 200 --output "video_editors.csv"

# 2. Check your credits
python campaign_cli.py status

# 3. Configure Gmail agent (one-time setup)
python campaign_cli.py configure --add-gmail

# 4. Send emails to top-quality leads
python campaign_cli.py send --csv video_editors.csv \
  --campaign "Video Studio Recruitment" \
  --min-score 70 \
  --batch-size 15
```

## 💳 Credit System Explained

### Operation Costs

| Operation | Cost |
|-----------|------|
| LinkedIn Search | 1.0 credit |
| Email (Gmail) | 0.5 credit |
| Email (SendGrid) | 1.0 credit |
| Lead Quality Scoring | 0.1 credit |
| Email Personalization | 0.1 credit |
| Send Time Optimization | 0.05 credit |
| Subject Optimization | 0.05 credit |

### Example Cost Calculation

Sending 100 personalized emails to filtered leads:
- Lead quality scoring: 100 × 0.1 = 10 credits
- Email personalization: 100 × 0.1 = 10 credits
- Email sending: 100 × 0.5 = 50 credits
- **Total: 70 credits**

With 1000 credits, you can send ~14 campaigns of 100 leads each.

### Tracking Credits

```python
from credit_tracker import CreditTracker
from database_manager import DatabaseManager

db = DatabaseManager()
tracker = CreditTracker(initial_credits=1000, db_manager=db)

# Check balance
balance = tracker.get_balance()

# See what you can do
estimates = tracker.get_estimated_operations()
# Output: {'email_send_gmail': 2000, 'linkedin_search': 1000, ...}

# Display full status
tracker.display_status()
```

## 🤖 AIML Components

### Lead Quality Scoring

Scores leads 0-100 based on:
- **Job Title** (Manager=0.9, CEO=1.0, Developer=0.6)
- **Company Size** (1000+ employees=0.98)
- **Industry** (Technology=0.9, Finance=0.85)
- **Contact Info** (Email=+10, Phone=+10)
- **Location** (USA/UK/Europe=+5)

```python
from aiml_engine import LeadQualityScorer

scorer = LeadQualityScorer()

lead = {
    "name": "John Doe",
    "job_title": "Engineering Manager",
    "company": "Google",
    "location": "San Francisco",
    "email": "john@google.com",
    "phone": "+1-555-0100"
}

score = scorer.score_lead(lead)  # Returns: 92.5
response_rate = scorer.get_predicted_response_rate(lead)  # Returns: 0.95
```

### Email Personalization

Generates personalized emails based on profile:

```python
from email_personalization import EmailPersonalization

personalizer = EmailPersonalization()

lead = {
    "name": "Jane Smith",
    "job_title": "Video Editor",
    "company": "Adobe",
    "location": "Los Angeles"
}

email = personalizer.personalize_email(lead)
# Returns:
# {
#     "subject": "Opportunity for Jane",
#     "body": "Hi Jane,\n\nYour work in video editing is impressive...",
#     "personalization_level": "high"
# }
```

## 📊 Email Agent System

### Multi-Agent Rotation

```python
from email_agent_manager import EmailAgentManager
from database_manager import DatabaseManager

db = DatabaseManager()
manager = EmailAgentManager(db)

# Add multiple Gmail accounts
manager.add_agent("agent1@gmail.com", "gmail")
manager.add_agent("agent2@gmail.com", "gmail")
manager.add_agent("agent3@gmail.com", "gmail")

# Get next agent (automatic rotation)
agent = manager.get_next_agent()
# Returns: {'email_account': 'agent1@gmail.com', 'service': 'gmail', ...}

# Display all agents
manager.display_agent_status()
```

### Agent Health Monitoring

Each agent is tracked for:
- Bounce rate (auto-banned if >5%)
- Emails sent today/total
- Last used timestamp
- Service type (Gmail/SendGrid)
- Current status (active/banned/cooldown)

### Automatic Failover

When an agent fails:
1. Email send marked as failed
2. Agent moved to cooldown
3. Automatically try next agent
4. Continue campaign seamlessly

## ⚙️ Rate Limiting & Anti-Spam

### Rate Limits

Per agent:
- 50 emails/hour (1 email per 72 seconds)
- 400 emails/day
- Automatic cooldown after limits exceeded

Global:
- 500 emails/hour (across all agents)
- 4000 emails/day (across all agents)

### Human-Like Behavior

- **Random delays**: 5-15 seconds between sends
- **Day/time variation**: Sends at different hours each day
- **User agent rotation**: Different browser headers
- **Pattern avoidance**: No exactly-on-the-hour sends

```python
from rate_limiter import HumanBehaviorSimulator

# Get random delay
delay = HumanBehaviorSimulator.get_random_delay(5, 15)
time.sleep(delay)

# Get optimal send time
send_time = HumanBehaviorSimulator.get_optimal_send_time("USA")

# Get random user agent
ua = HumanBehaviorSimulator.get_random_user_agent()
```

## 📈 Campaign Management

### Launch Campaign

```bash
python campaign_cli.py send --csv leads.csv --campaign "My Campaign"
```

### Campaign Tracking

All campaigns tracked in SQLite database:
- Campaign ID and name
- Total leads sent
- Bounce count
- Opens and clicks (if tracking enabled)
- Sent/failed/skipped counts
- Timestamps

### Deduplication

System prevents duplicate sends:
1. Checks database before sending
2. Unique constraint on email address
3. Never re-sends to same recipient
4. Can span multiple campaigns

## 🛡️ Spam Prevention Best Practices

### Email Quality

1. **Personalize all emails** - Generic emails trigger spam filters
2. **Include unsubscribe link** - Legal requirement, improves deliverability
3. **Use professional tone** - Avoid marketing language
4. **Keep emails short** - 50-200 words optimal
5. **Limit links** - One call-to-action link max

### Infrastructure Setup

1. **Gmail**: Use business domain (not free @gmail accounts for best delivery)
2. **SendGrid**: Verify sender domain, set up SPF/DKIM
3. **Sender Policy Framework (SPF)**: Add to DNS records
4. **DKIM**: Digital signature for emails
5. **DMARC**: Email authentication protocol

### Monitoring

1. **Check bounce rates** - Should be <2%
2. **Monitor agent health** - Auto-disable if issues detected
3. **Track opens** - Indicator of email quality
4. **Review feedback loops** - Suppress complaints

## 📊 Database Schema

### Tables

1. **email_sent** - Log of all sent emails
   - recipient_email (unique)
   - campaign_id
   - agent_used
   - status (sent/bounced/failed)
   - timestamp

2. **agents** - Email agent tracking
   - email_account (unique)
   - service (gmail/sendgrid)
   - status (active/banned/cooldown)
   - emails_sent_today/total
   - bounce_rate

3. **api_credits** - Credit ledger
   - operation_type
   - credits_used
   - timestamp
   - remaining_balance

4. **campaigns** - Campaign tracking
   - campaign_id (unique)
   - name
   - total_leads
   - sent/open/bounce counts

5. **leads_quality** - Lead scoring cache
   - email (unique)
   - quality_score
   - predicted_response_rate

## 🔧 Advanced Configuration

### Custom Email Templates

Create a template file (template.txt):
```
Subject: Opportunity for {first_name}

Hi {first_name},

Your background at {company} is impressive.

Would you be interested in exploring a new opportunity?

Best regards!
```

Use in campaign:
```bash
python campaign_cli.py send --csv leads.csv --template template.txt
```

### Proxy Configuration

For IP rotation (optional):
```python
PROXIES = [
    {"http": "http://proxy1.com:8080", "https": "http://proxy1.com:8080"},
    {"http": "http://proxy2.com:8080", "https": "http://proxy2.com:8080"}
]
```

### Adjust Rate Limits

Edit `agents_config.py`:
```python
CAMPAIGN_CONFIG = {
    "rate_limit_per_hour": 75,  # Increase from 50
    "rate_limit_per_day": 600,  # Increase from 400
    "min_delay_between_sends": 3,  # Decrease from 5
}
```

## 📖 API Reference

### EmailCampaign

```python
from email_campaign import EmailCampaign
from database_manager import DatabaseManager
from credit_tracker import CreditTracker

db = DatabaseManager()
credits = CreditTracker(1000, db)

campaign = EmailCampaign("My Campaign", db, credits)

# Load CSV
total, filtered = campaign.load_csv("leads.csv", min_quality_score=75)

# Configure email service
campaign.configure_email_service(
    gmail_config={"email": "...", "password": "..."},
    sendgrid_key="SG...."
)

# Send campaign
results = campaign.send_campaign_batch(batch_size=20)

# Get status
status = campaign.get_campaign_status()
```

### CreditTracker

```python
from credit_tracker import CreditTracker

tracker = CreditTracker(initial_credits=1000)

# Check balance
balance = tracker.get_balance()

# Deduct credits
tracker.deduct_credits("email_send_gmail", count=100)

# Get status
status = tracker.get_credit_status()
tracker.display_status()

# Bulk operations
operations = {"email_send_gmail": 50, "lead_scoring": 50}
success, result = tracker.bulk_deduct(operations)
```

## 🚨 Troubleshooting

### Gmail Authentication Fails

- Verify Gmail address in `.env`
- Generate new app password (not account password)
- Enable "Less secure apps" (if using business account)
- Check for 2FA enabled

### No Leads After Filtering

- Lower `--min-score` threshold
- Expand search criteria (keywords, location)
- Check CSV format matches expected headers
- Verify email addresses are valid

### Emails Going to Spam

- Use real name (not just email domain)
- Add unsubscribe link
- Personalize all emails
- Test with mail testing services (mail-tester.com)
- Set up SPF/DKIM records

### Rate Limit Exceeded

- Add more Gmail agents to distribute load
- Reduce batch size
- Increase delays between sends
- Use SendGrid as backup service

### High Bounce Rates

- Verify email sources are quality
- Use higher quality score threshold
- Check for stale email lists
- Test leads before full campaign

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review log files for error details
3. Verify all .env credentials
4. Ensure dependencies installed correctly

## ⚖️ Legal & Compliance

- ✅ Uses official APIs (respect Terms of Service)
- ✅ Includes unsubscribe links (CAN-SPAM compliant)
- ✅ Respects rate limits (prevents abuse)
- ✅ Transparent logging (audit trail)
- ✅ Data privacy (SQLite local storage)

Always comply with:
- LinkedIn's Terms of Service
- CAN-SPAM Act (for email marketing)
- GDPR (for EU residents)
- Local email marketing regulations

## 🎓 Examples

### Recruit Video Editors

```bash
# Search for video editors
python lead.py --keywords "Video Editor" --location "USA" --limit 500 \
  --output "video_editors.csv"

# Send recruitment emails
python campaign_cli.py send --csv video_editors.csv \
  --campaign "Video Studio Team Expansion" \
  --min-score 80 \
  --batch-size 25
```

### Outreach to Company Managers

```bash
# Find managers at specific companies
python lead.py --keywords "Manager" --company "Google" --location "USA" \
  --limit 200 --output "google_managers.csv"

# Launch campaign
python campaign_cli.py send --csv google_managers.csv \
  --campaign "Executive Recruitment Drive" \
  --min-score 85
```

### Freelancer Outreach

```bash
# Find freelancers with specific skills
python lead.py --keywords "Freelancer" --industry "Technology" \
  --limit 300 --output "freelancers.csv"

# Send project opportunities
python campaign_cli.py send --csv freelancers.csv \
  --campaign "Project Opportunities Q1" \
  --min-score 65
```

---

**Happy campaigning! 🚀**

For advanced features or customization, review the source code or extend the modules as needed.
