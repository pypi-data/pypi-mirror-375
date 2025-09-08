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
  * File   : tachyons/utils/__init__.py
  * Created: 2025/08/30 22:50:12 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import random
import string
import hashlib

def string2id(string: str) -> str:
    """
    Converts a string to a unique identifier using SHA-256 hashing.
    The same input string will always produce the same output.
    """
    return "i" + hashlib.sha256(str(string).encode('utf-8')).hexdigest()

def hashpass(password: str) -> str:
    """
    Hashes a password using SHA-256.
    The same password will always produce the same hash.
    """
    return hashlib.sha256(str(password).encode('utf-8')).hexdigest()

def randcode(code_length: int = 6, characters: str = string.digits) -> str:
    """
    Generates a random verification code consisting of uppercase letters and digits.
    Returns:
        str: A string containing the verification code.
    """
    return ''.join(
        random.choice(characters)
        for _ in range(code_length)
    )
