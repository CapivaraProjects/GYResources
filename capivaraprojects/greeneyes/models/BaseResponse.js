class BaseResponse {
	constructor(status_code = 0, message = "", elapsed_ms = 0.0, response = Object()) {
		this.status_code = status_code;
		this.message = message;
		this.elapsed_ms = elapsed_ms;
		this.response = response;
	}
}