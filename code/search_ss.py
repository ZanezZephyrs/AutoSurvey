


from searchers.semantic_scholar import SemanticScholarSearcher
from filters.field_in_list_filter import FieldInListFilter
from filters.field_numeric_filter import FieldNumericFilter
import json

searcher=SemanticScholarSearcher()

# search for papers with "deep learning" in the title
params={
    "query": "deep learning",
    "limit": 100, # max 100
    "fields": "title,authors,citationCount,year,tldr,url"
}

# compose as many filters as you like, they are applied in sequence
filters=[
    FieldNumericFilter("citationCount", lower_bound=0), # at least 10 citations
    FieldNumericFilter("authors", lower_bound=2), # at least 2  authors
    FieldNumericFilter("year", lower_bound=2020, upper_bound=2023), # between 2020 and 2023
]

results=searcher.search(params, filters=filters)



print(len(results))
print(json.dumps(results[0],indent=4))