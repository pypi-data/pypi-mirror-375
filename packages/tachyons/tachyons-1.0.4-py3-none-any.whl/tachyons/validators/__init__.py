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
  * File   : tachyons/validators/__init__.py
  * Created: 2025/08/30 22:50:17 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

from typing import Any
from tachyons.exceptions.http import TachyonsHTTPError

class BaseValidator:
	@staticmethod
	def isvalid(value) -> bool:
		raise NotImplementedError("isvalid method must be implemented in subclasses")

	@staticmethod
	def validate(value: Any) -> Any:
		raise NotImplementedError("validate method must be implemented in subclasses")

class EmailValidator:

	LOCAL_PART_CHARSET  = sorted(set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.!#$%&'*+/=?^_`{|}~"))
	DOMAIN_PART_CHARSET = sorted(set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-."))

	@staticmethod
	def isvalid(email: str) -> bool:
		"""
		Checks if the given email is valid.
		:param email: The email address to validate.
		:return: True if the email is valid, False otherwise.
		"""
		if not email or not isinstance(email, str):
			return False
		try:
			EmailValidator.validate(email)
			return True
		except TachyonsHTTPError:
			pass
		return False

	@staticmethod
	def validate(email: str) -> str:
		_email = str(email)
		if _email.count("@") != 1:
			raise TachyonsHTTPError("Email must contain exactly one '@' character")
		[local_part, domain] = _email.split("@")
		if not local_part or not domain:
			raise TachyonsHTTPError("Email must have both local part and domain")
		"""
			Local part (before @):

			Cannot start or end with a dot
			Cannot have consecutive dots (..)
			Otherwise dots can appear anywhere in between
		"""
		if local_part.startswith(".") or local_part.endswith("."):
			raise TachyonsHTTPError("Local part cannot start or end with '.'")
		if ".." in local_part:
			raise TachyonsHTTPError("Local part cannot contain consecutive '.' characters")
		"""
			Domain part (after @):

			Cannot start or end with a dot
			Cannot have consecutive dots (..)
			Must separate valid labels
		"""
		if domain.startswith(".") or domain.endswith("."):
			raise TachyonsHTTPError("Domain part cannot start or end with '.'")
		if ".." in domain:
			raise TachyonsHTTPError("Domain part cannot contain consecutive '.' characters")
		for c in local_part:
			if not (c in EmailValidator.LOCAL_PART_CHARSET):
				raise TachyonsHTTPError(f"Invalid character in local part")
		for c in domain:
			if not (c in EmailValidator.DOMAIN_PART_CHARSET):
				raise TachyonsHTTPError(f"Invalid character in domain part")
		return _email

class PasswordValidator:

	LOWERCASE_CHARSET = "abcdefghijklmnopqrstuvwxyz"
	UPPERCASE_CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" 
	DIGITS_CHARSET    = "0123456789"
	SPECIAL_CHARSET   = "!@#$%^&*()_+-=[]{}|;':\",./<>?~`"

	@staticmethod
	def isvalid(
			password         : str,
			lowercase_charset: str = LOWERCASE_CHARSET,
			uppercase_charset: str = UPPERCASE_CHARSET,
			digits_charset   : str = DIGITS_CHARSET   ,
			special_charset  : str = SPECIAL_CHARSET  ,
			min_length       : int = 8,
			max_length       : int = 64,
		) -> bool:
			if not password or not isinstance(password, str):
				return False
			try:
				PasswordValidator.validate(
					password          = password,
					lowercase_charset = lowercase_charset,
					uppercase_charset = uppercase_charset,
					digits_charset    = digits_charset   ,
					special_charset   = special_charset  ,
					min_length		  = min_length       ,
					max_length		  = max_length       ,
				)
				return True
			except ValueError:
				pass
			return False

	@staticmethod
	def validate(
			password         : str,
			lowercase_charset: str = LOWERCASE_CHARSET,
			uppercase_charset: str = UPPERCASE_CHARSET,
			digits_charset   : str = DIGITS_CHARSET   ,
			special_charset  : str = SPECIAL_CHARSET  ,
			min_length       : int = 8,
			max_length       : int = 64,
		) -> str:
		password = str(password)
		_lowercases: int = 0
		_uppercases: int = 0
		_digits    : int = 0
		_specials  : int = 0
		for c in password:
			if lowercase_charset and (c in lowercase_charset):
				_lowercases += 1
			elif uppercase_charset and (c in uppercase_charset):
				_uppercases += 1
			elif digits_charset and (c in digits_charset):
				_digits += 1
			elif special_charset and (c in special_charset):
				_specials += 1
			else:
				raise TachyonsHTTPError(f"Invalid character '{c}' in password.")
		if lowercase_charset and _lowercases < 1:
			raise TachyonsHTTPError("Password must contain at least one lowercase character")
		if uppercase_charset and _uppercases < 1:
			raise TachyonsHTTPError("Password must contain at least one uppercase character")
		if digits_charset and _digits < 1:
			raise TachyonsHTTPError("Password must contain at least one digit")
		if special_charset and _specials < 1:
			raise TachyonsHTTPError("Password must contain at least one special character")
		if len(password) < min_length:
			raise TachyonsHTTPError(f"Password must be at least {min_length} characters long")
		if len(password) > max_length:
			raise TachyonsHTTPError(f"Password must be at most {max_length} characters long")
		return password
