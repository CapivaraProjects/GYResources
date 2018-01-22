class PagedReponse {
	constructor(self, status_code=0, message="", elapsed_ms=0.0, response=Object() , total=0, offset="", page_size=0) {
		this.self = self;
		this.status_code = status_code;
		this.message = message;
		this.elapsed_ms = elapsed_ms;
		this.response = response;
		this.total = total;
		this.offset = offset;
		this.page_size = page_size;
	}
}