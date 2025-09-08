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
  * File   : tachyons/exceptions/http.py
  * Created: 2025/08/30 22:48:34 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

class TachyonsHTTPError(Exception):
	"""
	Custom exception class for HTTP errors.
	This class is used to raise HTTP errors with a specific status code and message.
	"""

	__is_http_exception__ = True

	def __init__(self, message: str, status: int = 400):
		if not isinstance(message, str):
			raise TypeError("message must be a string")
		status = int(str(status), 10)
		super().__init__(message)
		self._status  = status
		self._message = message
    
	@property
	def status(self) -> int:
		"""
		Returns the HTTP status code.
		This property provides access to the HTTP status code of the error.
		"""
		return self._status

	@property
	def message(self) -> str:
		"""
		Returns the error message.
		This property provides access to the error message of the HTTP error.
		"""
		return self._message

	def json(self) -> dict[str, object]:
		"""
		Returns a JSON representation of the error.
		This method formats the error details into a JSON object.
		"""
		return {
			"success" : False,
			"status" : self.status,
			"message": self.message,
			"error"  : self.message
		}

HTTPException = TachyonsHTTPError

def isHTTPException(e: Exception) -> bool:
	"""
	Check if the exception is an HTTPException.
	:param e: The exception to check.
	:return: True if the exception is an HTTPException, False otherwise.
	"""
	try:
		if not hasattr(e, "__is_http_exception__"):
			return False
		if not e.__is_http_exception__:
			return False
		if not hasattr(e, "status"):
			return False
		if not hasattr(e, "message"):
			return False
		if not (isinstance(e.__class__.status, property)):
			return False
		if not (isinstance(e.__class__.message, property)):
			return False
	except:
		return False
	return True

def asHTTPException(e: Exception) -> Exception | None:
	"""
	Get the HTTPException from the exception if it is one.
	:param e: The exception to check.
	:return: The HTTPException if the exception is an HTTPException, None otherwise.
	"""
	if isHTTPException(e):
		return e
	if isinstance(e, AssertionError):
		return asHTTPException(e.args[0])
	return None
