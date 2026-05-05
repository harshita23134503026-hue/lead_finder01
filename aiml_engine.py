import logging
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeadQualityScorer:
    """ML-based lead quality scoring system."""

    def __init__(self):
        self.job_title_weights = {
            "manager": 0.9,
            "director": 0.95,
            "ceo": 1.0,
            "founder": 0.95,
            "lead": 0.85,
            "head": 0.9,
            "vp": 0.95,
            "vice president": 0.95,
            "executive": 0.9,
            "owner": 0.95,
            "partner": 0.9,
            "producer": 0.8,
            "editor": 0.75,
            "developer": 0.6,
            "engineer": 0.65,
            "analyst": 0.55,
            "freelancer": 0.7,
            "contractor": 0.65
        }

        self.company_size_weights = {
            "1-10": 0.8,
            "11-50": 0.85,
            "51-200": 0.9,
            "201-500": 0.92,
            "501-1000": 0.95,
            "1000+": 0.98
        }

        self.industry_weights = {
            "technology": 0.9,
            "media": 0.88,
            "entertainment": 0.87,
            "recruiting": 0.95,
            "finance": 0.85,
            "healthcare": 0.82,
            "education": 0.75,
            "consulting": 0.88,
            "marketing": 0.85,
            "sales": 0.8
        }

    def score_lead(self, lead: Dict[str, Any]) -> float:
        """
        Calculate quality score for a lead (0-100).
        Based on: job title, company size, industry, location
        """
        try:
            score = 50.0

            job_title = lead.get("job_title", "").lower()
            company = lead.get("company", "").lower()
            industry = lead.get("industry", "").lower()

            title_score = self._score_job_title(job_title)
            score += title_score * 20

            company_score = self._score_company_relevance(company)
            score += company_score * 15

            industry_score = self._score_industry(industry)
            score += industry_score * 15

            email_score = 10 if lead.get("email") and lead.get("email") != "N/A" else 0
            score += email_score

            phone_score = 10 if lead.get("phone") and lead.get("phone") != "N/A" else 0
            score += phone_score

            location_score = self._score_location(lead.get("location", ""))
            score += location_score

            score = max(0, min(100, score))
            logger.debug(f"Lead quality score for {lead.get('email', 'unknown')}: {score:.2f}")
            return score

        except Exception as e:
            logger.warning(f"Error scoring lead: {str(e)}")
            return 50.0

    def _score_job_title(self, title: str) -> float:
        """Score based on job title relevance."""
        if not title or title == "n/a":
            return 0.5

        title_lower = title.lower()
        for keyword, weight in self.job_title_weights.items():
            if keyword in title_lower:
                return weight

        return 0.6

    def _score_company_relevance(self, company: str) -> float:
        """Score based on company type/size."""
        if not company or company == "n/a":
            return 0.6

        company_lower = company.lower()

        large_companies = ["google", "apple", "microsoft", "amazon", "meta", "netflix", "adobe"]
        if any(comp in company_lower for comp in large_companies):
            return 0.95

        if any(word in company_lower for word in ["startup", "small", "indie"]):
            return 0.7

        return 0.75

    def _score_industry(self, industry: str) -> float:
        """Score based on industry."""
        if not industry or industry == "n/a":
            return 0.5

        industry_lower = industry.lower()
        for ind_key, weight in self.industry_weights.items():
            if ind_key in industry_lower:
                return weight

        return 0.6

    def _score_location(self, location: str) -> float:
        """Score based on location (US/EU prioritized)."""
        if not location or location == "n/a":
            return 0

        location_lower = location.lower()

        high_value_locations = ["usa", "united states", "uk", "europe", "san francisco", "new york", "london"]
        if any(loc in location_lower for loc in high_value_locations):
            return 5

        return 3

    def filter_leads_by_quality(self, leads: List[Dict[str, Any]], min_score: float = 60.0) -> List[Dict[str, Any]]:
        """Filter leads by minimum quality score."""
        filtered = []

        for lead in leads:
            score = self.score_lead(lead)
            if score >= min_score:
                lead["quality_score"] = score
                filtered.append(lead)
            else:
                logger.debug(f"Filtered out lead {lead.get('email')} with score {score:.2f}")

        logger.info(f"Filtered {len(leads)} leads to {len(filtered)} high-quality leads (min score: {min_score})")
        return filtered

    def rank_leads_by_quality(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank leads by quality score (highest first)."""
        scored_leads = []

        for lead in leads:
            lead["quality_score"] = self.score_lead(lead)
            scored_leads.append(lead)

        sorted_leads = sorted(scored_leads, key=lambda x: x.get("quality_score", 0), reverse=True)
        logger.info(f"Ranked {len(sorted_leads)} leads by quality")
        return sorted_leads

    def get_predicted_response_rate(self, lead: Dict[str, Any]) -> float:
        """Predict response rate for a lead (0-1)."""
        score = lead.get("quality_score", self.score_lead(lead))
        base_rate = score / 100.0

        if lead.get("email") and lead.get("email") != "N/A":
            base_rate += 0.05

        if lead.get("phone") and lead.get("phone") != "N/A":
            base_rate += 0.05

        return min(1.0, base_rate)
