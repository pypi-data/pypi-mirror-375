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
  * File   : tachyons/integrations/google/drive.py
  * Created: 2025/08/30 22:48:56 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import os
import io
import mimetypes
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials      import Credentials
from google_auth_oauthlib.flow      import InstalledAppFlow
from googleapiclient.discovery      import build
from googleapiclient.http           import MediaIoBaseUpload, MediaIoBaseDownload, MediaFileUpload

class TachyonsGoogleDrive:

    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
    ]

    def __init__(self, token_path: str, cedentials_path: str):
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, TachyonsGoogleDrive.SCOPES)
        if (not creds) or (not creds.valid):
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cedentials_path, TachyonsGoogleDrive.SCOPES)
                creds = flow.run_local_server(port = 0)
            try:
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            except:
                pass
        self._service = build('drive', 'v3', credentials=creds)

    @staticmethod
    def getFolderIdByUrl(url: str) -> Optional[str]:
        raise NotImplementedError("This method should be implemented to extract folder ID from the URL.")

    @staticmethod
    def getFileIdByUrl(url: str) -> Optional[str]:
        return TachyonsGoogleDrive.getFolderIdByUrl(url)

    def lstdir(self, urlpath: str):
        folder_id = urlpath
        params = {
                "q": f"'{folder_id}' in parents and trashed=false",
                "pageSize": 100,
                "fields": "nextPageToken, files(id, name, mimeType, webViewLink, iconLink, modifiedTime, size)",
                "supportsAllDrives": True,
                "includeItemsFromAllDrives": True,
        }
        response = self._service.files().list(**params).execute()
        return response

    def download_folder(self, url: str, filename: str):
        folder_id = url
        metadata  = self._service.files().get(fileId=folder_id, fields = "name, mimeType").execute()
        if metadata["mimeType"] != "application/vnd.google-apps.folder":
            raise ValueError("Cannot download a file, please use download_file method instead.")
        print ( self.lstdir(url) )
        exit()

    def download_file(self, url: str, filename: str):
        file_id  = url
        metadata = self._service.files().get(fileId=file_id, fields = "name, mimeType").execute()
        if metadata["mimeType"] == "application/vnd.google-apps.folder":
            raise ValueError("Cannot download a folder, please use download_folder method instead.")

        request = self._service.files().get_media(
            fileId = file_id,
        )
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        with open(filename, "wb") as fp:
            fp.write(fh.read())

    def create_folder(self, name: str, parent_id: str = None):
        """
        Create a folder in Google Drive.

        :param name: Name of the folder
        :param parent_id: Optional ID of parent folder
        :return: The created folder's Drive ID
        """

        # Build query to check for existing folder with same name
        query = f"name='{name}' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        results = self._service.files().list(q = query, fields="files(id, name)").execute()
        if results.get('files', []):
            print(f"'{name}' already exists. Folder ID")
            return False

        file_metadata = {
            'name'    : name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        folder = self._service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()

        print(f"Folder '{name}' created successfully. Folder ID: {folder['id']}")
        return folder['id']

    def upload_file(self, filepath: str, folder_id: str = None):
        filename = os.path.basename(filepath)


        file_metadata = {'name': filename}

        if folder_id:
            file_metadata['parents'] = [folder_id]

        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = 'application/octet-stream'

        media = MediaFileUpload(filepath, mimetype=mime_type)

        uploaded_file = self._service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        print(f"Uploaded '{filename}' successfully. File ID: {uploaded_file['id']}")
        return uploaded_file['id']

    def _upload_recursive(self, current_local_folder, parent_id, uploaded = None):
        folder_name = os.path.basename(current_local_folder)
        drive_folder_id = self.create_folder(folder_name, parent_id)
        uploaded[current_local_folder] = drive_folder_id
        for item in os.listdir(current_local_folder):
            local_path = os.path.join(current_local_folder, item)
            if os.path.isdir(local_path):
                self._upload_recursive(local_path, drive_folder_id, uploaded = uploaded)
            else:
                file_id = self.upload_file(local_path, folder_id=drive_folder_id)
                uploaded[local_path] = file_id

    def upload_folder(self, local_folder: str, parent_drive_folder_id: str = None):
        uploaded = {}
        self._upload_recursive(local_folder, parent_drive_folder_id, uploaded = uploaded)
        return uploaded

    def upload_io(self, file_obj: io.IOBase, filename: str, folder_id: str = None):
        """
        Uploads a file to Google Drive from a file-like object.
        
        :param file_obj: A file-like object (e.g., BytesIO)
        :param filename: The name to save the file as on Drive
        :param folder_id: Optional folder ID to upload into
        :return: The uploaded file's Google Drive ID
        """

        # Prepare metadata
        file_metadata = {'name': filename}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        # Guess MIME type based on filename
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream'

        # Create MediaIoBaseUpload from file-like object
        media = MediaIoBaseUpload(file_obj, mimetype=mime_type)

        # Upload
        uploaded_file = self._service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        print(f"Uploaded '{filename}' successfully. File ID: {uploaded_file['id']}")
        return uploaded_file['id']
