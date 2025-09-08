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
  * File   : tachyons/routers/base.py
  * Created: 2025/08/30 22:49:54 GMT+1
  * Updated: 2025/09/05 00:06:00 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import os
import re
import sys
import json
import uuid
import logging
import inspect
import asyncio
import functools
from typing                   import Any, List, Dict, Optional, Callable
from tachyons.response        import JsonResponse
from tachyons.exceptions.http import TachyonsHTTPError
from tachyons.settings        import TachyonsSettings
from tachyons.forms           import TachyonsBaseForm
from tachyons.parsing.base    import BaseParser
from tachyons.request         import Cookie         as TachyonsRequestCookie
from tachyons.request         import Body           as TachyonsRequestBody
from tachyons.request         import Header         as TachyonsRequestHeader
from tachyons.request         import QueryParameter as TachyonsRequestQueryParameter
from tachyons.request         import PathParameter  as TachyonsRequestPathParameter
from tachyons.request         import BearerToken    as TachyonsBearerToken
from tachyons.request         import FastAPIRequest as TachyonsFastAPIRequest
from tachyons.request         import FlaskRequest   as TachyonsFlaskRequest
from tachyons.request         import DjangoRequest  as TachyonsDjangoRequest
from tachyons.parsing         import parsejson

logger = logging.getLogger(__name__)

def is_optional_type(param) -> bool:
	"""
	Check if the given annotation is an Optional type.
	"""
	try:
		if param._default is not inspect._empty:
			return True
	except:
		pass
	panno = param.annotation
	try:
		if str(panno).startswith("typing.Optional["):
			return True
		if not panno._getitem:
			return False
	except:
		pass
	return False

def get_default_value(param) -> Any:
	"""
	Get the default value of the given parameter, if any.
	"""
	try:
		if param._default is not inspect._empty:
			return param._default
	except:
		pass
	return None

def is_tachyons_typename(param, name, typeval) -> bool:
	"""
	Check if the given annotation is of the specified Tachyons type name.
	"""
	panno = param.annotation
	if panno == typeval:
		return True
	try:
		if isinstance(panno, typeval):
			return True
	except:
		pass
	try:
		if is_optional_type(param):
			panno = panno.__args__[0]
	except:
		pass
	if panno == name:
		return True
	if (panno == inspect._empty) or (panno is None):
		return False
	name = str(name).strip().lower()
	if str(panno).lower().strip() == name:
		return True
	try:
		tname = str(panno.__tachyons_typename__).strip().lower()
		if tname == "request@" + name:
			return True
	except:
		pass
	return False

def _map_bearer_token_argument(pname, panno, param, arguments, headers, **kwargs) -> bool:
	if not is_tachyons_typename(param, "BearerToken", TachyonsBearerToken):
		return False
	authorization = BaseRouter._get_header_value("Authorization", headers)
	if authorization is None:
		if not is_optional_type(param):
			raise TachyonsHTTPError(
				status  = 401,
				message = "Missing Authorization header",
			)
		arguments[pname] = get_default_value(param)
		return True
	authorization = str(authorization)
	if not authorization.lower().startswith("bearer "):
		raise TachyonsHTTPError(
			status  = 401,
			message = "Invalid Authorization header",
		)
	bearer_token = authorization[7:].strip()
	if not bearer_token:
		raise TachyonsHTTPError(
			status  = 401,
			message = "Invalid Authorization header",
		)
	arguments[pname] = bearer_token
	return True

def _map_request_header_argument(pname, panno, param, arguments, headers, **kwargs) -> bool:
	if not is_tachyons_typename(param, "header", TachyonsRequestHeader):
		return False
	header_name: str = pname
	try   : header_name = param.annotation.name
	except: header_name = pname
	header_value = BaseRouter._get_header_value(header_name, headers)
	if header_value is None:
		if not is_optional_type(param):
			logger.info(f" - Missing required header: {header_name}")
			raise TachyonsHTTPError(
				status  = 400,
				message = "Bad Request",
			)
		arguments[pname] = get_default_value(param)
		return True
	arguments[pname] = header_value
	return True

def _map_query_parameter_argument(pname, panno, param, arguments, query_params, **kwargs) -> bool:
	if not is_tachyons_typename(param, "QueryParameter", TachyonsRequestQueryParameter):
		return False
	try   : converter = panno.converter
	except: converter = str
	try   : query_name = panno.name
	except: query_name = pname
	query_value = BaseRouter._get_query_value(query_name, query_params)
	if query_value is None:
		if not is_optional_type(param):
			logger.info(f" - Missing required query parameter: {query_name}")
			raise TachyonsHTTPError(
				status  = 400,
				message = "Bad Request",
			)
		arguments[pname] = get_default_value(param)
		return True
	arguments[pname] = converter(query_value)
	return True

