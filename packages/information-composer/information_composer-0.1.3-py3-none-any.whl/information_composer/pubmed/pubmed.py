import asyncio
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Union

import aiohttp
from Bio import Entrez, Medline
import pandas as pd
from tqdm import tqdm


def query_pmid_by_date(
    query: str,
    email: str = "your_email@example.com",
    start_date: str = None,
    end_date: str = None,
    batch_months: int = 12,
) -> List[str]:
    """
    Query PubMed database with date ranges to get all unique PMIDs matching the search query.

    Args:
        query (str): PubMed search query string
        email (str): Email address for NCBI's tracking purposes
        start_date (str): Start date in format 'YYYY/MM/DD' (defaults to earliest possible)
        end_date (str): End date in format 'YYYY/MM/DD' (defaults to today)
        batch_months (int): Number of months per batch (default 12)

    Returns:
        List[str]: List of unique PMIDs matching the query
    """
    Entrez.email = email

    # Set default dates if not provided
    if end_date is None:
        end_date = datetime.today().strftime("%Y/%m/%d")
    if start_date is None:
        start_date = "1800/01/01"  # PubMed's earliest date

    # Convert dates to datetime objects
    start_dt = datetime.strptime(start_date, "%Y/%m/%d")
    end_dt = datetime.strptime(end_date, "%Y/%m/%d")

    all_pmids = set()

    # Calculate total number of batches for progress bar
    total_months = (end_dt.year - start_dt.year) * 12 + end_dt.month - start_dt.month
    total_batches = (total_months + batch_months - 1) // batch_months

    # Process in batches with progress bar
    with tqdm(total=total_batches, desc="Querying PubMed") as pbar:
        current_start = start_dt
        while current_start <= end_dt:
            # Calculate end of current batch
            current_end = min(current_start + timedelta(days=batch_months * 30), end_dt)

            # Format dates for query
            date_query = (
                f"{query} AND ({current_start.strftime('%Y/%m/%d')}[DP] : "
                f"{current_end.strftime('%Y/%m/%d')}[DP])"
            )

            try:
                with Entrez.esearch(
                    db="pubmed", term=date_query, retmax=9999
                ) as search_handle:
                    record = Entrez.read(search_handle)
                    batch_pmids = record["IdList"]
                    all_pmids.update(batch_pmids)

                    # If we got less than 9999 results, we don't need to worry about missing any
                    if len(batch_pmids) < 9999:
                        current_start = current_end + timedelta(days=1)
                        pbar.update(1)
                    else:
                        # If we hit the limit, use smaller time intervals
                        new_batch_months = max(1, batch_months // 2)
                        if new_batch_months == batch_months:
                            raise RuntimeError(
                                f"Too many results even with minimum batch size for period "
                                f"{current_start.strftime('%Y/%m/%d')} to {current_end.strftime('%Y/%m/%d')}"
                            )
                        batch_months = new_batch_months
                        # Recalculate total batches with new batch_months
                        total_batches = (
                            total_months + batch_months - 1
                        ) // batch_months
                        pbar.reset(total=total_batches)
                        continue

            except Exception as e:
                raise RuntimeError(f"Error querying PubMed: {e!s}")

    return list(all_pmids)


def query_pmid(
    query: str, email: str = "your_email@example.com", retmax: int = 9999
) -> list:
    """
    Query PubMed database and return a list of PMIDs matching the search query.

    Args:
        query (str): PubMed search query string
        email (str): Email address for NCBI's tracking purposes
        retmax (int): Maximum number of results to return

    Returns:
        list: List of PMIDs matching the query
    """
    Entrez.email = email
    try:
        with Entrez.esearch(db="pubmed", term=query, retmax=retmax) as search_handle:
            record = Entrez.read(search_handle)
            return record["IdList"]
    except Exception as e:
        raise RuntimeError(f"Error querying PubMed: {e!s}")


def load_pubmed_file(filename: str, *args, **kwargs) -> Union[pd.DataFrame, dict, list]:
    """
    Load and parse PubMed Medline file.

    Args:
        filename (str): Path to Medline format file
        **kwargs: Optional parameters
            - output_type (str): Output format ('pd', 'dict', 'list')

    Returns:
        Union[pd.DataFrame, dict, list]: Parsed data in specified format
    """
    output_type = kwargs.get("output_type", "list")
    if output_type not in ["list", "dict", "pd"]:
        raise ValueError('output_type must be "pd", "list" or "dict"')

    records_dict = {}
    try:
        with open(filename) as handle:
            for record in Medline.parse(handle):
                pmid = record["PMID"]
                records_dict[pmid] = {
                    "pmid": pmid,
                    "title": record.get("TI", "N/A"),
                    "abstract": record.get("AB", "No abstract available"),
                    "journal": record.get("JT", "N/A"),
                    "pubdate": record.get("DP", "N/A"),
                    "publication_types": record.get("PT", []),
                    "authors": record.get("AU", []),
                    "doi": record.get("LID", "N/A"),
                    "keywords": record.get("MH", []),
                }
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {filename} does not exist")
    except Exception as e:
        raise RuntimeError(f"Error parsing file {filename}: {e!s}")

    if output_type == "pd":
        return pd.DataFrame.from_dict(records_dict).T
    elif output_type == "dict":
        return records_dict
    return list(records_dict.values())


async def _fetch_pmids_chunk(
    pmids: List[str], email: str, session: aiohttp.ClientSession
) -> List[Dict]:
    """
    Helper function to fetch a chunk of PMIDs asynchronously.
    """
    Entrez.email = email
    try:
        with Entrez.efetch(
            db="pubmed", id=pmids, rettype="medline", retmode="text"
        ) as handle:
            records = list(Medline.parse(handle))
            return [_process_record(record) for record in records]
    except Exception as e:
        print(f"Error fetching chunk {pmids[:5]}...: {e!s}")
        return []


def _clean_doi(doi: str) -> str:
    """
    Clean and standardize DOI format by extracting the actual DOI from various formats.

    Args:
        doi (str): Raw DOI string

    Returns:
        str: Cleaned DOI string

    Examples:
        >>> _clean_doi("10.26508/lsa.202302380 [doi] e202302380")
        "10.26508/lsa.202302380"
        >>> _clean_doi("S1534-5807(24)00603-8 [pii] 10.1016/j.devcel.2024.10.004 [doi]")
        "10.1016/j.devcel.2024.10.004"
    """
    if not doi or doi == "N/A":
        return "N/A"

    # Regular expression to find DOI patterns
    doi_pattern = r"(10\.\d{4,}(?:\.[1-9][0-9]*)*(?:\/|%2F)(?:(?![\"&\'])\S)+)"

    # Find all matches
    matches = re.findall(doi_pattern, doi)

    if matches:
        # Return the first valid DOI found
        return matches[0].strip()

    return "N/A"


def _process_record(record: Dict) -> Dict:
    """
    Helper function to process a single record.
    """
    processed_record = {
        # Basic Information
        "pmid": record.get("PMID", "N/A"),
        "title": record.get("TI", "N/A"),
        "abstract": record.get("AB", "No abstract available"),
        # Journal Information
        "journal": record.get("JT", "N/A"),
        "journal_abbreviation": record.get("TA", "N/A"),
        "journal_iso": record.get("IS", "N/A"),
        "volume": record.get("VI", "N/A"),
        "issue": record.get("IP", "N/A"),
        "pagination": record.get("PG", "N/A"),
        # Dates
        "pubdate": record.get("DP", "N/A"),
        "create_date": record.get("DA", "N/A"),
        "complete_date": record.get("LR", "N/A"),
        "revision_date": record.get("DEP", "N/A"),
        # Publication Details
        "publication_types": record.get("PT", []),
        "publication_status": record.get("PST", "N/A"),
        "language": record.get("LA", ["N/A"])[0],
        # Authors and Affiliations
        "authors": record.get("AU", []),
        "authors_full": record.get("FAU", []),
        "affiliations": record.get("AD", []),
        # Identifiers
        "doi": _clean_doi(
            record.get("LID", record.get("AID", ["N/A"])[0])
        ),  # Try LID first, then AID
        "pmcid": record.get("PMC", "N/A"),
        "article_id": record.get("AID", []),
        # Subject Terms
        "mesh_terms": record.get("MH", []),
        "mesh_qualifiers": record.get("SH", []),
        "keywords": record.get("OT", []),
        "chemicals": record.get("RN", []),
        "chemical_names": record.get("NM", []),
        # Grant Information
        "grants": record.get("GR", []),
        "grant_agencies": record.get("GS", []),
        # Additional Information
        "comments_corrections": record.get("CIN", []),
        "publication_country": record.get("PL", "N/A"),
        "article_type": record.get("PT", []),
        "citation_subset": record.get("SB", []),
    }

    return processed_record


async def fetch_pubmed_details_batch(
    pmids: List[str],
    email: str = "your_email@example.com",
    cache_dir: Optional[str] = None,
    chunk_size: int = 100,
    delay_between_chunks: float = 1.0,
    max_retries: int = 3,
) -> List[Dict[str, Any]]:
    """
    Fetch detailed information from PubMed for a large list of PMIDs with caching and retry support.
    """
    if cache_dir:
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

    # Initialize results storage
    results = {}
    pmids_to_fetch = set()

    # Check cache for existing results with progress bar
    if cache_dir:
        print("Checking cache...")
        for pmid in tqdm(pmids, desc="Reading cache"):
            cache_file = cache_dir / f"{pmid}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, encoding="utf-8") as f:
                        results[pmid] = json.load(f)
                except Exception as e:
                    print(f"\nError reading cache for {pmid}: {e}")
                    pmids_to_fetch.add(pmid)
            else:
                pmids_to_fetch.add(pmid)
    else:
        pmids_to_fetch = set(pmids)

    # Process uncached PMIDs in chunks
    if pmids_to_fetch:
        pmids_list = list(pmids_to_fetch)
        chunks = [
            pmids_list[i : i + chunk_size]
            for i in range(0, len(pmids_list), chunk_size)
        ]

        print(
            f"\nFetching {len(pmids_to_fetch)} uncached PMIDs in {len(chunks)} chunks..."
        )
        async with aiohttp.ClientSession() as session:
            with tqdm(total=len(pmids_to_fetch), desc="Downloading") as pbar:
                for chunk in chunks:
                    retry_count = 0
                    while retry_count < max_retries:
                        try:
                            chunk_results = await _fetch_pmids_chunk(
                                chunk, email, session
                            )

                            # Store results and update cache
                            for record in chunk_results:
                                pmid = record["pmid"]
                                results[pmid] = record

                                if cache_dir:
                                    cache_file = cache_dir / f"{pmid}.json"
                                    with open(cache_file, "w", encoding="utf-8") as f:
                                        json.dump(
                                            record, f, ensure_ascii=False, indent=2
                                        )

                            # Update progress bar
                            pbar.update(len(chunk_results))

                            # Success - break retry loop
                            break

                        except Exception as e:
                            retry_count += 1
                            print(
                                f"\nError processing chunk (attempt {retry_count}/{max_retries}): {e}"
                            )
                            if retry_count == max_retries:
                                print(
                                    f"\nFailed to process chunk after {max_retries} attempts: {chunk}"
                                )
                                # Update progress bar even for failed chunks
                                pbar.update(len(chunk))
                            else:
                                await asyncio.sleep(delay_between_chunks * retry_count)

                    # Delay between chunks to avoid overwhelming the API
                    await asyncio.sleep(delay_between_chunks)

    # Return results in the same order as input PMIDs
    return [
        results.get(pmid, {"pmid": pmid, "error": "Failed to fetch"}) for pmid in pmids
    ]


def fetch_pubmed_details_batch_sync(*args, **kwargs) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for fetch_pubmed_details_batch
    """
    return asyncio.run(fetch_pubmed_details_batch(*args, **kwargs))


def clean_pubmed_cache(
    cache_dir: Union[str, Path], older_than_days: Optional[int] = None
) -> int:
    """
    Clean the PubMed cache directory.

    Args:
        cache_dir (Union[str, Path]): Path to the cache directory
        older_than_days (Optional[int]): If provided, only delete files older than this many days

    Returns:
        int: Number of files deleted
    """
    cache_dir = Path(cache_dir)
    if not cache_dir.exists():
        return 0

    deleted_count = 0
    current_time = time.time()

    try:
        with tqdm(list(cache_dir.glob("*.json")), desc="Cleaning cache") as pbar:
            for cache_file in pbar:
                should_delete = True
                if older_than_days is not None:
                    file_age = current_time - cache_file.stat().st_mtime
                    should_delete = file_age > (older_than_days * 24 * 3600)

                if should_delete:
                    cache_file.unlink()
                    deleted_count += 1
                    pbar.set_postfix(deleted=deleted_count)

        # Remove the directory if it's empty
        if not any(cache_dir.iterdir()):
            cache_dir.rmdir()

        return deleted_count

    except Exception as e:
        raise RuntimeError(f"Error cleaning cache directory: {e!s}")
