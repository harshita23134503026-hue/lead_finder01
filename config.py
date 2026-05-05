import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_API_BASE_URL = "https://api.linkedin.com/v2"

API_VERSION = "v2"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

OUTPUT_DIR = "leads"
CSV_HEADERS = ["Name", "LinkedIn URL", "Email", "Phone", "Job Title", "Company", "Location", "Extraction Date"]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