def _map_path_parameter_argument(pname, panno, param, arguments, path_parameters, **kwargs) -> bool:
	if not is_tachyons_typename(param, "PathParameter", TachyonsRequestPathParameter):
		return False
	try   : converter = panno.converter
	except: converter = None
	try   : param_name = panno.name
	except: param_name = pname
	if not (param_name in path_parameters):
		logger.info(f" - Missing required path parameter: {param_name}")
		raise TachyonsHTTPError(
			status  = 500,
			message = f"Path parameter not found",
		)
	if (converter is not None) and (path_parameters[param_name]["type"] is not None):
		if converter != path_parameters[param_name]["type"]:
			raise TachyonsHTTPError(
				status  = 400,
				message = f"Path parameter type mismatch for '{param_name}'",
			)
	if converter is None:
		converter = path_parameters[param_name]["type"]
	if converter is None:
		converter = str
	arguments[pname] = converter(path_parameters[param_name]["value"])
	return True


def _map_request_body_argument(pname, panno, param, arguments, rawbody, **kwargs) -> bool:
	if not is_tachyons_typename(param, "body", TachyonsRequestBody):
		return False
	if is_optional_type(param) and ((not rawbody) or (len(rawbody) == 0)):
		arguments[pname] = get_default_value(param)
		return True
	try:
		converter = panno.converter
	except:
		converter = bytes
	if converter in [None, inspect._empty, bytes, "bytes"]:
		arguments[pname] = rawbody
		return True
	if converter in [str, "str", "string"]:
		arguments[pname] = rawbody.decode('utf-8')
		return True
	if converter in [dict, "dict", json, "json", Dict]:
		try:
			arguments[pname] = parsejson(rawbody)
		except Exception as e:
			logger.info(f" - Invalid JSON body: {e}")
			raise TachyonsHTTPError(
				status  = 400,
				message = "Invalid JSON body",
			)
		return True
	arguments[pname] = converter(rawbody)
	return True

def _map_request_cookie_argument(pname, panno, param, arguments, cookies, **kwargs) -> bool:
	if not is_tachyons_typename(param, "cookie", TachyonsRequestCookie):
		return False
	cookie_name: str = pname
	try   : cookie_name = param.annotation.name
	except: cookie_name = pname
	try   : converter = panno.converter
	except: converter = str
	cookie_value = BaseRouter._get_cookie_value(cookie_name, cookies)
	if cookie_value is None:
		if not is_optional_type(param):
			logger.info(f" - Missing required cookie: {cookie_name}")
			raise TachyonsHTTPError(
				status  = 400,
				message = "Bad Request",
			)
		arguments[pname] = get_default_value(param)
		return True
	arguments[pname] = converter(cookie_value)
	return True

def _map_argument(callback, pname, panno, param, arguments, cookies, headers, rawbody, query_params, path_parameters):
	result = callback(
		pname           = pname,
		panno           = panno,
		param           = param,
		arguments       = arguments,
		cookies         = cookies,
		headers         = headers,
		rawbody         = rawbody,
        query_params    = query_params,
        path_parameters = path_parameters,
	)
	return result

def is_subclass(a, b):
  try:
    if issubclass(a, b):
      return True
  except:
    pass
  return False

class app:
  handler404 = None

  @staticmethod
  def _pyfind(path: str, result = None):
    excluded_names = [
      "__pycache__",
    ]
    if result is None:result = {}
    try   : children = os.listdir(path)
    except: return result
    for child_name in children:
      if child_name.startswith("."):
        continue
      if child_name in excluded_names:
        continue
      child_path = os.path.join(path, child_name)
      app._pyfind(path = child_path, result = result)
      file_ext = child_name.split(".")[-1].lower()
      if not (file_ext in ["py", "pyc"]):
        continue
      result[child_path] = True
      result[os.path.join(path, "__init__.py")] = True
    return result

  @staticmethod
  def load_dir(path: str):
    result = app._pyfind(path)
    for module_file in result:
      module_name = module_file.split("/")[-1].split(".")[0]
      module_dir  = os.path.dirname(module_file)
      sys.path.insert(0, module_dir)
      exec(f"from {module_name} import __name__")
      for i in range(len(sys.path)):
        if sys.path[i] == module_dir:
          sys.path = sys.path[:i] + sys.path[i + 1:]
          break

  @staticmethod
  def urlpatterns(*args, **kwargs):
    TachyonsSettings.get_django_urlpatterns()
    return TachyonsSettings.get_django_urlpatterns()

