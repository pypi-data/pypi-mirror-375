

if __name__ == "__main__":
	_match_query_parameters(
		"http://127.0.0.1:8000/{?api?}/{v1}/<?auth::?::::?>/users/read?al&uid=<int:uid>&name=<str:name>&=5#?????",
		"http://127.0.0.1:8000/api/v1/auth/users/read?uid=me#?????"
	)
