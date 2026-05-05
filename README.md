# LinkedIn Lead Finder - Automation Tool

A Python automation tool to collect professional leads from LinkedIn using the official LinkedIn API. Perfect for recruitment, outreach campaigns, and business development.

## Features

✅ **Official LinkedIn API Integration** - Uses OAuth 2.0 for secure authentication
✅ **Multiple Search Filters** - Filter by job title, company, location, and industry
✅ **Data Enrichment** - Collects Name, LinkedIn URL, Email, Phone, Job Title, Company, Location
✅ **CSV Export** - Automatically saves leads to organized CSV files
✅ **Deduplication** - Removes duplicate profiles automatically
✅ **Rate Limiting** - Built-in retry logic and rate limit handling
✅ **Production Ready** - Error handling, logging, and data validation

## Use Cases

- 🏢 **Recruitment** - Find company managers for placement opportunities
- 🎬 **Video Production** - Locate video editors and studio professionals
- 💼 **Freelancing** - Build lists of potential freelance contractors
- 📊 **Business Development** - Generate targeted prospect lists
- 👥 **Networking** - Build qualified contact databases

## Prerequisites

1. **Python 3.7+** - Install from python.org
2. **LinkedIn Developer Account** - Create at https://linkedin.com/developers
3. **OAuth 2.0 Credentials** - Get from your LinkedIn app

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get LinkedIn API Credentials

1. Go to https://linkedin.com/developers
2. Create a new application
3. Get your **Client ID** and **Client Secret**
4. Configure authorized redirect URIs in your app settings
5. Generate an **Access Token** (or get one through OAuth flow)

### Step 3: Configure Environment Variables

Create a `.env` file in the project directory (or copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
```

**Note:** Keep your `.env` file private and never commit it to version control!

## Usage

### Basic Search

Search for managers in the USA:

```bash
python lead.py --keywords "Manager" --location "USA" --limit 50
```

### Search by Company

Find all employees at Apple:

```bash
python lead.py --company "Apple" --output apple_leads.csv
```

### Video Studio Search

Find video editors across the industry:

```bash
python lead.py --keywords "Video Editor" --location "USA" --industry "Media"
```

### Freelancer Search

Collect freelance professionals:

```bash
python lead.py --keywords "Freelancer" --limit 100
```

### Advanced Search

Combine multiple filters:

```bash
python lead.py --keywords "Product Manager" --company "Google" --location "USA" --limit 100 --output "google_pms.csv"
```

## Command-Line Options

```
--keywords TEXT       Search keywords (e.g., "Manager", "Video Editor")
--company TEXT       Filter by company name (e.g., "Apple")
--location TEXT      Filter by location (e.g., "USA", "India")
--industry TEXT      Filter by industry (e.g., "Technology", "Media")
--limit INTEGER      Maximum leads to collect (default: 50)
--output FILE        Output CSV filename (auto-generated if not specified)
--help              Show help message
```

## Output Format

Leads are saved to CSV with the following columns:

| Column | Description |
|--------|-------------|
| Name | Full name of the professional |
| LinkedIn URL | Direct link to LinkedIn profile |
| Email | Email address (if available) |
| Phone | Phone number (if available) |
| Job Title | Current job title |
| Company | Current company |
| Location | Geographic location |
| Extraction Date | When the data was collected |

Example CSV output:

```
Name,LinkedIn URL,Email,Phone,Job Title,Company,Location,Extraction Date
John Smith,https://www.linkedin.com/in/john-smith,john@example.com,+1-555-0100,Product Manager,Apple,Cupertino,2024-01-15 10:30:00
Jane Doe,https://www.linkedin.com/in/jane-doe,N/A,N/A,Video Editor,Adobe,Los Angeles,2024-01-15 10:31:00
```

## File Structure

```
linkedIn/
├── lead.py                 # Main CLI script
├── linkedin_client.py      # LinkedIn API client
├── lead_searcher.py        # Search orchestration
├── data_processor.py       # Data cleaning & validation
├── csv_exporter.py         # CSV export functionality
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── .env                    # Your credentials (DO NOT COMMIT)
├── leads/                  # Output directory for CSV files
└── README.md              # This file
```

## Output Directory

All generated CSV files are saved to the `leads/` directory with auto-generated timestamps:

```
leads/
├── leads_20240115_103000.csv
├── leads_20240115_104500.csv
└── apple_leads.csv
```

## Troubleshooting

### "LINKEDIN_ACCESS_TOKEN not set" Error

**Solution:** Make sure your `.env` file exists and contains the `LINKEDIN_ACCESS_TOKEN` variable.

### "Authentication failed" Error

**Solution:** Verify your access token is valid and hasn't expired. Generate a new one from your LinkedIn app.

### No Results Found

**Solutions:**
- Check spelling of company/location names
- Try broader keywords
- Verify API has people search permissions enabled
- Check rate limits haven't been exceeded

### Rate Limit Issues

The tool automatically handles rate limiting with exponential backoff. If you hit limits:
- Reduce the `--limit` value
- Wait before running another search
- Contact LinkedIn for higher rate limits

## API Rate Limits

LinkedIn API rate limits vary by access tier:
- **Free/Development:** Limited requests per day
- **Commercial:** Higher limits with paid plan

Check your LinkedIn app dashboard for current limits.

## Best Practices

1. **Start Small** - Test with limit of 10-20 before large searches
2. **Respect Privacy** - Only use data for legitimate business purposes
3. **Regular Updates** - Refresh data regularly as profiles change
4. **Backup Data** - Keep copies of important CSV exports
5. **Monitor Logs** - Check output for warnings and errors

## Compliance & Legal

- ✅ Uses official LinkedIn API (respects Terms of Service)
- ✅ OAuth 2.0 authentication (secure)
- ✅ No scraping or unauthorized access
- ✅ Complies with GDPR and data privacy laws

**Important:** Always comply with LinkedIn's Terms of Service and applicable data protection laws when using this tool.

## Performance Tips

- **Cache Results:** Save CSV exports and reuse them
- **Batch Processing:** Run searches during off-peak hours
- **Combine Filters:** Use specific filters to reduce result set
- **Monitor API Usage:** Track API calls in your LinkedIn dashboard

## Advanced Configuration

Edit `config.py` to customize:

```python
REQUEST_TIMEOUT = 30          # API request timeout (seconds)
MAX_RETRIES = 3               # Number of retries on failure
RETRY_DELAY = 2               # Wait time between retries (seconds)
```

## Support & Issues

For issues or feature requests:
1. Check the troubleshooting section above
2. Review LinkedIn API documentation
3. Check API credentials and permissions

## License

This tool is provided as-is for educational and commercial use.

## Version History

- **v1.0.0** (2024-01-15) - Initial release with core functionality

---

**Happy lead hunting! 🚀**
