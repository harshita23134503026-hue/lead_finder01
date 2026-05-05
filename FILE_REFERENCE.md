# File Reference Guide

## Quick Navigation

### 🎯 Want to...

| Goal | File(s) | Command |
|------|---------|---------|
| **Search for leads** | lead.py | `python lead.py --keywords "Manager"` |
| **Send emails** | campaign_cli.py | `python campaign_cli.py send --csv leads.csv` |
| **Check credits** | campaign_cli.py | `python campaign_cli.py status` |
| **Add email agent** | campaign_cli.py | `python campaign_cli.py configure --add-gmail` |
| **Setup project** | .env.example | `cp .env.example .env` |
| **Learn basics** | QUICKSTART.md | Read this first! |
| **Advanced setup** | README_ADVANCED.md | Detailed reference |
| **Understand system** | BUILD_SUMMARY.md | Architecture overview |

---

## File-by-File Breakdown

### 📋 Configuration Files

**`.env.example`**
- Template for credentials
- LinkedIn API token, Gmail password, SendGrid key
- Credit settings
- Copy to `.env` and fill with your values

**`.env`** (Create this)
- Your actual credentials
- NEVER commit to git
- Created after copying `.env.example`

**`config.py`**
- Core system settings
- API URLs and timeouts
- Output directory paths
- Loads from `.env` file

**`agents_config.py`**
- Email agent templates
- Campaign settings
- Rate limits and delays
- Email template examples
- Proxy configuration (optional)

**`requirements.txt`**
- Python package dependencies
- Run: `pip install -r requirements.txt`
- 8 packages listed with versions

---

### 🔍 Lead Discovery (Original)

**`lead.py`** - Main CLI for searching
- Entry point for lead searching
- Arguments: keywords, company, location, industry, limit, output
- Exports results to CSV
- Example: `python lead.py --keywords "Manager" --limit 50`

**`linkedin_client.py`** - LinkedIn API wrapper
- OAuth 2.0 authentication
- API request handling with retries
- Rate limiting built-in
- Profile data extraction

**`lead_searcher.py`** - Search orchestration
- Combines multiple searches
- Deduplicates results
- Manages search state

**`data_processor.py`** - Data cleaning
- Validates and cleans lead data
- Normalizes email/phone formats
- Removes invalid records
- Validates quality before export

**`csv_exporter.py`** - CSV output
- Exports leads to CSV format
- Supports append mode
- Generates file statistics
- Auto-creates output directory

---

### 🤖 AI/ML Intelligence (NEW)

**`aiml_engine.py`** - Lead quality scoring
- Scores leads 0-100 based on:
  - Job title (Manager=0.9, CEO=1.0)
  - Company size (larger = higher score)
  - Industry relevance
  - Contact info availability
  - Location
- Predicts response probability
- Filters low-quality leads

**`email_personalization.py`** - Email generation
- Creates personalized emails from templates
- Extracts first name, company, job title
- Generates multiple subject line options
- Customizes greeting and CTA based on profile
- Adds unsubscribe footer
- Validates email quality

**`rate_limiter.py`** - Rate limiting + human behavior
- Token bucket algorithm
- Per-agent rate limits (50/hr, 400/day)
- Global rate limits (500/hr, 4000/day)
- Human-like delays (5-15 sec random)
- Optimal send time calculation
- Random user agent strings
- Anti-pattern detection

---

### 📧 Email Campaign (NEW)

**`email_campaign.py`** - Campaign orchestration
- Main campaign control system
- Loads CSV with leads
- Filters by quality score
- Orchestrates batch sending
- Checks for duplicates
- Personalizes each email
- Manages agent rotation
- Tracks campaign metrics
- Generates reports

**`campaign_cli.py`** - Campaign CLI
- Command-line interface for campaigns
- 4 subcommands: search, configure, send, status
- Argument parsing and validation
- Integration with all subsystems
- Progress reporting
- Human-friendly output

**`email_agent_manager.py`** - Agent management
- Manages pool of email agents
- Agent health monitoring
- Round-robin rotation
- Automatic failover on failure
- Rate limit tracking per agent
- Bounce rate monitoring
- Auto-ban on high bounce rate
- Agent warmup support

**`email_sender.py`** - Email sending
- Gmail SMTP implementation
- SendGrid API implementation
- Hybrid sender with automatic fallover
- Connection management
- Credential validation
- Error handling with retries

---

### 💾 Database & Tracking (NEW)

**`database_manager.py`** - SQLite management
- Creates 5 database tables:
  1. email_sent (deduplication)
  2. agents (agent tracking)
  3. api_credits (credit ledger)
  4. campaigns (campaign metrics)
  5. leads_quality (lead scores)
- Manages all database operations
- Implements unique constraints
- Creates indexes for performance
- Handles concurrent access

**`credit_tracker.py`** - Credit ledger
- Tracks API usage credits
- Tracks operation costs
- Maintains running balance
- Estimates future operations
- Provides usage reports
- Alerts on low credits
- Supports bulk deductions

---

### 📚 Documentation

**`README.md`** (7.4 KB)
- Basic features overview
- Setup instructions
- Original lead finder features
- Command reference
- Limitations and troubleshooting

