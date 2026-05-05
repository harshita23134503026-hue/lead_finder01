# Quick Start Guide - Advanced LinkedIn Lead Finder

## 🎯 5-Minute Setup

### 1. Verify Installation
```bash
cd "c:\Users\khush\OneDrive\Desktop\linkedIn"
python campaign_cli.py --help  # Should show all commands
```

### 2. Create .env File
```bash
cp .env.example .env
```

Edit `.env` and add:
```
LINKEDIN_ACCESS_TOKEN=your_token_here
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
INITIAL_CREDITS=1000
```

### 3. Quick Test - Search Leads
```bash
python lead.py --keywords "Manager" --location "USA" --limit 10 --output "test.csv"
```

## 📧 Send Your First Campaign

### Step 1: Load Leads from CSV
```bash
# You already have test.csv from above, or create your own
# CSV must have columns: Name, Email, Job Title, Company, Location
```

### Step 2: Check Credit Balance
```bash
python campaign_cli.py status
```

### Step 3: Configure Email Agent
```bash
python campaign_cli.py configure --add-gmail
```

### Step 4: Send Campaign
```bash
python campaign_cli.py send --csv test.csv --campaign "Test Campaign" --min-score 60
```

## 📊 What Each Command Does

| Command | What It Does | Example |
|---------|-------------|---------|
| `lead.py` | Search LinkedIn and export leads | `python lead.py --keywords "Manager" --limit 50` |
| `campaign_cli.py search` | Same as lead.py (alternative) | `python campaign_cli.py search --keywords "Manager"` |
| `campaign_cli.py status` | Show credits and agent health | `python campaign_cli.py status` |
| `campaign_cli.py configure` | Register email agents | `python campaign_cli.py configure --add-gmail` |
| `campaign_cli.py send` | Send emails to leads | `python campaign_cli.py send --csv leads.csv` |

## 🔑 Key Features Explained

### AIML/ML Scoring
Every lead gets a quality score (0-100):
- **90-100**: Highly likely to respond (C-level, managers at big tech)
- **70-89**: Good fit (mid-level roles, relevant industry)
- **50-69**: Moderate fit (general roles, smaller companies)
- **<50**: Lower priority (junior roles, unrelated industries)

Only leads with score ≥ specified threshold are sent emails.

### Multi-Agent Email Rotation
- Add multiple Gmail accounts
- System automatically rotates between them
- If one account gets rate-limited or banned, switches to next
- Prevents single account from getting blocked

### Anti-Ban Protection
- Limits: 50 emails/hour per agent, 400/day
- Random delays: 5-15 seconds between sends
- Sends at different times (avoids patterns)
- Automatic bounce detection
- Proxy rotation support (optional)

### Credit System
- Each operation costs credits
- Search: 1 credit
- Email send: 0.5-1 credit
- Start with 1000 credits
- See what you can do: `python campaign_cli.py status`

## 🚀 Real-World Examples

### Recruit Video Editors
```bash
# Find video editors across USA
python lead.py --keywords "Video Editor" --location "USA" --limit 500 --output "video_editors.csv"

# Send recruitment emails to top 200
python campaign_cli.py send --csv video_editors.csv --campaign "Video Studio Hiring" --min-score 80 --batch-size 20
```

### Reach Out to Company Managers
```bash
# Find all managers at Apple
python lead.py --keywords "Manager" --company "Apple" --location "USA" --limit 200 --output "apple_managers.csv"

# Send to high-quality leads only
python campaign_cli.py send --csv apple_managers.csv --campaign "Apple Manager Outreach" --min-score 85
```

### Freelancer Outreach
```bash
# Find freelancers with tech background
python lead.py --keywords "Freelancer" --industry "Technology" --limit 300 --output "freelancers.csv"

# Send project opportunities
python campaign_cli.py send --csv freelancers.csv --campaign "Q1 Projects" --min-score 65
```

## 💡 Pro Tips

1. **Start Small**: Test with 10-20 emails first before scaling
2. **Quality Over Quantity**: Higher quality score = more responses
3. **Multiple Agents**: Add 2-3 Gmail accounts for better distribution
4. **Monitor Bounces**: If bounce rate >5%, pause that agent
5. **Personalization Helps**: Let the system customize each email
6. **Track Results**: Check database for open rates and responses

## 🆘 Common Issues

### "Database is locked"
- Close other programs accessing the database
- Or: Wait 30 seconds and try again

### "Gmail authentication failed"
- Check your app password (not regular password)
- Generate new one at: myaccount.google.com/apppasswords
- Update .env file

### "No leads found"
- Check CSV format (needs Email column)
- Lower min-score threshold
- Expand search criteria

### "Rate limit exceeded"
- Wait 1 hour or add more Gmail accounts
- Reduce batch size
- Increase delays in config

## 📈 Expected Performance

With proper setup:
- **Delivery Rate**: 95%+ (if emails personalized and credits high)
- **Bounce Rate**: <2% (indicates quality leads)
- **Response Rate**: 2-5% (depends on targeting and message)
- **Email Speed**: 50-60 emails/hour per agent

## 🔒 Security Notes

- **Never commit .env file** to version control
- **Keep API keys private** - treat like passwords
- **Use app passwords** for Gmail, not account password
- **Database is local** - no data sent to external servers
- **Audit logs** stored in database for compliance

## 📚 Full Documentation

For advanced features, configuration, and troubleshooting:
- Read: `README_ADVANCED.md` in project directory
- Check: `agents_config.py` for campaign settings
- Reference: Source code comments in each module

## ✅ Checklist Before Full Campaign

- [ ] `.env` file created with all credentials
- [ ] Tested lead search: `python lead.py --keywords "test" --limit 5`
- [ ] Checked credits: `python campaign_cli.py status`
- [ ] Configured agent: `python campaign_cli.py configure --add-gmail`
- [ ] Tested send to 1-2 emails: `python campaign_cli.py send --csv test.csv --batch-size 2`
- [ ] Verified emails arrive (check inbox)
- [ ] Checked for spam folder (note if landing there)
- [ ] Ready for full campaign!

## 📞 Next Steps

1. **Production Gmail**: Set up business domain email for better deliverability
2. **SendGrid Backup**: Add SendGrid for redundancy
3. **Email Tracking**: Enable click/open tracking in config
4. **Custom Templates**: Create branded email templates
5. **Proxy Rotation**: Add proxies for IP rotation (if needed)

---

**Ready to launch? Start with:**
```bash
python lead.py --keywords "your-target" --location "your-location" --limit 50 --output "my_leads.csv"
```

Then:
```bash
python campaign_cli.py send --csv my_leads.csv --campaign "My Campaign"
```

**Good luck! 🚀**
