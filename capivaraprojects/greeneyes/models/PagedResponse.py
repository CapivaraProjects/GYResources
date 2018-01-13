class PagedReponse:
    def __init__(self, status_code=0, message="", elapsed_ms="", response="" , total=0, offset="", page_size=0):
        self.status_code = status_code
        self.message = message
        self.elapsed_ms = elapsed_ms
        self.response = response
        self.total = total
        self.offset = offset
        self.page_size = page_size
