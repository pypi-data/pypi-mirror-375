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
  * File   : tachyons/parsing/__init__.py
  * Created: 2025/08/30 22:49:40 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import json
from typing import Any, Dict

def parsejson(data: Any):
	"""
	Parse JSON data from various formats.
	:param data: The data to parse, can be a dict, str, or bytes.
	:return: Parsed JSON data as a dict.
	"""
	if isinstance(data, dict):
		return data.copy()
	if isinstance(data, str):
		try:
			return json.loads(data.strip())
		except json.JSONDecodeError as e:
			pass
	if isinstance(data, bytes):
		try:
			return json.loads(data.decode('utf-8'))
		except json.JSONDecodeError as e:
			pass
	raise ValueError(f"Invalid JSON data")

def _get_query_strings(url: str):
  prefix = ""
  found  = False
  for item in url.split("/"):
    i = 0
    while i < len(item):
      if item[i].isalnum():
        prefix += item[i]
      elif item[i].isspace():
        prefix += item[i]
      elif item[i] in "._-":
        prefix += item[i]
      else:
        break
      i += 1
    if ( item[i:].startswith("?") ):
      found = True
      break
    while i < len(item):
      prefix += item[i]
      i += 1
    prefix += "/"
  if not found:
    return {}
  query_strings = url[url.index(prefix) + len(prefix):].lstrip("?")
  query_strings = query_strings.split("#")[0].strip()
  queries = {}
  while query_strings:
    val = ""
    key = query_strings
    for c in "&=":
      key = key.split(c)[0]
    query_strings = query_strings[len(key):].strip()
    if query_strings.startswith("="):
      query_strings = query_strings[1:]
      val = query_strings
      for c in "&":
        val = val.split(c)[0]
      query_strings = query_strings[len(val):]
    queries[key] = val
    if not query_strings.startswith("&"):
      break
    query_strings = query_strings.strip("&")
  return queries

def _match_query_parameters(url_pattern: str, request_path: str):
  # TODO: (url decode) request_path
  queryz_url_pattern  = _get_query_strings(url_pattern)
  queryz_request_path = _get_query_strings(request_path)
  query_parameters    = {}

  for key_pattern, val_pattern in queryz_url_pattern.items():
    if not key_pattern:
      continue
    val_request = queryz_request_path.get(key_pattern, None)
    converter   = None
    if val_pattern.startswith("<") and val_pattern.endswith(">"):
      if ":" in val_pattern:
        converter = val_pattern[1:].split(":")[0]
    query_parameters[key_pattern] = {
      "name" : key_pattern,
      "value": val_request,
      "type" : converter,
    }
  return query_parameters
