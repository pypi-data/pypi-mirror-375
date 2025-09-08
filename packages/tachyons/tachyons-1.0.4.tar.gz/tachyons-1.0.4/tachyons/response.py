# -*- coding: utf-8 -*-
"""
<license>
  * Copyright (C) 2024-2025 Abdelmathin Habachi, contact@abdelmathin.com.
  *
  * https://abdelmathin.com
  * https://github.com/Abdelmathin/tachyons
  *
  * Permission is hereby granted, free of charge, to any person obtaining
  * a copy of this software and associated documentation files (the
  * "Software"), to deal in the Software without restriction, including
  * without limitation the rights to use, copy, modify, merge, publish,
  * distribute, sublicense, and/or sell copies of the Software, and to
  * permit persons to whom the Software is furnished to do so, subject to
  * the following conditions:
  *
  * The above copyright notice and this permission notice shall be
  * included in all copies or substantial portions of the Software.
  *
  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
  * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
  * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
  * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  *
  * File   : tachyons/response.py
  * Created: 2025/08/30 22:47:59 GMT+1
  * Updated: 2025/09/05 00:00:13 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import datetime
from tachyons.settings    import TachyonsSettings
from tachyons.serializers import JsonSerializer

def HtmlResponse(content, status = 200, cookies: dict = None, *args, **kwargs):
	"""
	"""
	raise NotImplementedError("HtmlResponse is not implemented yet. Please use the appropriate engine's response class directly.")	

def JsonResponse(
		data         : dict        ,
		status       : int  = 200  ,
		cookies      : dict = None ,
		basic_fields : list[str] = ["status", "timestamp", "message", "success", "error"],
		*args,
		**kwargs
	):
	"""
	Returns a JSON response using the tachyons's default engine.
	Args:
		data (dict): The JSON object to return.
		status (int): The HTTP status code for the response.
	Returns:
		Response object compatible with the tachyons's engine.
	"""
	if basic_fields:
		"""
		Ensures that the JSON response contains the basic fields:
		- success: A boolean indicating the success of the operation.
		- status: The HTTP status code.
		- timestamp: The current UTC timestamp in ISO 8601 format.
		- message: A human-readable message (can be customized later).
		- error: None (can be customized later).
		"""
		if ("status" in basic_fields):
			_status = int(str(data.get("status", status)), 10)
			if _status != status:
				raise ValueError(f"Status code in the JSON object does not match the provided status code: {_status} != {status}")
			data["status"] = _status
		if ("timestamp" in basic_fields):
			data["timestamp"] = str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
		if ("success" in basic_fields):
			if not ("success" in data):
				data["success"] = (status >= 200) and (status < 300)
			data["success"] = not not data["success"]
		if ("message" in basic_fields):
			if not ("message" in data):
				data["message"] = "OK" if (status >= 200) and (status < 300) else "Error"
		if ("error" in basic_fields):
			if not ("error" in data):
				data["error"] = None

	data: dict = JsonSerializer.serialize(data.copy())

	engine = TachyonsSettings.get_base_engine()
	if engine == "flask":
		import flask
		return flask.jsonify(data), status
	elif engine == "fastapi":
		from fastapi.responses import JSONResponse as fastAPIJsonResponse
		rsp = fastAPIJsonResponse(
			content     = data,
			status_code = status
		)
		if cookies:
			for key, cookie in cookies.items():
				cookie = cookie.copy()
				cookie["key"] = key
				rsp.set_cookie(**cookie)
		return rsp
	elif engine == "django":
		"""
		Django's JsonResponse class automatically sets the Content-Type to application/json
		and serializes the data to JSON format.
		"""
		from django.http import JsonResponse as DjangoJsonResponse
		rsp = DjangoJsonResponse(
			data   = data,
			status = status
		)
		if cookies:
			for key, cookie in cookies.items():
				cookie = cookie.copy()
				cookie["key"] = key
				rsp.set_cookie(**cookie)
		return rsp
	raise ValueError("Unsupported tachyons base engine: {}".format(engine))

def Json400Response(message: str = "Bad Request"):
	"""
	Returns a standardized JSON response for HTTP 400 Bad Request errors.
	Args:
		message (str): Custom error message. Default is "Bad Request".
	Returns:
		Response object compatible with the tachyons's engine.
	"""
	return JsonResponse(
		{
			"success": False,
			"status" : 400,
			"message": message,
			"error"  : message,
		},
		status = 400,
		basic_fields = ["status", "timestamp", "message", "success", "error"]
	)

def Json403Response(message: str = "Forbidden"):
	"""
	Returns a standardized JSON response for HTTP 403 Forbidden errors.
	Args:
		message (str): Custom error message. Default is "Forbidden".
	Returns:
		Response object compatible with the tachyons's engine.
	"""
	return JsonResponse(
		{
			"success": False,
			"status" : 403,
			"message": message,
			"error"  : message,
		},
		status = 403,
		basic_fields = ["status", "timestamp", "message", "success", "error"]
	)

def Json404Response(message: str = "Not Found"):
	"""
	Returns a standardized JSON response for HTTP 404 Not Found errors.
	Args:
		message (str): Custom error message. Default is "Not Found".
	Returns:
		Response object compatible with the tachyons's engine.
	"""
	return JsonResponse(
		{
			"success": False,
			"status" : 404,
			"message": message,
			"error"  : message,
		},
		status = 404,
		basic_fields = ["status", "timestamp", "message", "success", "error"]
	)

def Json500Response(message: str = "Internal Server Error"):
	"""
	Returns a standardized JSON response for HTTP 500 Internal Server Error errors.
	Args:
		message (str): Custom error message. Default is "Internal Server Error".
	Returns:
		Response object compatible with the tachyons's engine.
	"""
	return JsonResponse(
		{
			"success": False,
			"status" : 500,
			"message": message,
			"error"  : message,
		},
		status = 500,
		basic_fields = ["status", "timestamp", "message", "success", "error"]
	)
