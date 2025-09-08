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
  * File   : tachyons/routers/django.py
  * Created: 2025/08/30 22:49:57 GMT+1
  * Updated: 2025/09/05 16:39:22 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import re
import logging
from typing                    import Any, List, Dict
from tachyons.settings         import TachyonsSettings
from tachyons.exceptions.http  import TachyonsHTTPError
from tachyons.exceptions.http  import isHTTPException
from tachyons.exceptions.http  import asHTTPException
from tachyons.routers.base     import BaseRouter
from tachyons.response         import JsonResponse
from tachyons.response         import Json400Response
from tachyons.response         import Json403Response
from tachyons.response         import Json404Response
from tachyons.response         import Json500Response
from django.conf               import urls as django_urls

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class DjangoRouter:

  @staticmethod
  def parse_arguments(
      request        : Any,
      url_pattern    : str,
      headers        : Any,
      handler        : Any,
      *args,  
      **kwargs
  ):

    query_parameters = {}
    for key, value in request.GET.items():
      query_parameters[key] = {
        "name" : key,
        "value": value,
        "type" : None
      }

    arguments = BaseRouter.create_arguments(
		request_path     = request.path,
		url_pattern      = url_pattern,
		query_params     = request.GET.dict(),
		headers          = headers,
		cookies          = request.COOKIES,
		body_content     = request.body,
		handler          = handler,
		django_request   = request,
		query_parameters = query_parameters,
    )
    return arguments

  @staticmethod
  def add(rule: str, handler, response_dto = None, django_request = None):
    from django.urls import path as djpath, re_path as djre_path
    from django.views.decorators.csrf import csrf_exempt
    @csrf_exempt
    def callback(request, *args, **kwargs):
      method  = str(request.method).upper().strip()

      try:
        handler = BaseRouter.get_registered_endpoint_handler(method, rule)
      except TachyonsHTTPError as e:
        return JsonResponse(
          {
            "success": False,
            "status" : e.status,
            "message": e.message,
            "error"  : e.message,
          },
          status = e.status
        )

      try:
        handler_arguments = DjangoRouter.parse_arguments(
          request,
          url_pattern = rule,
          headers = request.headers,
          handler = handler,
          django_request = django_request,
          *args,
          **kwargs
        )
      except Exception as e:
        logger.error(f"Error parsing arguments: {e}")
        if isHTTPException(e):
          return JsonResponse(
            {
              "success": False,
              "status" : e.status,
              "message": e.message,
              "error"  : e.message,
            },
            status = e.status
          )
        else:
          return JsonResponse(
            {
              "success": False,
              "status" : 400,
              "message": "Bad Request",
              "error"  : "Bad Request",
            },
            status = 400
          )

      try:
        result = handler(**handler_arguments)
      except Exception as e:
        hexp = asHTTPException(e)
        if hexp:
          return JsonResponse(
            {
              "success": False,
              "status" : hexp.status,
              "message": hexp.message,
              "error"  : hexp.message,
            },
            status = hexp.status
          )
        else:
          logger.error(f"Internal Server Error: {e}")
          return JsonResponse(
            {
              "success": False,
              "status" : 500,
              "message": "Internal Server Error",
              "error"  : "Internal Server Error",
            },
            status = 500
          )
  
      if response_dto:
        try:
          result = response_dto(result)
          if result is None:
            raise ValueError("Response DTO returned None")
        except Exception as e:
          return JsonResponse(
            {
              "success": False,
              "status" : 500,
              "message": "Error in Response DTO, eREF=#e15645f",
              "error"  : "Error in Response DTO, eREF=#e15645f",
            },
            status = 500
          )

      return result
    djrule   = rule
    for c in "?&#":
      djrule = djrule.split(c)[0]
    for item in djrule.split("<"):
      t = "<" + item.split(":")[0] + ":"
      if not (t in ["int", "str", "slug", "uuid", "path"]):
        djrule = djrule.replace(t, "<str:")
    djrule = djrule.strip("/")
    escaped  = re.escape(djrule)
    # pattern  = rf"^{escaped}(?:/(?P<subpath>.*))?$"
    TachyonsSettings.add_django_urlpatterns(
      [
        djpath(djrule    , callback),
        # djre_path(pattern, callback),
      ]
    )
  @staticmethod
  def handler404(request, exception):
    # app = TachyonsSettings.get_base_app()
    # return JsonResponse(
    # 	{
    # 		"success": False,
    # 		"status" : 500,
    # 		"message": str(request.path),
    # 		"error"  : str(app),
    # 	},
    # 	status = 500
    # )
    
    return Json404Response()

django_urls.handler400 = lambda request, exception: Json400Response()
django_urls.handler403 = lambda request, exception: Json403Response()
django_urls.handler404 = DjangoRouter.handler404
django_urls.handler500 = lambda request           : Json500Response()
