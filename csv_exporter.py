import csv
import logging
import os
from typing import List, Dict, Any
from datetime import datetime
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVExporter:
    @staticmethod
    def export(leads: List[Dict[str, Any]], output_file: str = None) -> str:
        """Export leads to CSV file."""

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(config.OUTPUT_DIR, f"leads_{timestamp}.csv")
        else:
            if not output_file.endswith(".csv"):
                output_file += ".csv"

            if not os.path.isabs(output_file):
                output_file = os.path.join(config.OUTPUT_DIR, output_file)

        try:
            os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

            file_exists = os.path.isfile(output_file)

            with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=config.CSV_HEADERS)

                if not file_exists:
                    writer.writeheader()
                    logger.info(f"Created new CSV file: {output_file}")
                else:
                    logger.info(f"Appending to existing CSV file: {output_file}")

                writer.writerows(leads)

            logger.info(f"Successfully exported {len(leads)} leads to {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Failed to export CSV: {str(e)}")
            raise

    @staticmethod
    def get_file_stats(filepath: str) -> Dict[str, Any]:
        """Get statistics about a CSV file."""
        try:
            if not os.path.isfile(filepath):
                logger.warning(f"File not found: {filepath}")
                return {}

            with open(filepath, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                total_rows = len(rows)
                unique_companies = len(set(row.get("Company", "") for row in rows if row.get("Company", "") != "N/A"))
                emails_found = len([row for row in rows if row.get("Email", "") != "N/A"])
                phones_found = len([row for row in rows if row.get("Phone", "") != "N/A"])

                return {
                    "total_leads": total_rows,
                    "unique_companies": unique_companies,
                    "emails_available": emails_found,
                    "phones_available": phones_found,
                    "file_path": filepath,
                    "file_size_kb": round(os.path.getsize(filepath) / 1024, 2)
                }

        except Exception as e:
            logger.error(f"Failed to get file stats: {str(e)}")
            return {}
