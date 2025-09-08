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
  * File   : tachyons/databases/__init__.py
  * Created: 2025/08/30 22:48:11 GMT+1
  * Updated: 2025/09/02 11:53:22 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import uuid
import datetime

class TachyonsDatabaseBASE:
    """
    Base class for tachyons Database validators.
    """

    def __init__(self, *args, **kwargs):
        pass

    def NOW(self):
        """
        Returns the current UTC time in ISO 8601 format with 'Z' suffix.
        """
        return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

    def GENERATE_UNIQUE_ID(self, table_name, size = 1024):
        """
        Generates a unique ID for a new document in the specified collection.
        """
        charset   = str(uuid.uuid4()) + "w" + str(self.NOW())
        unique_id = "".join(c for c in charset if c.isalnum())
        return (("u" + table_name + unique_id).lower())[:size]

    def GET(self, table_name: str, identifier: str) -> dict:
        """
        Retrieves a document from the specified collection by its identifier.
        :param table_name: The name of the collection.
        :param identifier: The unique identifier of the document.
        :return: The document data as a dictionary, or None if not found.
        :rtype: dict
        """
        raise NotImplementedError("GET method must be implemented in the subclass.")

    def PUT(self, data: dict, table_name: str, identifier: str) -> bool:
        """
        Stores a document in the specified collection.
        :param data: The document data to store.
        :param table_name: The name of the collection.
        :param identifier: The unique identifier for the document.
        :return: True if the document was stored successfully, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError("PUT method must be implemented in the subclass.")

    def EXISTS(self, table_name: str, identifier: str) -> bool:
        """
        Checks if a document exists in the specified collection.
        """
        raise NotImplementedError("EXISTS method must be implemented in the subclass.")

    def DELETE(self, table_name: str, identifier: str) -> bool:
        """
        Deletes a document from the specified collection.
        """
        raise NotImplementedError("DELETE method must be implemented in the subclass.")

    def UPDATE(self, table_name: str, document_id: str, data: dict) -> bool:
        """
        Updates a document in the specified collection with the given data.
        """
        odata = self.GET(table_name, document_id)
        if not odata:
            odata = {}
        for key, value in data.items():
            odata[key] = value
        return self.PUT(odata, table_name, document_id)
