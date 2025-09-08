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
  * File   : tachyons/integrations/aws/s3.py
  * Created: 2025/08/30 22:48:45 GMT+1
  * Updated: 2025/08/31 21:13:13 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import os
import io
import uuid
import logging
from typing import Optional, Union, BinaryIO

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


class TachyonsAwsS3Client:
    """
    A lightweight AWS S3 client wrapper for Tachyons integrations.

    Features:
    - Environment variable fallback for credentials.
    - Upload, delete, and URI-based operations.
    - Minimal error handling with logging.
    """

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ) -> None:
        aws_access_key_id = aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        region_name = region_name or os.environ.get("AWS_REGION")

        if not (aws_access_key_id and aws_secret_access_key and region_name):
            raise ValueError("Missing AWS credentials or region. Provide explicitly or via environment variables.")

        try:
            self._s3client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
            )
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def upload_fileobj(
        self,
        fobject: Union[BinaryIO, io.BytesIO],
        bucket_name: str,
        object_name: Optional[str] = None,
    ) -> str:
        """
        Uploads a file-like object to S3.

        Args:
            fobject: File-like object (e.g., open file, io.BytesIO).
            bucket_name: Target S3 bucket.
            object_name: Optional S3 key name. Defaults to UUID.

        Returns:
            str: Full `s3://` URI of uploaded object.
        """
        object_name = object_name.strip("/") if object_name else str(uuid.uuid4())

        try:
            self._s3client.upload_fileobj(fobject, bucket_name, object_name)
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Upload failed: bucket={bucket_name}, object={object_name}, error={e}")
            raise

        uri = f"s3://{bucket_name}/{object_name}"
        logger.debug(f"Uploaded to {uri}")
        return uri

    def delete_object(
        self,
        bucket_name: Optional[str] = None,
        object_name: Optional[str] = None,
        uri: Optional[str] = None,
    ) -> bool:
        """
        Deletes an object from S3.

        Args:
            bucket_name: Name of the bucket.
            object_name: Key of the object.
            uri: Full `s3://` URI (alternative to bucket_name+object_name).

        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        if uri:
            if not uri.lower().startswith("s3://"):
                raise ValueError(f"Invalid S3 URI: {uri}")

            parts = uri[5:].split("/", 1)
            if len(parts) != 2:
                raise ValueError(f"Malformed S3 URI: {uri}")
            bucket_name, object_name = parts

        if not bucket_name or not object_name:
            raise ValueError("Both bucket_name and object_name must be provided, or use a valid `uri`.")

        try:
            self._s3client.delete_object(Bucket=bucket_name, Key=object_name)
            logger.debug(f"Deleted s3://{bucket_name}/{object_name}")
            return True
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Delete failed: bucket={bucket_name}, object={object_name}, error={e}")
            return False

    def object_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Checks if an object exists in S3.

        Returns:
            bool: True if object exists, False otherwise.
        """
        try:
            self._s3client.head_object(Bucket=bucket_name, Key=object_name)
            return True
        except self._s3client.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def download_fileobj(
        self, bucket_name: str, object_name: str, fobject: Union[BinaryIO, io.BytesIO]
    ) -> None:
        """
        Downloads an object from S3 into a file-like object.

        Args:
            bucket_name: Source bucket.
            object_name: Key of the object.
            fobject: File-like object to write to.
        """
        try:
            self._s3client.download_fileobj(bucket_name, object_name, fobject)
            logger.debug(f"Downloaded s3://{bucket_name}/{object_name}")
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Download failed: bucket={bucket_name}, object={object_name}, error={e}")
            raise
