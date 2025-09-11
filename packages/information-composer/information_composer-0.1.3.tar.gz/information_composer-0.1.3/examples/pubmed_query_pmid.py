from information_composer.pubmed.pubmed import query_pmid_by_date


def query_demo():
    """
    Example function demonstrating how to query PubMed for cis-regulatory elements
    using different date ranges and search parameters.
    """
    # Example 1: Get all related papers from the past 5 years
    recent_pmids = query_pmid_by_date(
        query="cis-regulatory elements",
        email="your_email@example.com",
        start_date="2019/01/01",
        batch_months=6,  # Use 6-month intervals
    )

    print("=== Recent Publications (2019-present) ===")
    print(f"Number of publications found: {len(recent_pmids)}")
    print(f"First 5 PMIDs: {recent_pmids[:5]}\n")

    # Example 2: Get papers from a specific date range with more precise search
    historical_pmids = query_pmid_by_date(
        query="rice[Title/Abstract]",  # More precise search
        email="your_email@example.com",
        batch_months=12,
    )

    print("=== Historical Publications ===")
    print(f"Number of publications found: {len(historical_pmids)}")
    print(f"First 5 PMIDs: {historical_pmids[:5]}")


if __name__ == "__main__":
    query_demo()
