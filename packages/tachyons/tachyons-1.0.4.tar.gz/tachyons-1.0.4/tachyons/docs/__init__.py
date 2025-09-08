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
  * File   : tachyons/docs/__init__.py
  * Created: 2025/08/04 23:22:11 GMT+1
  * Updated: 2025/09/05 16:52:53 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import os
import json
from tachyons.routing  import route
from django.http       import HttpResponse
from tachyons.settings import TachyonsSettings

class TachyonsOpenAPIDocs:

	def __init__(self, 
			templates_dir: str = None,
			prefix       : str = "/docs",
			default      : str = None,
			title        : str = "OpenAPI Docs",
			description  : str = "A simple example OpenAPI spec.",
			version      : str = "1.0.0"
		):
		if default is not None and (not isinstance(default, str) or not default.strip()):
			raise ValueError("`default UI` must be a non-empty string or None, got: {default}")
		self._prefix        = prefix.strip("/")
		self.__templates__  = {}
		self._templates_dir = templates_dir
		if not self._templates_dir:
			f = os.path.abspath(__file__)
			while f and f != os.path.dirname(f):
				d = os.path.join(f, "templates", "docs")
				if os.path.exists(d):
					self._templates_dir = d
					break
				f = os.path.dirname(f)
		for template_name in os.listdir(self._templates_dir):
			template_file = os.path.join(self._templates_dir, template_name, "index.html")
			if not os.path.exists(template_file):
				continue
			template_data = open(template_file).read()
			self.__templates__[template_name.lower().strip()] = {
				"content": template_data
			}
		if not (default in self.__templates__):
			if ("scalar" in self.__templates__):
				default = "scalar"
			else:
				default = list(self.__templates__)[0]
		self._default = default

	@property
	def prefix(self):
		return self._prefix

	def html(self):
		html = self.__templates__[self._default]["content"]
		html = html.replace("/docs/openapi.json", "/docs/openapi.json")
		return HttpResponse(html, content_type="text/html")

	def json(self):
		openapi_json = {}
		return openapi_json

default = TachyonsOpenAPIDocs().html()
