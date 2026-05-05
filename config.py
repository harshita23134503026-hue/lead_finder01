import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_API_BASE_URL = "https://api.linkedin.com/v2"

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
HUNTER_API_BASE_URL = "https://api.hunter.io/v2"
HUNTER_RATE_LIMIT_PER_HOUR = int(os.getenv("HUNTER_RATE_LIMIT_PER_HOUR", "50"))
HUNTER_RATE_LIMIT_PER_DAY = int(os.getenv("HUNTER_RATE_LIMIT_PER_DAY", "400"))

API_VERSION = "v2"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

OUTPUT_DIR = "leads"

CSV_HEADERS = ["Name", "LinkedIn URL", "Email", "Phone", "Job Title", "Company", "Location", "Extraction Date"]
CSV_HEADERS_LINKEDIN = ["Name", "LinkedIn URL", "Email", "Phone", "Job Title", "Company", "Location", "Extraction Date", "Source"]
CSV_HEADERS_HUNTER = ["Name", "Email", "Domain", "Confidence", "Phone", "Job Title", "Company", "Location", "Extraction Date", "Source"]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
