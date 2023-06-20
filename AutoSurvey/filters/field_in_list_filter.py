from .base import Filter

class FieldInListFilter(Filter):
    def __init__(self, field: str, allowed_options, strict=True) -> None:
        self.field=field
        self.allowed_options=allowed_options
        self.strict=strict
        pass

    def filter_sm(self, doc: str):
        if self.field not in doc or not doc[self.field]:
            return False
        
        if isinstance(doc[self.field], list):
            at_least_one_match=False
            all_match=True
            for option in doc[self.field]:

                if option in self.allowed_options:
                    at_least_one_match=True
                else:
                    all_match=False
            
            if self.strict:
                return all_match
            else:
                return at_least_one_match
        
        else:
            # Check if one of the dict keys is in the allowed options
            keys = list(doc[self.field].keys())
            if self.strict:
                # all items in allowed options are in keys
                return all([key in keys for key in self.allowed_options])
            else:
                return any([key in keys for key in self.allowed_options])

