# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"
          ]  # the current scope is for read and write
TOKEN_PATH = "credentials/token.json"
CREDENTIALS_PATH = "credentials/credentials.json"


class APIConnector:

    def __enter__(self):
        credentials = self._load_credentials()
        service = self._build_service(credentials)
        return service

    def __exit__(self, type, value, traceback):  # noqa
        pass

    def _load_credentials(self):
        if os.path.exists(TOKEN_PATH):
            credentials = Credentials.from_authorized_user_file(
                TOKEN_PATH, SCOPES)
        else:
            credentials = self._get_credentials_from_user()

        if not credentials.valid and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        return credentials

    @staticmethod
    def _get_credentials_from_user():
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH, SCOPES)
        credentials = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(credentials.to_json())
        return credentials

    @staticmethod
    def _build_service(credentials):
        try:
            service = build("calendar", "v3", credentials=credentials)
            return service
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
