import json
from pprint import pprint

from information_composer.pubmed.pubmed import fetch_pubmed_details


def main():
    # Example PMIDs
    pmids = ["39659015", "24191062", "26400163"]

    # Fetch details for the PMIDs
    # Replace with your email address
    results = fetch_pubmed_details(pmids, email="your_email@example.com")

    print(f"Retrieved details for {len(results)} articles:\n")

    # Display key information for each article
    for article in results:
        print("=" * 80)
        print(f"PMID: {article['pmid']}")
        print(f"Title: {article['title']}")
        print(f"Journal: {article['journal']} ({article['pubdate']})")
        print(f"Authors: {', '.join(article['authors'])}")
        print(f"DOI: {article['doi']}")
        print("\nPublication Types:")
        for pub_type in article["publication_types"]:
            print(f"- {pub_type}")
        print("\nMeSH Terms:")
        for term in article["mesh_terms"]:
            print(f"- {term}")
        print("\nAbstract:")
        print(
            article["abstract"][:300] + "..."
            if len(article["abstract"]) > 300
            else article["abstract"]
        )
        print("\n")

    # Save the full results to a JSON file for reference
    with open("pubmed_details_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Full results have been saved to 'pubmed_details_output.json'")


if __name__ == "__main__":
    main()
