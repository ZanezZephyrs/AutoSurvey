
from .base import Searcher
import requests
class SemanticScholarSearcher(Searcher):
    def __init__(self) -> None:
        self.base_url="http://api.semanticscholar.org/graph/v1/paper/search"

    def search(self, request_data: dict, filters=None):
        # consult https://api.semanticscholar.org/api-docs/#tag/Paper-Data/operation/post_graph_get_papers for options
        if "query" not in request_data:
            raise ValueError("Semantic Scholar requires a query to search")
        
        current_try=0
        max_tries=3
        while current_try<max_tries:
            try:
                response=requests.get(self.base_url, params=request_data)
                if response.ok:
                    break 
                else:
                    current_try+=1
                    response.raise_for_status()

            except requests.HTTPError as e:
                
                continue
            

        data=response.json()["data"]
        if filters:
            for desired_filter in filters:
                data=list(filter(desired_filter.filter_sm, data))
        return data
