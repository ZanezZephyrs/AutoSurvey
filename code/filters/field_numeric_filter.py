
from filters.base import Filter

class FieldNumericFilter(Filter):
    def __init__(self, field: str, lower_bound=0, upper_bound=1000000) -> None:
        self.field=field
        self.lower_bound=lower_bound
        self.upper_bound=upper_bound
        pass

    def filter_sm(self, doc: str):
        if self.field not in doc or not doc[self.field]:
            return False
        
        if isinstance(doc[self.field], list):
            return self.lower_bound <= len(doc[self.field]) <= self.upper_bound
        
        else:
            return self.lower_bound <= int(doc[self.field]) <= self.upper_bound
        
        
