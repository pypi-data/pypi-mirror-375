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
  * File   : tachyons/forms.py
  * Created: 2025/08/30 22:47:28 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import json

from tachyons.exceptions.http import TachyonsHTTPError

class TachyonsBaseForm:
	__columns__ = {}

	# def __init_subclass__(self, *args, **kwargs):
	# 	print ( "called!" )

	def is_valid(self):
		"""Check if the form is valid. This method should be overridden in subclasses."""
		return True

	def unifyattr(key):
		key = key.lower().strip()
		return key

	# def __getattr__(self, attr):
	# 	return str(attr)

	def __init__(self, byte_data: bytes = b"", json_data: dict = None):

		if byte_data:
			raw_str   = byte_data.decode("utf-8")
			json_data = json.loads(raw_str)
		if not json_data:
			json_data = {}
		jdata = {}
		for key, val in json_data.items():
			jdata[ TachyonsBaseForm.unifyattr(key) ] = val

		visited: dict = {}

		for attr_name, attr_type in self.__annotations__.items():
			uni_attr_name = TachyonsBaseForm.unifyattr(attr_name)
			if not (uni_attr_name in jdata):
				if attr_type.isrequired():
					raise TachyonsHTTPError(
						status = 400,
						message = f"Missing required field: {uni_attr_name}"
					)
				continue
			attr_type = attr_type.setvalue(jdata[uni_attr_name])
			setattr(self, attr_name, attr_type)
			visited[attr_name] = True

		for attr_name, attr_type in self.__annotations__.items():
			if attr_name not in visited:
				setattr(self, attr_name, None)
