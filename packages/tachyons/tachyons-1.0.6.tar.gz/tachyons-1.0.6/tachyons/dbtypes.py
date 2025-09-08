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
  * File   : tachyons/dbtypes.py
  * Created: 2025/08/30 22:47:16 GMT+1
  * Updated: 2025/08/30 23:46:11 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

from tachyons.validators import BaseValidator
from tachyons.validators import EmailValidator
from tachyons.validators import PasswordValidator

class TachyonsBaseType:

	# def to_dict(self):
	# 	return ({"key": "value"})

	# def __json__(self):
	# 	return ({"key": "value"})

	# def __repr__(self):
	# 	return (str(self))

	def __init__(self, required: bool = True, customValidator = None, nullable: bool = False, unique: bool = False):
		self._required = True if required else False
		if customValidator:
			if not isinstance(customValidator, BaseValidator):
				raise TypeError("Custom validator must be an instance of tachyons.validators.BaseValidator")
			self._validator = customValidator

	def setvalue(self, value):
		clsname = self.__class__.__name__
		raise NotImplementedError(f"{clsname}.setvalue() must be implemented")

	def isrequired(self):
		return self._required

	def __str__(self):
		return (str(self._value))

	def __repr__(self):
		return (str(self))

	def __serialize__(self):
		clsname = self.__class__.__name__
		raise NotImplementedError(f"{clsname}.__serialize__() must be implemented")

class String(TachyonsBaseType):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def setvalue(self, value: str):
		self._value = str(value)
		return self

	def __jserialize__(self):
		return str(self._value)

class Email(TachyonsBaseType):

	def __init__(self, *args, **kwargs):
		self._validator = EmailValidator
		super().__init__(*args, **kwargs)
	
	def setvalue(self, value: str):
		self._value = self._validator.validate(str(value).strip())
		return self

	def __jserialize__(self):
		return str(self._value)

class Password(TachyonsBaseType):

	def __init__(self, *args, **kwargs):
		self._validator = PasswordValidator
		super().__init__(*args, **kwargs)

	def setvalue(self, value: str):
		self._value = self._validator.validate(str(value))
		return self

	def __jserialize__(self):
		return str(self._value)

class Field(TachyonsBaseType):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def setvalue(self, value: str):
		self._value = str(value)
		return self