**`README_ADVANCED.md`** (15 KB)
- Complete feature reference
- Advanced setup instructions
- AIML component explanation
- Email agent system details
- Rate limiting explanation
- Campaign management guide
- API reference
- Real-world examples
- Troubleshooting guide
- Best practices

**`QUICKSTART.md`** (6.4 KB)
- 5-minute setup
- First campaign walkthrough
- Command explanations
- Real-world examples
- Pro tips
- Common issues
- Next steps
- Security notes

**`BUILD_SUMMARY.md`** (This file)
- Architecture overview
- File structure
- Feature matrix
- Database schema
- Usage workflow
- Performance metrics
- Technical stack
- Deployment checklist

---

### 📁 Directories (Created at Runtime)

**`leads/`**
- CSV export directory
- SQLite database file
- Campaign logs

**`campaigns/`** (Optional)
- Campaign reports
- Email templates
- Performance logs

---

## File Dependencies

```
lead.py
  ├─ config.py
  ├─ linkedin_client.py
  ├─ lead_searcher.py
  ├─ data_processor.py
  └─ csv_exporter.py

campaign_cli.py
  ├─ database_manager.py
  ├─ credit_tracker.py
  ├─ email_agent_manager.py
  ├─ email_campaign.py
  ├─ lead.py (for search command)
  └─ config.py

email_campaign.py
  ├─ database_manager.py
  ├─ credit_tracker.py
  ├─ email_agent_manager.py
  ├─ email_sender.py
  ├─ email_personalization.py
  ├─ aiml_engine.py
  └─ rate_limiter.py

email_agent_manager.py
  ├─ database_manager.py
  ├─ rate_limiter.py
  └─ (no external deps)

email_sender.py
  ├─ rate_limiter.py
  ├─ sendgrid (optional)
  └─ smtplib (stdlib)
```

---

## Import Order (If Starting Fresh)

1. Install dependencies: `pip install -r requirements.txt`
2. Configure: Edit `.env` file
3. Initialize database: Run any campaign_cli command (auto-creates)
4. Test search: `python lead.py --keywords "test" --limit 5`
5. Configure agents: `python campaign_cli.py configure --add-gmail`
6. Run campaign: `python campaign_cli.py send --csv leads.csv`

---

## Key Variables & Configuration

### In `.env`
```
LINKEDIN_ACCESS_TOKEN=          # Required for searching
GMAIL_EMAIL=                    # Optional for Gmail sending
GMAIL_APP_PASSWORD=             # Optional for Gmail
SENDGRID_API_KEY=              # Optional for SendGrid
INITIAL_CREDITS=1000           # Starting credits balance
```

### In `config.py`
```
REQUEST_TIMEOUT = 30           # API timeout in seconds
MAX_RETRIES = 3                # Retry attempts
RETRY_DELAY = 2                # Retry wait time
CSV_HEADERS = [...]            # Column names
```

### In `agents_config.py`
```
GMAIL_AGENTS = [...]           # Gmail account pool
SENDGRID_API_KEY = ""          # SendGrid key
CAMPAIGN_CONFIG = {...}        # Rate limits and behavior
```

---

## Size & Performance

| File | Size | Purpose |
|------|------|---------|
| email_campaign.py | ~11KB | Core campaign logic |
| database_manager.py | ~12KB | Database operations |
| linkedin_client.py | ~6.5KB | API wrapper |
| email_personalization.py | ~7.1KB | Email generation |
| email_agent_manager.py | ~7.1KB | Agent management |
| email_sender.py | ~6.7KB | Email sending |
| aiml_engine.py | ~5.9KB | Lead scoring |
| campaign_cli.py | ~6.3KB | CLI interface |
| rate_limiter.py | ~5.1KB | Rate limiting |
| Total | ~60KB | All modules |

---

## Which Files to Modify

### For Users (Most Common)
- `.env` - Add your credentials
- `agents_config.py` - Adjust rate limits, add proxies
- Email templates in `email_personalization.py`

### For Developers (Advanced)
- `aiml_engine.py` - Adjust scoring weights
- `rate_limiter.py` - Fine-tune rate limits
- `email_personalization.py` - Add new templates
- `database_manager.py` - Add new tracking fields

### DO NOT MODIFY (Unless You Know What You're Doing)
- `config.py` - Core paths and settings
- `database_manager.py` - Schema (breaks existing data)
- `credit_tracker.py` - Cost structure

---

## Troubleshooting by File

| Issue | Check File |
|-------|-----------|
| Lead search fails | linkedin_client.py, config.py |
| Email sending fails | email_sender.py, .env |
| Database errors | database_manager.py |
| Rate limit issues | rate_limiter.py, agents_config.py |
| Duplicate emails | database_manager.py (email_sent table) |
| Low credit balance | credit_tracker.py |
| Agent not rotating | email_agent_manager.py |
| Email not personalized | email_personalization.py |
| Bad quality scores | aiml_engine.py |
| Campaign won't launch | email_campaign.py, campaign_cli.py |

---

## Testing Checklist

- [ ] `python -m py_compile *.py` - All files compile
- [ ] `python campaign_cli.py --help` - CLI works
- [ ] `python lead.py --keywords "test" --limit 5` - Search works
- [ ] `python campaign_cli.py status` - Status command works
- [ ] Database file created in `leads/leads_manager.db`
- [ ] CSV file created in `leads/` directory

---

*For more information, see README_ADVANCED.md or QUICKSTART.md*
