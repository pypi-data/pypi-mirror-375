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
  * File   : tachyons/djproxy.py
  * Created: 2025/08/30 22:47:23 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

# File: @tachyons/djproxy.py

"""
    Django Proxy Router
    This module provides a utility function to create Django URL patterns
    that route requests to a specified endpoint, handling both exact matches
    and subpaths.
"""

import re
from django.urls import path, re_path

def djroute(endpoint: str, callback):
    """
    Creates Django URL patterns for a given endpoint and callback.
    This function generates two URL patterns:
    1. An exact match for the endpoint.
    2. A regex pattern that matches the endpoint and captures any subpath.
    The regex pattern captures the subpath as a named group 'subpath'.
    Args:
        endpoint (str): The endpoint URL to route.
        callback: The view or callable that handles requests to this endpoint.
    Returns:
        list: A list of Django URL patterns.
    """
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("Endpoint must be a non-empty string.")
    endpoint = endpoint.strip().rstrip("/")
    escaped  = re.escape(endpoint)
    pattern  = rf"^{escaped}(?:/(?P<subpath>.*))?$"
    return [
        path(endpoint  , callback),
        re_path(pattern, callback),
    ]
