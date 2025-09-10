import csv
import os
from datetime import datetime


class ReportLogger:
    def __init__(self):
        self.csv_file = None
        self.base_path = "reports/"
        os.makedirs(self.base_path, exist_ok=True)
        self.headers = [
            "Session ID", "FAQ", "Expected", "Actual", "Similarity", "Pass/Fail",
            "Hallucination", "Coverage", "LinkComparison", "LinkValidity", "FactCheck"
        ]

    def _initialize_csv(self):
        """Create the CSV file with headers if it hasn't been initialized yet."""
        if self.csv_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.csv_file = os.path.join(self.base_path, f"FAQ_Report_{timestamp}.csv")
            with open(self.csv_file, 'w', newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)

    def log_result(self, session_id, faq, expected, actual, sim, pass_fail, hallucination, coverage,
                   link_comparison, link_validity, fact_check):
        """Logs a result to the CSV file, initializing the file if needed."""
        self._initialize_csv()
        row = [session_id, faq, expected, actual, sim, pass_fail, hallucination, coverage,
               str(link_comparison), str(link_validity), fact_check]
        with open(self.csv_file, 'a', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

