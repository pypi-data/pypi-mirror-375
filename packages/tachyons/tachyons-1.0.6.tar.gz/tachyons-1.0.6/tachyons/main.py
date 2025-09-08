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
  * File   : tachyons/main.py
  * Created: 2025/08/30 23:04:30 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import os
import sys
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

endpoints = {}

endpoint_template = '''
"""
"""
import tachyons
from tachyons.response import JsonResponse

@route("${endpoint}", methods = "${methods}")
def handler():
	return JsonResponse(
		{
			"success": False,
			"status" : 500,
			"message": "Not implemented yet",
			"error"  : "Not implemented yet",
		},
		status = 500
	)
'''

def add_endpoint(url: str, method: str = "GET"):
	endpoint = url.strip()
	for c in "?&#":
		endpoint = endpoint.split(c)[0]
	if ("://" in endpoint[:10]):
		scheme   = endpoint.split("://")[0] + "://"
		endpoint = endpoint[endpoint.index(scheme) + len(scheme):]
		domain   = endpoint.strip("/").split("/")[0]
		endpoint = endpoint[endpoint.index(domain) + len(domain):]
	else:
		raise ValueError("Invalid URL format")
	endpoints[endpoint] = {
		"url"    : url,
		"methods": method.upper(),
	}

def extract_request(request: Dict[str, Any]):
	if not ("url" in request):
		# logger.error("No URL found in request")
		return
	url = request.get("url", None)
	if (not url) or (not isinstance(url, str)):
		# logger.error("Invalid URL in request")
		return
	add_endpoint(url)

def cycletrough_item(data):
	request = data.get("request", {})
	if isinstance(request, dict):
		extract_request(request)


	item = data.get("item", [])
	for element in item:
		cycletrough_item(element)

class PostmanCollectionImporter:

	def __init__(self, app_path: str):
		self._app_path = app_path

	def endpoint2path(self, endpoint: str) -> str:
		endpoint = endpoint.strip("/").lower()
		for c in "\r\n\t\v\f -_":
			endpoint = endpoint.replace(c, "_")
		while ("__" in endpoint):
			endpoint = endpoint.replace("__", "_")
		return endpoint.strip("_")

	def createfile(self, path: str):
		filename = os.path.join(self._app_path, path.strip("/"))
		dirname  = os.path.dirname(filename)
		os.makedirs(dirname, exist_ok = True)
		with open(filename, 'w') as file:
			file.write("")
		return filename

	def createfiles(self, endpoints: Dict[str, Any]):
		for endpoint, info in endpoints.items():
			subpath  = self.endpoint2path(endpoint)
			endpath  = subpath + ".py"
			initfile = os.path.join(os.path.dirname(endpath), "__init__.py")
			self.createfile(initfile)
			endpoint_filename = self.createfile(endpath)
			with open(endpoint_filename, 'w') as file:
				content = endpoint_template
				content = content.replace("${endpoint}", endpoint)
				content = content.replace("${methods}" , info["methods"])
				file.write( content )

	def loadfile(self, jsonfile: str):
		
		with open(jsonfile, 'r') as file:
			data = json.load(file)

		cycletrough_item(data)

		self.createfiles(endpoints)

def main(argv):
	"""
		tachyons --create-project --template="postman_collection.json"
	"""

if __name__ == "__main__":
	main(sys.argv)
