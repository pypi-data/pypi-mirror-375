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
  * File   : tachyons/routing.py
  * Created: 2025/08/30 22:48:04 GMT+1
  * Updated: 2025/09/05 00:00:29 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import json
import logging
import inspect
from typing                    import Any, Dict
from tachyons.settings         import TachyonsSettings
from tachyons.routers.base     import *
from tachyons.routers.base     import BaseRouter
from tachyons.routers.django   import DjangoRouter
from tachyons.routers.flask    import FlaskRouter
from tachyons.routers.fastapi  import FastAPIRouter
from tachyons.parsing.base     import BaseParser

logger = logging.getLogger(__name__)

def route(
		rule                : str,
		handler             : Any            = None ,
		methods             : Any            = "GET",
		engine              : str            = None ,
		baseapp             : Any            = None ,
		response_dto        : Any            = None ,
		responses           : Any            = None ,
		json_responses      : Dict[Any, Any] = None ,
		summary             : str            = ""   ,
		description         : str            = ""   ,
		response_description: str            = ""   ,
		body                : Dict[str, Any] = None ,
		*args, **kwargs
	):
	"""
	route decorator to define a route for a handler function.
	Args:
		rule (str): The URL rule as string.
		handler (Any, optional): The handler function. Defaults to None.
		methods (Any, optional): List of HTTP methods. Defaults to "GET".
		engine (str, optional): The web framework engine. Defaults to None.
		baseapp (Any, optional): The base application instance. Defaults to None.
		response_dto (Any, optional): The response data transfer object. Defaults to None.
		responses (Any, optional): Additional responses. Defaults to None.
		json_responses (Dict[Any, Any], optional): JSON responses schema. Defaults to None.
		summary (str, optional): Summary of the endpoint. Defaults to "".
		description (str, optional): Description of the endpoint. Defaults to "".
		response_description (str, optional): Description of the response. Defaults to "".
		body (Dict[str, Any], optional): Request body schema. Defaults to None.
		*args: Additional positional arguments.
		**kwargs: Additional keyword arguments.
	Returns:
		Any: The decorated handler function.
	"""

	baseapp = TachyonsSettings.get_base_app()
	engine  = TachyonsSettings.get_base_engine()

	if rule == "[404-NOT-FOUND]":
		raise NotImplementedError("404 handler not implemented yet.")

	path       = BaseParser.parse_path(rule)
	methods    = BaseParser.parse_methods(methods)
	url_params = BaseParser.parse_parameters(rule)

	if not responses:
		responses = {}
	def decorator(handler, path: str = path):
		"""
		The actual decorator function that registers the route.
		Args:
			handler (Any): The handler function to be decorated.
			path (str): The URL path for the route.
		Returns:
			Any: The decorated handler function.
		"""
		BaseRouter.add_registered_endpoint(
			endpoint = path,
			handler = handler,
			methods = methods
		)

		signature = inspect.signature(handler)
		funcargs  = signature.parameters
		for parameter_name in url_params.keys():
			if not (parameter_name in funcargs):
				raise ValueError(f"Parameter '{parameter_name}' not found in handler function '{handler.__name__}'")

		if ( engine == "django" ):
			"""
			Add the route to the Django router.
			"""
			DjangoRouter.add(
				rule         = path,
				handler      = handler,
				response_dto = response_dto,
			)

		elif ( engine == "flask" ):
			"""
			Add the route to the Flask router.
			"""
			FlaskRouter.add(
				rule    = rule,
				handler = handler,
				baseapp = baseapp
			)
		elif ( engine == "fastapi" ):
			"""
			Add the route to the FastAPI router.
			"""
			FastAPIRouter.add()
		else:
			raise NotImplementedError("Engine not implemented: " + engine)
		return handler

	if handler:
		return decorator(handler)
	return decorator
