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
  * File   : tachyons/request.py
  * Created: 2025/08/30 22:47:41 GMT+1
  * Updated: 2025/09/01 09:38:04 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import json
from typing import Any, Union, _tp_cache
# from typing import Generic, TypeVar, Optional

"""
	__tachyons_typename__: A special attribute used to identify the type in Tachyon's type system.
	__jserialize__       : A special attribute used to serialize the object to JSON.
"""

class RequestSpecialForm:
    __slots__ = ('__name__', '__doc__', '_handler')
    def __init__(self, handler):
        self._handler = handler
        self.__name__ = handler.__name__
        self.__doc__  = handler.__doc__

    def __getattr__(self, item):
        if item in {'__name__', '__qualname__'}:
            return self.__name__

        raise AttributeError(item)

    def __repr__(self):
        return self.__name__

    def __reduce__(self):
        return self.__name__

    def __call__(self, *args, **kwds):
        return self._handler(*args, **kwds)

    def __or__(self, other):
        return Union[self, other]

    def __ror__(self, other):
        return Union[other, self]

    def __instancecheck__(self, obj):
        raise TypeError(f"{self} cannot be used with isinstance()")

    def __subclasscheck__(self, cls):
        raise TypeError(f"{self} cannot be used with issubclass()")

    @_tp_cache
    def __getitem__(self, parameters):
        if isinstance(parameters, tuple):
            return self._handler(*parameters)
        return self._handler(parameters)

class BaseRequestType:
	"""
	Base class for request types.
	Provides common functionality for request type classes.
	"""
	def __jserialize__(self):
		return self.__str__()

class DjangoRequest(BaseRequestType):
	"""
	A class to represent a Django HTTP request object.
	It is used to type hint Django request objects in route handler functions.
	:return: The original Django request object.
	:raises:
		- TypeError if the current framework is not Django.
	Example Usage:
		>>> example1:
			@route('/example1', methods=['GET'])
			def example1(request: DjangoRequest):
				print("django request:", request)

		>>> example2:
			@route('/example2', methods=['POST'])
			def example2(request: "DjangoRequest"):
				print("django request:", request)
	"""
	__tachyons_typename__ = "request@DjangoRequest"

class FlaskRequest(BaseRequestType):
	"""
	A class to represent a Flask HTTP request object.
	It is used to type hint Flask request objects in route handler functions.
	:return: The original Flask request object.
	:raises:
		- TypeError if the current framework is not Flask.
	Example Usage:
		>>> example1:
			@route('/example1', methods=['GET'])
			def example1(request: FlaskRequest):
				print("flask request:", request)

		>>> example2:
			@route('/example2', methods=['POST'])
			def example2(request: "FlaskRequest"):
				print("flask request:", request)
	"""
	__tachyons_typename__ = "request@FlaskRequest"

class FastAPIRequest(BaseRequestType):
	"""
	A class to represent a FastAPI HTTP request object.
	It is used to type hint FastAPI request objects in route handler functions.
	:return: The original FastAPI request object.
	:raises:
		- TypeError if the current framework is not FastAPI.
	Example Usage:
		>>> example1:
			@route('/example1', methods=['GET'])
			def example1(request: FastAPIRequest):
				print("fastapi request:", request)

		>>> example2:
			@route('/example2', methods=['POST'])
			def example2(request: "FastAPIRequest"):
				print("fastapi request:", request)
	"""
	__tachyons_typename__ = "request@FastAPIRequest"

@RequestSpecialForm
class Cookie(BaseRequestType):
	"""
	A class to represent an HTTP cookie in a web request.
	It is used to extract cookie values from incoming requests.
	:param name: The name of the cookie to extract.
	:param converter: A callable to validate and convert the cookie value (default is str).
	:return: The value of the specified cookie, converted to the specified type.
	raises:
		- KeyError if the cookie is not found in the request, unless the type is Optional.
		- ValueError if the cookie value cannot be converted to the specified type.
	Examples:
		>>> example1:
			@route('/example1', methods=['GET'])
			def example1(session_id: Cookie["session_id"]):
				print ("session_id:", session_id)

		>>> example1:
			@route('/example2', methods=['GET'])
			def example2(user_id: Cookie["user_id", int]):
				print ("user_id:", user_id)
		>>> example3:
			from typing import Optional
			@route('/example3', methods=['GET'])
			def example3(unknown_cookie: Optional[Cookie["unknown_cookie"]]):
				if unknown_cookie is None:
					print ("unknown_cookie is not set")
				else:
					print ("unknown_cookie:", unknown_cookie)
	"""

	__tachyons_typename__ = "request@Cookie"

	def __init__(self, name: str, converter: Any = str):
		self._name      = name
		self._converter = converter

	@property
	def name(self):
		return self._name

	@property
	def converter(self):
		return self._converter

