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
  * File   : tachyons/io/file_reader.py
  * Created: 2025/08/30 22:49:31 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

class FileReader:

    def _parse_path(self, path: str) -> None:
        """
            git-repository://path/to/file
            google-drive://path/to/file
            s3://path/to/file
        """
        scheme = "file://"
        if ("://" in path):
            scheme = path.split("://")[0] + "://"
            path   = path[len(scheme):]
        path = path.strip().replace("\\", "/")
        return [ scheme.lower(), path ]

    def __init__(self, path: str, mode: str = "r") -> None:
        self._mode = mode
        if not (self._mode in ["r", "rb"]):
            raise ValueError(f"Unsupported mode '{self._mode}'. Use 'r' or 'rb'.")
        [self._scheme, self._path] = self._parse_path( path )
    
    def read(self):
        if (self._scheme == "file://"):
            newpath = self._path
            with open(newpath, self._mode) as fp:
                return fp.read()
        raise NotImplementedError(f"Scheme '{self._scheme}' is not supported yet.")
