import json
from pathlib import Path
import time

from tqdm import tqdm

from information_composer.pubmed.pubmed import (
    clean_pubmed_cache,
    fetch_pubmed_details_batch_sync,
    query_pmid_by_date,
)


def main(query: str, output_file: str, pmid_file: str):
    # Create cache directory
    cache_dir = Path("pubmed_cache")

    try:
        # Query PMIDs with progress information
        print(f"Querying PubMed for publications about {query} ...")
        start_time = time.time()

        pmids = query_pmid_by_date(
            query=query,
            email="your_email@example.com",
            # start_date="2024/01/01",
            batch_months=36,  # Use 36-month intervals
        )

        query_time = time.time() - start_time
        print(f"Found {len(pmids)} publications in {query_time:.2f} seconds\n")

        # Save PMIDs to file
        print(f"Saving PMIDs to {pmid_file}...")
        with open(pmid_file, "w") as f:
            f.write("\n".join(map(str, pmids)))
        print(f"Saved {len(pmids)} PMIDs to file")

        # Fetch details with caching enabled
        print("Fetching detailed information for each publication...")
        start_time = time.time()

        results = fetch_pubmed_details_batch_sync(
            pmids=pmids,
            email="your_email@example.com",
            cache_dir=cache_dir,
            chunk_size=100,  # Increased chunk size for better performance
            delay_between_chunks=1.0,
        )

        fetch_time = time.time() - start_time
        print(
            f"\nFetched details for {len(results)} articles in {fetch_time:.2f} seconds"
        )

        # Save complete results
        print("\nSaving results to file...")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Full results have been saved to {output_file}")

        # Display summary of results
        print("\nGenerating summary...")
        for article in tqdm(results, desc="Processing results"):
            if "error" in article:
                continue
            print("=" * 80)
            print(f"PMID: {article['pmid']}")
            print(f"Title: {article['title']}")
            print(f"Journal: {article['journal']} ({article.get('pubdate', 'N/A')})")
            print(f"Authors: {', '.join(article.get('authors', []))}")
            print("\n")

    finally:
        # Clean up cache after processing
        print("\nCleaning up cache...")
        deleted_count = clean_pubmed_cache(cache_dir)
        print(f"Cleaned up {deleted_count} cache files")


if __name__ == "__main__":
    # main(query="cis-regulatory elements", output_file="pubmed_batch_results.json")
    main(
        query="cis-regulatory elements",
        output_file="./data/CRM_pubmed_batch_results.json",
        pmid_file="./data/CRM_pmids.txt",
    )
