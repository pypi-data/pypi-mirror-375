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
  * File   : tachyons/encryption.py
  * Created: 2025/08/30 22:47:26 GMT+1
  * Updated: 2025/08/30 23:45:27 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

# File: tachyons/encryption.py

import json
import base64
from Crypto.Cipher import AES

def check_secret(secret: str):
    """
    Validates the provided secret string based on specific criteria.
    Args:
        secret (str): The secret string to be validated.
    Raises:
        ValueError: If the secret does not meet the required criteria.
    """
    if not isinstance(secret, str):
        raise ValueError("Invalid argument: secret must be a string.")
    if not secret.startswith("@Sk_"):
        raise ValueError("Invalid argument: secret must start with '@Sk_'.")
    if len(secret) != 16:
        raise ValueError(f"Secret must be exactly 16 characters long.")
    _digits   = 0
    _uppers   = 0
    _lowers   = 0
    _specials = 0
    for c in secret:
        if not c.isprintable():
            raise ValueError("Secret must contain only printable ASCII characters.")
        if c.isdigit():
            _digits += 1
        elif c.isupper():
            _uppers += 1
        elif c.islower():
            _lowers += 1
        else:
            _specials += 1
    if _digits < 1:
        raise ValueError(f"Secret must contain at least 1 digit(s).")
    if _uppers < 2:
        raise ValueError(f"Secret must contain at least 2 uppercase letter(s).")
    if _lowers < 2:
        raise ValueError(f"Secret must contain at least 2 lowercase letter(s).")
    if _specials < 3:
        raise ValueError(f"Secret must contain at least 3 special character(s).")

def encrypt(data: str, secret: str, ivsecret: str) -> str:
    """
    Encrypts a string using AES-128 encryption in CBC mode.
    Args:
        data (str): The plaintext data to be encrypted.
        secret (str): The encryption key (must be 16 characters long).
        ivsecret (str): The initialization vector (must be 16 characters long).
    Returns:
        str: The encrypted data.
    Raises:
        ValueError: If the secret or ivsecret is not exactly 16 characters long,
                    or if the data is not a string.
    """
    check_secret(secret)
    check_secret(ivsecret)
    if not isinstance(data, str):
        raise ValueError("Invalid argument: data must be a string.")
    if secret == ivsecret:
        raise ValueError("Secret and ivsecret must be different.")
    secret           = secret.encode('utf-8')
    ivsecret         = ivsecret.encode('utf-8')
    pad_len          = AES.block_size - (len(data) % AES.block_size)
    padded_input     = data + chr(pad_len) * pad_len
    cipher           = AES.new(secret, AES.MODE_CBC, ivsecret)
    encrypted_output = cipher.encrypt(padded_input.encode('utf-8'))
    encoded_output   = base64.urlsafe_b64encode(encrypted_output).decode('utf-8').rstrip("=")
    return encoded_output

def decrypt(input: str, secret: str, ivsecret: str) -> dict:
    """
    Decrypts a encrypted string using AES-128 encryption in CBC mode.
    Args:
        input (str): The encrypted data to be decrypted.
        secret (str): The decryption key (must be 16 characters long).
        ivsecret (str): The initialization vector (must be 16 characters long).
    Returns:
        str: The decrypted plaintext data.
    Raises:
        ValueError: If the secret or ivsecret is not exactly 16 characters long,
                    or if the input is not a string.
    """
    secret           = secret.encode('utf-8')
    ivsecret         = ivsecret.encode('utf-8')
    cipher           = AES.new(secret, AES.MODE_CBC, ivsecret)
    padding_needed   = (4 - len(input) % 4) % 4
    encoded_input    = input + "=" * padding_needed
    encrypted_data   = base64.urlsafe_b64decode(encoded_input)
    decrypted_data   = cipher.decrypt( encrypted_data )
    pad_len          = decrypted_data[-1]
    pad_len = decrypted_data[-1]
    if pad_len < 1 or pad_len > AES.block_size:
        raise ValueError("Invalid padding detected")
    decrypted_string = decrypted_data[:-pad_len].decode('utf-8')
    return decrypted_string

def jencrypt(data: dict, secret: str, ivsecret: str):
    """
    Serializes a dictionary to JSON and encrypts it using AES-128 encryption in CBC mode.
    Args:
        data (dict): The dictionary to be serialized and encrypted.
        secret (str): The encryption key (must be 16 characters long).
        ivsecret (str): The initialization vector (must be 16 characters long).
    Returns:
        str: The encrypted data.
    Raises:
        ValueError: If the data is not a dictionary or is empty.
    """
    if not isinstance(data, dict):
        raise ValueError("Invalid argument: data must be a dictionary.")
    if not data:
        raise ValueError("Invalid argument: data dictionary cannot be empty.")
    sdata = json.dumps(data)
    return encrypt(data = sdata, secret = secret, ivsecret = ivsecret)

def jdecrypt(input: str, secret: str, ivsecret: str) -> dict:
    """
    Decrypts an encrypted string and deserializes it from JSON to a dictionary.
    Args:
        input (str): The encrypted data to be decrypted.
        secret (str): The decryption key (must be 16 characters long).
        ivsecret (str): The initialization vector (must be 16 characters long).
    Returns:
        dict: The decrypted dictionary.
    Raises:
        ValueError: If the decrypted data is not valid JSON.
    """
    decrypted_string = decrypt(
        input    = input,
        secret   = secret,
        ivsecret = ivsecret
    )
    try:
        return json.loads(decrypted_string)
    except json.JSONDecodeError:
        raise ValueError("Decrypted data is not valid JSON.")
    return None
