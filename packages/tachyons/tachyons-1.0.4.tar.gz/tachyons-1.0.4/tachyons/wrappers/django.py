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
  * File   : tachyons/wrappers/django.py
  * Created: 2025/08/30 22:50:40 GMT+1
  * Updated: 2025/09/05 16:28:00 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import tachyons.docs
from tachyons.docs     import TachyonsOpenAPIDocs
from tachyons.settings import TachyonsSettings

class DjangoWrapper:
	"""
	DjangoWrapper class to integrate with Django framework.
	This class wraps a Django application instance and sets it as the
	base application in TachyonsSettings.
	"""

	def __init__(self, app, docs: TachyonsOpenAPIDocs = tachyons.docs.default):
		"""
		DjangoWrapper class to integrate with Django framework.
		"""
		self._app  = app
		self._docs = docs
		TachyonsSettings.set_base_app(app)
		TachyonsSettings.set_base_engine("django")

	def __call__(self, environ, start_response):
		"""
		Ensure this wrapper is still a valid WSGI application.
		This allows DjangoWrapper to be used directly as `application`.
		"""
		return self._app(environ, start_response)

	@property
	def app(self):
		"""
		Get the wrapped Django application instance.
		"""
		return self._app
	
	@property
	def docs(self):
		"""
		Get the OpenAPI documentation configuration.
		"""
		return self._docs