class BaseRouter:

  @staticmethod
  def add_registered_endpoint(methods: list[str], endpoint: str, handler: Any):

    for c in "?#&":
      endpoint = endpoint.split(c)[0]

    if not (endpoint in TachyonsSettings.__settings__["tachyons"]["endpoints"]):
      TachyonsSettings.__settings__["tachyons"]["endpoints"][endpoint] = {}

    for method in methods:
      TachyonsSettings.__settings__["tachyons"]["endpoints"][endpoint][method] = handler

  @staticmethod
  def get_registered_endpoint_handler(method: str, endpoint: str):

    for c in "?#&":
      endpoint = endpoint.split(c)[0]

    if not (endpoint in TachyonsSettings.__settings__["tachyons"]["endpoints"]):
      raise TachyonsHTTPError(
        status  = 404,
        message = "Endpoint not found: " + endpoint,
      )

    handlers = TachyonsSettings.__settings__["tachyons"]["endpoints"][endpoint]

    if not (method in handlers):
      raise TachyonsHTTPError(
        status  = 405,
        message = "Method not allowed for endpoint: " + endpoint + ", method: " + method,
      )

    return handlers[method]

  @staticmethod
  def _norm_header_name(header_name: str) -> str:
    header_name = str(header_name).strip().lower()
    return header_name

  @staticmethod
  def _get_header_name(pname, param):
    header_name: str = param.annotation.name
    if header_name:
      return header_name
    return pname

  @staticmethod
  def _get_header_value(header_name: str, headers: dict) -> str:
    header_value = headers.get(header_name, None)
    if header_value is not None:
      return header_value
    header_name = BaseRouter._norm_header_name(header_name)
    for key, val in headers.items():
      key = BaseRouter._norm_header_name(key)
      if key == header_name:
        return val
    return None

  @staticmethod
  def _norm_cookie_name(cookie_name: str) -> str:
    cookie_name = str(cookie_name).strip()
    return cookie_name

  @staticmethod
  def _get_cookie_name(pname, param):
    cookie_name: str = param.annotation.name
    if cookie_name:
      return cookie_name
    return pname

  @staticmethod
  def _get_cookie_value(cookie_name: str, cookies: dict) -> str:
    cookie_value = cookies.get(cookie_name, None)
    if cookie_value is not None:
      return cookie_value
    cookie_name = BaseRouter._norm_cookie_name(cookie_name)
    for key, val in cookies.items():
      key = BaseRouter._norm_cookie_name(key)
      if key == cookie_name:
        return val
    return None

  @staticmethod
  def _norm_query_name(query_name: str) -> str:
    query_name = str(query_name).strip()
    return query_name

  @staticmethod
  def _get_query_name(pname, param):
    query_name: str = param.annotation.name
    if query_name:
      return query_name
    return pname

  @staticmethod
  def _get_query_value(query_name: str, querys: dict) -> str:
    query_value = querys.get(query_name, None)
    if query_value is not None:
      return query_value
    query_name = BaseRouter._norm_query_name(query_name)
    for key, val in querys.items():
      key = BaseRouter._norm_query_name(key)
      if key == query_name:
        return val
    return None

  @staticmethod
  def _match_url_patterns(url_pattern: str, request_path: str):
    original_url_pattern  = url_pattern
    original_request_path = request_path

    if ("://" in url_pattern[:10]):
      raise ValueError("Invalid request path: " + url_pattern)

    if ("://" in request_path[:10]):
      raise ValueError("Invalid request path: " + request_path)
    for c in "?&#":
      request_path = request_path.split(c)[0]
      url_pattern  = url_pattern.split(c)[0]
    request_path = request_path.strip("/")
    url_pattern  = url_pattern.strip("/")

    splited_request_path = request_path.split("/")
    splited_url_pattern  = url_pattern.split("/")

    if len(splited_request_path) != len(splited_url_pattern):
      raise ValueError(
        "Invalid request path: " + original_request_path + " != " + original_url_pattern
      )
    matched_arguments = {}
    for i in range(len(splited_request_path)):
      pattren   = splited_url_pattern[i]
      reqpath   = splited_request_path[i]
      varname   = None
      converter = None
      if pattren.startswith("<") and pattren.endswith(">"):
        [_converter, _varname] = ( [None] + pattren[1:-1].strip().split(":") )[-2:]
        varname   = _varname
        converter = _converter
      elif pattren.startswith("{") and pattren.endswith("}"):
        varname   = pattren[1:-1]
        converter = None
      elif reqpath != pattren:
        raise ValueError(
          "Invalid request path: " + original_request_path + " != " + original_url_pattern
        )
      if converter is not None:
        converter = converter.strip()
        if converter in ["int", "integer", "number"]:
          converter = int
        elif converter in ["", "str"]:
          converter = str
        else:
          raise ValueError(
            "Invalid converter: '" + converter + "' in request path: " + original_request_path
          )
      matched_arguments[varname] = {
        "name" : varname,
        "value": reqpath,
        "type" : converter,
      }
    return matched_arguments

  @staticmethod
  def is_typename(panno: Any, name: str):
    try:
      typehint = getattr(panno, "__tachyons_typename__")
    except:
      typehint = None
    if (not typehint) or (not name):
      return False
    name     = str(name).strip().lower()
    typehint = str(typehint).strip().lower()
    if (not name) or (not typehint):
      return False
    return (name == typehint)

  @staticmethod
  def _map_custom_argument(
    pname    : str,
    panno    : Any,
    param    : Any,
    arguments: dict,
        cookies  : dict  = None,
        headers  : dict  = None,
        query    : dict  = None, 
        payload  : dict  = None,
        rawbody  : bytes = None,
  ):
    try:
      iscustomtype = getattr(panno, "__tachyons_customtype__")
    except:
      iscustomtype = None
    if not iscustomtype:
      return False

    arguments[pname] = panno(
      cookies = cookies,
      headers = headers,
      query   = query, 
      payload = payload,
      rawbody = rawbody,
    )

    return True

  @staticmethod
  def create_arguments(
		request_path    : str,
		url_pattern     : str,
		query_params    : dict,
		headers         : Any,
		cookies         : dict,
		body_content    : Any,
		handler         : Any,
		query_parameters: dict = None,
		django_request  : Any  = None,
		flask_request   : Any  = None,
		fastapi_request : Any  = None,
    ):
    arguments        = {}
    signature        = inspect.signature(handler)
    path_paramerters = BaseRouter._match_url_patterns(url_pattern, request_path)

    for pname, param in signature.parameters.items():
      panno = param.annotation

      kwinfo = {
        "pname"          : pname       ,
        "panno"          : panno       ,
        "param"          : param       ,
        "arguments"      : arguments   ,
        "cookies"        : cookies     ,
        "headers"        : headers     ,
        "rawbody"        : body_content,
        "query_params"   : query_params,
        "path_parameters": path_paramerters,
      }

      if False:
        pass
      elif is_tachyons_typename(param, "DjangoRequest", TachyonsDjangoRequest):
        arguments[pname] = django_request
      elif is_tachyons_typename(param, "FlaskRequest", TachyonsFlaskRequest):
        arguments[pname] = flask_request
      elif is_tachyons_typename(param, "FastAPIRequest", TachyonsFastAPIRequest):
        arguments[pname] = fastapi_request
      elif _map_argument(_map_request_header_argument, **kwinfo):
        pass
      elif _map_argument(_map_request_cookie_argument, **kwinfo):
        pass
      elif _map_argument(_map_bearer_token_argument, **kwinfo):
        pass
      elif _map_argument(_map_request_body_argument, **kwinfo):
        pass
      elif _map_argument(_map_query_parameter_argument, **kwinfo):
        pass
      elif _map_argument(_map_path_parameter_argument, **kwinfo):
        pass
      elif BaseRouter._map_custom_argument(pname, panno, param, arguments, cookies = cookies, rawbody = body_content):
        pass

      # - - - - - - - - - <path> - - - - - - - - -
      elif path_paramerters and (pname in path_paramerters):
        varname   = path_paramerters[pname]["name"]
        varvalue  = path_paramerters[pname]["value"]
        converter = path_paramerters[pname]["type"]
        if (converter is None) and not (panno is inspect._empty):
          converter = panno
        if converter is None:
          converter = str
        varvalue = converter(varvalue)
        arguments[pname] = varvalue

      # - - - - - - - - - </path> - - - - - - - -

      # - - - - - - - - - <query> - - - - - - - - -

      elif query_parameters and (pname in query_parameters):
        query_name  = query_parameters[pname]["name"]
        query_value = query_parameters[pname]["value"]
        converter   = query_parameters[pname]["type"]
        if (converter is None) and not (panno is inspect._empty):
          converter = panno
        if converter is None:
          converter = str
        arguments[pname] = converter(query_value)

      # - - - - - - - - - </query> - - - - - - - -

      elif is_subclass(panno, TachyonsBaseForm):
        form_object = panno(byte_data = body_content)
        if not form_object.is_valid():
          return JsonResponse(
            {
              "sucess" : False,
              "status" : 400,
              "message": "Invalid body data",
              "error"  : "Invalid body data",
            },
            status = 400
          )
        arguments[pname] = form_object

    return arguments