@RequestSpecialForm
class Body(BaseRequestType):

	"""
	A class to handle and parse the body of an HTTP request.
	It can parse the body content into different types based on the provided type validator.
	:param type_validator: A callable to validate and convert the body content (default is bytes).
	Example Usage:
		>>> example1:
			@route('/example1', methods=['POST'])
			def example1(body: Body):
				print("Parsed body as bytes:", body)

		>>> example2:
			@route('/example2', methods=['POST'])
			def example2(body: Body[dict]):
				print("Parsed body as dict:", body)

		>>> example3:
			@route('/example3', methods=['POST'])
			def example3(body: Body[int]):
				print("Parsed body as int:", body)

		>>> example3:
			@route('/example3', methods=['POST'])
			def example3(body: Body[YourCustomType]):
				print("Parsed body as YourCustomType:", body)
		"""
	__tachyons_typename__ = "request@Body"

	def __init__(self, converter: Any):
		self._converter = converter

	@property
	def converter(self):
		return self._converter

@RequestSpecialForm
class PathParameter(BaseRequestType):
	"""
	A class to represent a path parameter in a web request.
	It is used to extract parameters from the URL path.
	:param type: The expected type of the path parameter (e.g., str, int), default is str.
	:param name: The name of the path parameter to extract (optional).
	:return: The value of the specified path parameter, converted to the specified type.
	:raises:
		- ValueError if the path parameter value cannot be converted to the specified type.
	Examples:
		>>> example1:
			@route('/users/<user_id>', methods=['GET'])
			def example1(user_id: PathParameter[int]):
				print("User ID:", user_id)

		>>> example2:
			@route('/articles/<slug>', methods=['GET'])
			def example2(slug: PathParameter[str]):
				print("Article Slug:", slug)

		>>> example3:
			@route('/articles/<slug>', methods=['GET'])
			def example3(slug: PathParameter):
				print("Article Slug:", slug)

		>>> example4:
			@route('/articles/<slug>', methods=['GET'])
			def example4(slug: "PathParameter"):
				print("Article Slug:", slug)
	"""
	__tachyons_typename__ = "request@PathParameter"

	def __init__(self, converter: Any):
		self._converter = converter

	@property
	def converter(self):
		return self._converter

@RequestSpecialForm
class QueryParameter(BaseRequestType):
	"""
	A class to represent a query parameter in a web request.
	It is used to extract parameters from the URL query string.
	:param type: The expected type of the query parameter (e.g., str, int), default is str.
	:param name: The name of the query parameter to extract (optional).
	:return: The value of the specified query parameter, converted to the specified type.
	:raises:
		- KeyError if the query parameter is not found in the request, unless the type is Optional.
		- ValueError if the query parameter value cannot be converted to the specified type.
	Examples:
		>>> example1:
			@route('/search', methods=['GET'])
			def example1(q: QueryParameter[str]):
				print("Search query:", q)

		>>> example2:
			@route('/items', methods=['GET'])
			def example2(page: QueryParameter[int, "page"]):
				print("Page number:", page)

		>>> example3:
			from typing import Optional
			@route('/filter', methods=['GET'])
			def example3(category: Optional[QueryParameter[str, "category"]]):
				if category is None:
					print("No category filter applied")
				else:
					print("Category filter:", category)
		>>> example4:
			@route('/filter', methods=['GET'])
			def example4(category: "QueryParameter"):
				print("Category filter:", category)
	"""
	__tachyons_typename__ = "request@QueryParameter"

	def __init__(self, name: str, converter: Any = str):
		self._name      = name
		self._converter = converter

	@property
	def name(self):
		return self._name

	@property
	def converter(self):
		return self._converter

@RequestSpecialForm
class Header(BaseRequestType):
	"""
	A class to represent an HTTP request header.
	It is used to extract header values from incoming requests.
	:param name: The name of the header to extract.
	:return: The value of the specified header.
	:raises:
		- KeyError if the header is not found in the request, unless the type is Optional.
	Examples:
		>>> example1:
			@route('/example1', methods=['GET'])
			def example1(user_agent: Header["User-Agent"]):
				print("User-Agent:", user_agent)

		>>> example2:
			from typing import Optional
			@route('/example2', methods=['GET'])
			def example2(custom_header: Optional[Header["X-Custom-Header"]]):
				if custom_header is None:
					print("X-Custom-Header is not set")
				else:
					print("X-Custom-Header:", custom_header)
	"""
	__tachyons_typename__ = "request@Header"

	def __init__(self, name: str, value: str = None):
		self._name  = name
		self._value = value

	@property
	def name(self):
		return self._name

	def __str__(self):
		if (not hasattr(self, "_value")) or not self._value:
			return f"{self._name}:"
		return f"{self._name}: {self._value}"
	
	def __repr__(self):
		return self.__str__()

class BearerToken(BaseRequestType):
	"""
	A class to represent a Bearer token in the Authorization header of an HTTP request.
	It is used to extract and validate Bearer tokens from incoming requests.
	:return: The Bearer token string.
	:raises:
		- KeyError if the Authorization header is not found in the request, unless the type is Optional.
		- ValueError if the Authorization header does not contain a valid Bearer token.
	Examples:
		>>> example1:
			@route('/secure-endpoint', methods=['GET'])
			def secure_endpoint(token: BearerToken):
				print("Bearer Token:", token)

		>>> example2:
			from typing import Optional
			@route('/optional-endpoint', methods=['GET'])
			def optional_endpoint(token: Optional[BearerToken]):
				if token is None:
					print("No Bearer token provided")
				else:
					print("Bearer Token:", token)
	"""
	__tachyons_typename__ = "request@BearerToken"
