from milvus_wrapper import MilvusAPI

def test_text_search():
    milvus = MilvusAPI(collection_name="movies")
    
    # Test cases
    test_queries = [
        {
            "name": "Basic Search",
            "query": "action",
            "filters": None
        },
        {
            "name": "Search with Rating Filter",
            "query": "adventure",
            "filters": {"rating": "PG-13"}
        },
        {
            "name": "Search with Genre Filter",
            "query": "drama",
            "filters": {"genres": "Drama"}
        },
        {
            "name": "Combined Search",
            "query": "star",
            "filters": {
                "rating": "PG-13",
                "genres": "Science Fiction"
            }
        }
    ]
    
    for test in test_queries:
        print(f"\n=== {test['name']} ===")
        results = milvus.text_search(
            query=test["query"],
            filters=test["filters"],
            limit=5,
            output_fields=["title", "rating", "genres"]
        )
        
        for result in results:
            print(f"\nTitle: {result['title']}")
            print(f"Rating: {result['rating']}")
            print(f"Genres: {result['genres']}")
            print("-" * 50)

if __name__ == "__main__":
    test_text_search()
