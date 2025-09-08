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
  * File   : tachyons/serializers.py
  * Created: 2025/09/01 10:46:12 GMT+1
  * Updated: 2025/09/01 14:10:44 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

from typing import Any

class JsonSerializer:
	"""
	A simple JSON serializer class.
	"""
	@staticmethod
	def serialize(data: Any) -> Any:
		"""
		Serializes the given data to a JSON-compatible format.
		Args:
			data (Any): The data to serialize.
		Returns:
			Any: The serialized data.
		"""
		for key in ["__jserialize__"]:
			if hasattr(data, key):
				return getattr(data, key)()
		if JsonSerializer.is_dictlike(data):
			return { key: JsonSerializer.serialize(data[key]) for key in data }
		elif JsonSerializer.is_listlike(data):
			return [JsonSerializer.serialize(item) for item in data]
		return data

	@staticmethod
	def is_dictlike(obj: Any) -> bool:
		"""
		Checks if the object is dict-like.
		"""
		return isinstance(obj, dict)

	@staticmethod
	def is_listlike(obj: Any) -> bool:
		"""
		Checks if the object is list-like (list, tuple, or set).
		"""
		return isinstance(obj, (list, tuple, set))
