"""
DOI Downloader module for downloading academic papers using DOI.
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Union

from habanero import Crossref
import requests
from tqdm import tqdm


class DOIDownloader:
    """A class to download academic papers using their DOI."""

    def __init__(self, email: str = None):
        """
        Initialize DOIDownloader.

        Args:
            email (str, optional): Email for Crossref API. Providing an email improves service.
        """
        self.cr = Crossref(mailto=email if email else "anonymous@example.com")
        self.headers = {
            "User-Agent": "information-composer/1.0 (https://github.com/yourusername/information-composer)"
        }

    def get_pdf_url(self, doi: str) -> Optional[str]:
        """
        Get PDF URL from DOI using Crossref.

        Args:
            doi (str): The DOI of the paper.

        Returns:
            Optional[str]: The URL of the PDF if found, None otherwise.
        """
        try:
            work = self.cr.works(ids=doi)

            if "message" in work:
                if "link" in work["message"]:
                    for link in work["message"]["link"]:
                        if (
                            "content-type" in link
                            and "pdf" in link["content-type"].lower()
                        ):
                            return link["URL"]

                if "URL" in work["message"]:
                    return work["message"]["URL"]

            return None
        except Exception as e:
            print(f"Error getting PDF URL: {e!s}")
            return None

    def download_pdf(self, url: str, output_path: str) -> bool:
        """
        Download PDF from URL.

        Args:
            url (str): The URL of the PDF.
            output_path (str): Path where the PDF should be saved.

        Returns:
            bool: True if download was successful, False otherwise.
        """
        try:
            response = requests.get(url, headers=self.headers, stream=True)

            # Check for various status codes
            if response.status_code == 401 or response.status_code == 403:
                print("Access denied: This paper requires subscription or payment")
                return False
            elif response.status_code == 404:
                print("PDF not found: The URL is no longer valid")
                return False
            elif response.status_code != 200:
                print(f"Failed to download: HTTP status code {response.status_code}")
                return False

            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if "application/pdf" in content_type:
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
            elif "text/html" in content_type:
                print("Access restricted: Redirected to login or payment page")
                return False
            else:
                print(f"Unexpected content type: {content_type}")
                return False

        except requests.exceptions.SSLError:
            print("SSL Error: Could not establish secure connection")
            return False
        except requests.exceptions.ConnectionError:
            print("Connection Error: Could not connect to the server")
            return False
        except Exception as e:
            print(f"Error downloading PDF: {e!s}")
            return False

    def download_by_doi(self, doi: str, output_dir: str = "downloads") -> Optional[str]:
        """
        Download PDF by DOI.

        Args:
            doi (str): The DOI of the paper.
            output_dir (str, optional): Directory where PDFs should be saved. Defaults to "downloads".

        Returns:
            Optional[str]: Path to the downloaded PDF if successful, None otherwise.
        """
        os.makedirs(output_dir, exist_ok=True)
        doi = doi.strip()
        output_path = os.path.join(output_dir, f"{doi.replace('/', '_')}.pdf")

        print(f"Processing DOI: {doi}")
        pdf_url = self.get_pdf_url(doi)

        if pdf_url:
            print(f"Found PDF URL: {pdf_url}")
            if self.download_pdf(pdf_url, output_path):
                print(f"Successfully downloaded PDF to: {output_path}")
                return output_path
            else:
                print("Failed to download PDF")
                return None
        else:
            print("Could not find PDF URL")
            return None

    def download_single(
        self, doi: str, output_dir: str, file_name: Optional[str] = None
    ) -> Dict:
        """
        Download a single paper by DOI with detailed output.

        Args:
            doi (str): The DOI of the paper to download
            output_dir (str): Directory to save the downloaded paper
            file_name (Optional[str], optional): Custom filename for the PDF.
                If None, uses DOI as filename. Defaults to None.

        Returns:
            Dict: Download result containing DOI, file_name, and download status
        """
        os.makedirs(output_dir, exist_ok=True)

        # If custom filename is provided, use it; otherwise use DOI
        if file_name:
            # Ensure filename ends with .pdf
            if not file_name.lower().endswith(".pdf"):
                file_name += ".pdf"
            output_path = os.path.join(output_dir, file_name)
            # Use custom output path for download
            result = self.download_by_doi(doi, output_dir=os.path.dirname(output_path))
            if result:  # If download successful, rename the file
                os.rename(result, output_path)
                result = output_path
        else:
            result = self.download_by_doi(doi, output_dir=output_dir)

        # Prepare result dictionary
        download_result = {
            "DOI": doi,
            "file_name": result if result else "",
            "downloaded": bool(result),
        }

        # Print status
        if result:
            print(f"Successfully downloaded to: {result}")
            print(f"File size: {os.path.getsize(result) / 1024:.2f} KB")
        else:
            print("Download failed")

        return download_result

    def download_batch(
        self, dois: List[str], output_dir: str, delay: int = 2
    ) -> List[Dict]:
        """
        Download multiple papers by their DOIs with detailed output.

        Args:
            dois (List[str]): List of DOIs to download
            output_dir (str): Directory to save the downloaded papers
            delay (int, optional): Delay between downloads in seconds. Defaults to 2

        Returns:
            List[Dict]: List of download results, each containing DOI, file_name, and download status
        """
        os.makedirs(output_dir, exist_ok=True)
        download_results = []  # List to store results for CSV
        status = []  # Track detailed status for each DOI

        for doi in tqdm(dois, desc="Downloading papers", unit="paper"):
            result = self.download_by_doi(doi, output_dir)

            # Prepare result dictionary for CSV
            download_result = {
                "DOI": doi,
                "file_name": result if result else "",
                "downloaded": bool(result),
            }
            download_results.append(download_result)

            # Store status information for display
            if not result:
                response = requests.get(
                    f"https://doi.org/{doi}", headers=self.headers, allow_redirects=True
                )
                if response.status_code in (401, 403):
                    status.append((doi, "Subscription required"))
                elif response.status_code == 404:
                    status.append((doi, "DOI not found"))
                else:
                    status.append((doi, "Access restricted"))
            else:
                status.append((doi, "Success"))

            time.sleep(delay)

        # Print results with improved status information
        print("\nDownload Results:")
        print("-" * 50)
        for result, (_, status_msg) in zip(download_results, status):
            if result["downloaded"]:
                file_size = os.path.getsize(result["file_name"]) / 1024  # Convert to KB
                print(f"✓ {result['DOI']}")
                print(f"  └─ Saved to: {result['file_name']}")
                print(f"  └─ Size: {file_size:.2f} KB")
            else:
                print(f"✗ {result['DOI']}")
                print(f"  └─ Status: {status_msg}")
            print("-" * 50)

        # Print summary with categories
        success_count = sum(1 for r in download_results if r["downloaded"])
        subscription_count = sum(
            1 for _, msg in status if msg == "Subscription required"
        )
        not_found_count = sum(1 for _, msg in status if msg == "DOI not found")
        restricted_count = sum(1 for _, msg in status if msg == "Access restricted")

        print("\nDownload Summary:")
        print(f"Total papers: {len(dois)}")
        print(f"Successfully downloaded: {success_count}")
        if subscription_count > 0:
            print(f"Subscription required: {subscription_count}")
        if not_found_count > 0:
            print(f"DOI not found: {not_found_count}")
        if restricted_count > 0:
            print(f"Access restricted: {restricted_count}")

        return download_results
