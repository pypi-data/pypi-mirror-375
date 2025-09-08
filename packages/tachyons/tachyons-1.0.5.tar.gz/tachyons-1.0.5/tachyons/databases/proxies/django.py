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
  * File   : tachyons/databases/proxies/django.py
  * Created: 2025/09/02 11:56:23 GMT+1
  * Updated: 2025/09/02 14:18:58 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

from typing                 import Any, Type, Union
from django.db.models       import Model as DjangoModel
from django.core.exceptions import ValidationError as DjangoValidationError

def safe_isinstance(obj: Any, class_or_tuple: Any) -> bool:
	"""
	Safely checks if an object is an instance of a class or a tuple of classes.
	Args:
		obj (Any): The object to check.
		class_or_tuple (Any): A class or a tuple of classes to check against.
	Returns:
		bool: True if obj is an instance of class_or_tuple, False otherwise.
	"""
	try:
		return isinstance(obj, class_or_tuple)
	except Exception:
		pass
	return False

def safe_issubclass(cls: Any, class_or_tuple: Any) -> bool:
	"""
	Safely checks if a class is a subclass of another class or a tuple of classes.
	Args:
		cls (Any): The class to check.
		class_or_tuple (Any): A class or a tuple of classes to check against.
	Returns:
		bool: True if cls is a subclass of class_or_tuple, False otherwise.
	"""
	try:
		return issubclass(cls, class_or_tuple)
	except Exception:
		pass
	return False

class DjangoOrmProxy:
	"""Proxy layer for interacting with Django ORM in a safe, dependency-injected way."""

	@staticmethod
	def to_dj_model(model: Any) -> Type[DjangoModel]:
		"""
		Normalize input into a Django model class.

		Args:
			model (Any): A model class, instance, or identifier.

		Returns:
			Type[DjangoModel]: A Django model class.

		Raises:
			RuntimeError: If the model is invalid or unsupported.
		"""
		if safe_isinstance(model, str):
			# TODO: Implement dynamic model retrieval by table name or registry.
			raise RuntimeError("String-based model lookup is not yet implemented.")

		if safe_isinstance(model, DjangoModel):
			return model.__class__

		if not safe_issubclass(model, DjangoModel):
			raise RuntimeError(f"Invalid model: {model}")

		return model

	def EXISTS(self, model: Any, **kwargs):
		"""
		Check if a record exists in the database.
		Args:
			model (Any): The Django model class or instance to query.
			**kwargs: Field lookups to filter the query.
		Returns:
			bool: True if a record exists matching the criteria, False otherwise.
		Raises:
			ValueError: If the model is not a valid Django model class or instance.
		"""
		model : DjangoModel = DjangoOrmProxy.to_dj_model(model)
		result: bool        = False

		if not kwargs:
			# TODO: check instance with same fields, is exists
			raise ValueError("No filter criteria provided.")

		try:
			return model.objects.filter(**kwargs).exists()
		except DjangoValidationError as e:
			pass

		return result
	
	def GET(self, model: Any, **kwargs) -> Union[DjangoModel, None]:
		"""
			get first record matching the criteria
		Args:
			model (Any): The Django model class or instance to query.
			**kwargs: Field lookups to filter the query.
		Returns:
			Union[DjangoModel, None]: The first matching record or None if not found.
		Raises:
			ValueError: If the model is not a valid Django model class or instance.
		"""
		model : DjangoModel = DjangoOrmProxy.to_dj_model(model)
		if not kwargs:
			raise ValueError("No filter criteria provided.")
		try:
			result = model.objects.filter(**kwargs).first()
		except DjangoValidationError as e:
			result = None
		return result
