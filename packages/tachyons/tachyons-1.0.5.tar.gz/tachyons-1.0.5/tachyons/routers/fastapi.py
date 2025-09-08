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
  * File   : tachyons/routers/fastapi.py
  * Created: 2025/08/30 22:50:00 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import uuid
from typing import Any

class FastAPIRouter:

	@staticmethod
	def add():
			# print (handler.__doc__)
	      import fastapi
	      app = baseapp if isinstance(baseapp, fastapi.FastAPI) else fastapi.FastAPI()
	      def callback(request: fastapi.Request):
	        handlerargs = {

	        }
	        if body:
	          if (body["type"] in [dict, Dict]):
	            body_instance: dict = asyncio.run(request.json())
	          else:
	          # print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", body["type"])
	          # if isinstance(body["type"], TachyonsBaseForm):
	            data: bytes = asyncio.run(request.body())
	            try:
	              body_instance = body["type"](byte_data = data)
	            except ValueError as e:
	              return JsonResponse(
	                {
	                  "sucess" : False,
	                  "status" : 400,
	                  "message": str(e),
	                  "error"  : str(e),
	                },
	                status = 400
	              )

	          handlerargs[ body["name"] ] = body_instance
	        for func_argname, func_argvalue in funcargs.items():
	          func_argtype = func_argvalue.annotation
	          if (func_argtype == TachyonsRequestCookie) or (isinstance(func_argtype, TachyonsRequestCookie)):
	            for cookie_name, cookie_value in request.cookies.items():
	              if func_argname == cookie_name:
	                handlerargs[cookie_name] = cookie_value
	        return handler(**handlerargs)
	      callback.__name__ = handler.__name__
	      callback.__doc__  = handler.__doc__
	      if json_responses:
	        for status, response in json_responses.items():
	          responses[status] = {
	            "description": response.get("description", ""),
	            "content": {
	              "application/json": {
	                "example": response.get("example", {})
	              }
	            }
	          }
	      app.add_api_route(
	        rule,
	        callback,
	        methods              = methods,
	        name                 = handler.__name__,
	        tags                 = [handler.__name__],
	        responses            = responses,
	        summary              = summary,
	        description          = description,
	        response_description = response_description,
	      )
