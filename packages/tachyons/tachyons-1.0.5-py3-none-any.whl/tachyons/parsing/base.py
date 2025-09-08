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
  * File   : tachyons/parsing/base.py
  * Created: 2025/08/30 22:49:43 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

from typing import Any, List

class BaseParser:

  @staticmethod
  def is_varchar(c: str) -> bool:
    """
    Check if the character is a valid alphanumeric or underscore character.
    Args:
      c (str): The character to check.
    Returns:
      bool: True if the character is valid, False otherwise.
    """
    if c.isalnum():
      return True
    if c in "_":
      return True
    return False

  @staticmethod
  def parse_path_parameter(item: str) -> list:
    """
    Parse a single path parameter from the given item string.
    Args:
      item (str): The item string to parse.
    Returns:
      list: A list containing the converter and parameter name.
    Raises:
      ValueError: If there are invalid characters or formats in the path parameter.
    """
    if not item:
      return [None, None]
    item = item.strip()
    if item.startswith("{") and item.endswith("}"):
      parameter = item[1:-1].strip()
      if not parameter:
        raise ValueError("Empty path parameter")
      for c in parameter:
        if not BaseParser.is_varchar(c):
          raise ValueError(f"Invalid character '{c}' in path parameter: '{parameter}'")
      return [None, parameter]
    if item.startswith("<") and item.endswith(">"):
      item = item[1:-1].strip()
      parameter = ""
      while item and BaseParser.is_varchar(item[-1]):
        parameter = item[-1] + parameter
        item = item[:-1]
      if not parameter:
        raise ValueError("Empty path parameter")
      item = item.strip()
      if not item:
        return [None, parameter]
      if not item.endswith(":"):
        raise ValueError(f"Invalid path parameter format: '{item}:{parameter}'")
      item = item[:-1].strip()
      converter = item
      return [converter, parameter]
    return [None, None]

  @staticmethod
  def parse_path_parameters(endpoint: str) -> dict:
    """
    Parse path parameters from the endpoint string.
    Args:
      endpoint (str): The endpoint string to parse.
    Returns:
      dict: A dictionary of path parameters with their details.
    Raises:
      ValueError: If there are invalid converters or duplicate parameters.
    """
    path_parameters: dict = {}
    for item in endpoint.split("/"):
      [converter, parameter] = BaseParser.parse_path_parameter( item )
      if not parameter:
        continue
      if not converter:
        converter = None
      elif converter in ["int"]:
        converter = int
      elif converter in ["str"]:
        converter = str
      else:
        raise ValueError(
          f"Invalid converter: '{converter}' in request path: '{endpoint}'"
        )
      if (parameter in path_parameters):
        raise ValueError(
          f"Duplicate path parameter: '{parameter}' in request path: '{endpoint}'"
        )
      path_parameters[parameter] = {
        "name"      : parameter,
        "type"      : "PathParameter",
        "converter" : converter,
      }
    return path_parameters

  @staticmethod
  def get_query_strings(endpoint: str) -> str:
    """
    Extract query strings from the endpoint string.
    Args:
      endpoint (str): The endpoint string to extract query strings from.
    Returns:
      str: The extracted query strings.
    Raises:
      ValueError: If there are invalid characters in the endpoint.
    """
    splited_endpoint = endpoint.split("/")
    query_start      = 0
    while query_start < len(splited_endpoint):
      item = splited_endpoint[query_start]
      [_, parameter] = BaseParser.parse_path_parameter( item )
      if (not parameter) and ("?" in item):
        break
      query_start += 1
    if query_start >= len(splited_endpoint):
      return ""
    qstrings = "/".join(splited_endpoint[query_start:]).lstrip("/")
    qstrings = qstrings[qstrings.index("?") + 1:]
    return qstrings

  @staticmethod
  def parse_query_parameters(endpoint: str) -> dict:
    qstrings = BaseParser.get_query_strings(endpoint).split("#")[0]
    if not qstrings:
      return {}
    query_parameters: dict = {}
    for item in qstrings.split("&"):
      item = item.strip()
      query_name = ""
      while item and BaseParser.is_varchar(item[0]):
        query_name += item[0]
        item = item[1:]
      item = item.strip()
      if query_name and item.startswith("="):
        item = item[1:]
      [converter, argument] = BaseParser.parse_path_parameter( item )
      if not query_name:
        query_name = argument
      if not argument:
        raise ValueError(f"Invalid query parameter in request path: '{endpoint}', item: '{item}'")
      query_parameters[argument] = {
        "name"      : argument,
        "query"     : query_name,
        "type"      : "QueryParameter",
        "converter" : converter,
      }
    return query_parameters

  @staticmethod
  def parse_parameters(endpoint: str):
    """
    Parse parameters from the endpoint string.
    Args:
      endpoint (str): The endpoint string to parse.
    Returns:
      dict: A dictionary of parameters with their details.
    Raises:
      ValueError: If there are duplicate parameter names in path and query parameters.
    """
    path_parameters  = BaseParser.parse_path_parameters(endpoint)
    query_parameters = BaseParser.parse_query_parameters(endpoint)
    for pparam in path_parameters:
      if pparam in query_parameters:
        raise ValueError(
          f"Duplicate parameter name '{pparam}' in path and query parameters"
        )
    # merge path parameters into query parameters
    parameters: dict = { **path_parameters, **query_parameters }
    return parameters





  @staticmethod
  def nospaces(s: str):
    for c in ["\r", "\n", "\r", "\v", "\f", " "]:
      s = s.replace(c, "")
    return s

  def parse_methods(methods: Any):
    """
    Parse the HTTP methods from the given input.
    :param methods: A string or list of HTTP methods (e.g., "GET, POST, PUT").
    """
    allmethods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD", "TRACE"]
    original_methods = methods
    methods = str(methods).upper()
    for c in "\r\n\r\v\f '\"[](){};,+/|":
      methods = methods.replace(c, " ")
    methods = methods.strip().replace(" OR ", " ")
    while ("  " in methods):
      methods = methods.replace("  ", " ")
    methods = methods.strip().split(" ")

    if "*" in methods:
      """
      If '*' is present, include all HTTP methods.
      """
      methods.extend( allmethods )
      while ("*" in methods):
        methods.remove("*")
    methods = list(set(methods))
    if not methods:
      raise ValueError(
        f"Invalid methods: ( {original_methods} ), valid methods are: " + ", ".join(allmethods)
      )
    _continue = True
    while _continue:
      _continue = False
      for item in methods:
        if not item.startswith("!"):
          continue
        method = item[1:]
        if not (method in allmethods):
          raise ValueError(f"Invalid methods: ( {original_methods} ), valid methods are: " + ", ".join(allmethods))
        while ( item in methods ):
          methods.remove(item)
        while ( method in methods ):
          methods.remove(method)
        _continue = True
        break
    for method in methods:
      if not (method in allmethods):
        raise ValueError(
          f"Invalid methods: ( {original_methods} ), valid methods are: " + ", ".join(allmethods)
        )
    return methods

  @staticmethod
  def parse_path(rule: str):
    rule = str(rule).strip()
    if ("://" in rule[:10]):
      rule   = rule[rule.index("://") + len("://"):].strip("/")
      domain = rule.split("/")[0]
      rule   = rule[len(domain):]
    while ("//" in rule):
      rule = rule.replace("//", "/")
    for c in ["#"]:
      rule = rule.split(c)[0].strip()
    for c in ["\r", "\n", "\r", "\v", "\f", " "]:
      rule = rule.replace(c, "")
    rule = rule.strip("/")
    return "/" + rule

  @staticmethod
  def parse_urlargs(rule: str) -> List[str]:
    """
    Parse URL arguments from the given rule.
    """
    urlargs = {}
    subrule = BaseParser.parse_path(rule)
    while ("<" in subrule):
      subrule = subrule[subrule.index("<"):]
      if not (">" in subrule):
        raise ValueError(
          f"Invalid rule: {rule}, missing '>' in subrule: {subrule}"
        )
      ekey    = subrule[:subrule.index(">") + 1]
      subrule = subrule[subrule.index(">") + len(">"):]
      key     = BaseParser.nospaces(ekey)[1:-1].strip().split(":")[-1]
      if (key in urlargs):
        raise ValueError(
          f"Invalid rule: {rule}, duplicated URL argument: {key} in subrule: {subrule}"
        )
      urlargs[key] = True
    return list(urlargs)
