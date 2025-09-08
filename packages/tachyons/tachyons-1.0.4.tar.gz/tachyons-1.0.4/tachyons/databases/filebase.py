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
  * File   : tachyons/databases/filebase.py
  * Created: 2025/08/30 22:48:16 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import os
import json
import shutil
import dotenv
import logging
from tachyons.databases import TachyonsDatabaseBASE
from tachyons.models    import TachyonsBaseModel

dotenv.load_dotenv()

logging.basicConfig(
    level    = logging.INFO,
    format   = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers = [
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FileBase(TachyonsDatabaseBASE):

    def __init__(self, root: str, dest: str):
        self._root    = root
        self._datadir = dest
        os.makedirs(self._datadir, exist_ok = True)

    def GET(self, table_name: str, id: str) -> dict:
        filename = os.path.join(self._datadir, table_name, id, "object.json")
        try:
            with open(filename, "r") as fp:
                data = json.load(fp)
            return data
        except:
            pass
        return {}

    def PUT(self, data, table_name: str = None, id: str = None) -> bool:
        if isinstance(data, TachyonsBaseModel):
            if not table_name:
                table_name = data.__tablename__
            data = data.__json__()
        if not id:
            id = data["id"]
        if not id:
            raise ValueError("ID must be provided for PUT operation.")
        if not table_name:
            raise ValueError("Table name must be provided for PUT operation.")
        data["id"] = id
        filename = os.path.join(self._datadir, table_name, id, "object.json")
        os.makedirs(os.path.dirname(filename), exist_ok = True)
        with open(filename, "w") as fp:
            json.dump(data, fp, indent = 4)
        return True
