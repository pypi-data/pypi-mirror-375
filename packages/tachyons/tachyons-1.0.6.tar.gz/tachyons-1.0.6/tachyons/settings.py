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
  * File   : tachyons/settings.py
  * Created: 2025/08/30 22:46:53 GMT+1
  * Updated: 2025/09/05 16:08:38 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import os

class TachyonsSettings:
    """
    TachyonsSettings class to manage global settings for the Tachyons library.
    This class provides methods to set and get configuration options that
    can be used across different parts of the library.
    Example usage:
        TachyonsSettings.set_base_app(app)
        app = TachyonsSettings.get_base_app()
    """
    __settings__ = {
        "django": {
            "urlpatterns": []
        },
        "tachyons": {
            "base_app"   : None,
            "base_engine": None,
            "endpoints"  : {},
            "openapi"    : {}
        }
    }
    @classmethod
    def set_base_app(cls, app):
        """
        Set the base application instance.
        Args:
            app: The base application instance to be set.
        """
        cls.__settings__["tachyons"]["base_app"] = app

    @classmethod
    def get_base_app(cls):
        """
        Get the base application instance.
        Returns:
            The base application instance if set, otherwise None.
        """
        base_app = cls.__settings__["tachyons"]["base_app"]
        if not base_app:
            if os.getenv("DJANGO_SETTINGS_MODULE"):
                return None
            raise RuntimeError("Base app is not set.")
        return base_app

    @classmethod
    def set_base_engine(cls, engine):
        """
        Set the base template engine instance.
        Args:
            engine: The base template engine instance to be set.
        """
        cls.__settings__["tachyons"]["base_engine"] = engine
    
    @classmethod
    def get_base_engine(cls):
        """
        Get the base template engine instance.
        Returns:
            The base template engine instance if set, otherwise None.
        """
        base_engine = cls.__settings__["tachyons"]["base_engine"]
        if not base_engine:
            if os.getenv("DJANGO_SETTINGS_MODULE"):
                return "django"
            raise RuntimeError("Base engine is not set.")
        return base_engine

    @classmethod
    def get_django_urlpatterns(cls):
        """
        Get the Django urlpatterns list.
        Returns:
            The Django urlpatterns list.
        """
        return cls.__settings__["django"]["urlpatterns"]

    @classmethod
    def add_django_urlpatterns(cls, patterns):
        """
        Add patterns to the Django urlpatterns list.
        Args:
            patterns: A list of URL patterns to be added.
        """
        if not isinstance(patterns, list):
            raise TypeError("Patterns must be a list.")
        cls.__settings__["django"]["urlpatterns"].extend(patterns)
