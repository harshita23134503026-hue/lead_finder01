"""
Email agents configuration file.
Define your email agents (Gmail, SendGrid) here.
"""

# Gmail Configuration (Multiple accounts for rotation)
GMAIL_AGENTS = [
    {
        "email": "your-email-1@gmail.com",
        "app_password": "xxxx xxxx xxxx xxxx",  # Generate from Gmail app passwords
        "daily_limit": 100,
        "hourly_limit": 50
    },
    {
        "email": "your-email-2@gmail.com",
        "app_password": "xxxx xxxx xxxx xxxx",
        "daily_limit": 100,
        "hourly_limit": 50
    }
]

# SendGrid Configuration
SENDGRID_API_KEY = "SG.your_api_key_here"

# Proxy Configuration (optional - for IP rotation)
PROXIES = [
    # {
    #     "http": "http://proxy1.com:8080",
    #     "https": "http://proxy1.com:8080"
    # },
    # {
    #     "http": "http://proxy2.com:8080",
    #     "https": "http://proxy2.com:8080"
    # }
]

# Campaign Settings
CAMPAIGN_CONFIG = {
    "rate_limit_per_hour": 50,
    "rate_limit_per_day": 400,
    "min_delay_between_sends": 5,  # seconds
    "max_delay_between_sends": 15,  # seconds
    "agent_cooldown_period": 600,  # seconds (10 minutes)
    "min_quality_score": 60.0,
    "enable_proxy_rotation": False,
    "enable_human_behavior": True,
    "enable_email_tracking": True
}

# Email Template Settings
EMAIL_TEMPLATES = {
    "default": """
Hi {first_name},

I came across your profile and was impressed by your background.

I wanted to reach out because I think there might be a great opportunity for you.

Would you be open to a quick 15-minute call this week?

Best regards!
""",
    "recruiter": """
Hi {first_name},

I noticed your {job_title} role at {company}.

We're looking for someone with your expertise for an exciting opportunity.

Would you be interested in discussing this further?

Looking forward to connecting!
""",
    "freelancer": """
Hi {first_name},

Your freelance work caught my attention.

I have a project that might be perfect for your skills.

Are you open to new opportunities?

Thanks for your time!
"""
}
