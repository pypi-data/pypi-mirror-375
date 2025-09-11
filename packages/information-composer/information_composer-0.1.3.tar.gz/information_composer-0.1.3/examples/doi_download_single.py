import csv
import os
from typing import Dict, List

from information_composer.core.doi_downloader import DOIDownloader


def save_results_to_csv(results: List[Dict], output_file: str) -> None:
    """
    Save download results to a CSV file.

    Args:
        results (List[Dict]): List of dictionaries containing download results
        output_file (str): Path to the output CSV file
    """
    if not results:  # Check if results is empty
        print("No results to save")
        return

    try:
        fieldnames = ["DOI", "file_name", "downloaded"]
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Results saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results to CSV: {str(e)}")


def main():
    # Configuration
    base_dir = os.path.join(os.getcwd(), "downloads")
    email = "your_email@example.com"  # Replace with your email

    # Initialize downloader
    downloader = DOIDownloader(email=email)

    try:
        # Single DOI example
        print("Starting single DOI download example...")
        print("-" * 50)
        single_doi = "10.1093/jxb/erad499"
        single_output_dir = os.path.join(base_dir, "single")
        single_result = downloader.download_single(
            doi=single_doi, output_dir=single_output_dir
        )

        # Save single result to CSV
        if single_result:  # Check if we have a result
            single_csv_path = os.path.join(base_dir, "single_download_results.csv")
            save_results_to_csv([single_result], single_csv_path)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
