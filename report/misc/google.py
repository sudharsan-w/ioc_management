import os
import csv
from io import BytesIO

# import os.path
from enum import Enum
from dataclasses import dataclass

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


class Scope(Enum):
    GoogleDrive = "https://www.googleapis.com/auth/drive"
    GoogleSheets = "https://www.googleapis.com/auth/spreadsheets"


class Role(Enum):
    Writer = "writer"
    Owner = "owner"
    Viewer = "reader"


@dataclass
class GoogleConn:
    credentials_path: str
    scopes: list[Scope]

    def __get_scopes(self) -> list[str]:
        return [scope.value for scope in self.scopes]

    def get_creds(self) -> service_account.Credentials:
        return service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.__get_scopes()
        )


@dataclass
class GoogleSheet:
    id: str
    path: str


@dataclass
class LocalFile:
    file_path: str
    display_name: str
    mime_type: str = "*/*"


@dataclass
class GoogleDriveFile:
    id: str
    name: str
    parent_id: str


@dataclass
class GoogleDriveFolder:
    id: str
    name: str
    parent_id: str


class GoogleSheets:
    def __init__(
        self,
        google_conn: GoogleConn,
    ) -> None:
        self.google_conn = google_conn

    def __build_service(self):
        return build("sheets", "v4", credentials=self.google_conn.get_creds())

    def __build_drive_service(self):
        return build("drive", "v3", credentials=self.google_conn.get_creds())

    def is_accessible(self, sheet: GoogleSheet):
        try:
            service = self.__build_service()
            service.spreadsheets().values().get(
                spreadsheetId=sheet.id, range="A1:A2"
            ).execute()
            return True
        except:
            return False

    def __get_sheets(self, sheet: GoogleSheet):
        service = self.__build_service()
        spreadsheet = service.spreadsheets().get(spreadsheetId=sheet.id).execute()
        return spreadsheet.get("sheets", [])

    def create_sheet(self, title) -> GoogleSheet:
        service = self.__build_service()
        spreadsheet = {
            "properties": {"title": title},
            "sheets": [{"properties": {"title": title}}],
        }
        sheet = (
            service.spreadsheets()
            .create(body=spreadsheet, fields="spreadsheetId")
            .execute()
        )
        g_sheet = GoogleSheet(id=sheet.get("spreadsheetId"))
        return g_sheet

    def write_content(self, sheet: GoogleSheet, data: list[list]):
        service = self.__build_service()
        if not self.is_accessible(sheet):
            e = f"{sheet} not accessible"
            raise Exception(e)
        res = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=sheet.id,
                range="A1",
                valueInputOption="USER_ENTERED",
                body={"values": data},
            )
            .execute()
        )
        return res

    def get_no_of_rows(self, sheet: GoogleSheet) -> int:
        # sheet_name = "Sheet1"
        sheets = self.__get_sheets(sheet=sheet)
        sheet_ = sheets[0]
        sheet_name = sheet_.get("properties", {}).get("title", "Sheet1")
        service = self.__build_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet.id, range=sheet_name)
            .execute()
        )
        values = result.get("values", [])
        num_rows = len(values)
        if num_rows == 0:
            return 0
        end_row = num_rows
        return end_row

    def append_rows(self, sheet: GoogleSheet, data: list[list]):
        service = self.__build_service()
        sheets = self.__get_sheets(sheet=sheet)
        sheet_ = sheets[0]
        sheet_name = sheet_.get("properties", {}).get("title", "Sheet1")
        service = self.__build_service()
        if not self.is_accessible(sheet):
            e = f"{sheet} not accessible"
            raise Exception(e)
        tot_rows = self.get_no_of_rows(sheet=sheet)
        print(f"{sheet_name}!A{tot_rows+1}")
        res = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=sheet.id,
                range=f"{sheet_name}!A{tot_rows+1}",
                valueInputOption="USER_ENTERED",
                body={"values": data},
            )
            .execute()
        )
        return res

    def share_access(self, sheet: GoogleSheet, email: str, role: Role):
        drive_service = self.__build_drive_service()
        drive_service.permissions().create(
            fileId=sheet.id,
            body={
                "type": "user",
                "role": role.value,
                "emailAddress": email,
            },
            fields="id",
        ).execute()


class GoogleDrive:
    def __init__(
        self,
        google_conn: GoogleConn,
    ) -> None:
        self._google_conn = google_conn

    def __build_service(self):
        return build("drive", "v3", credentials=self._google_conn.get_creds())

    def upload_file(self, file: LocalFile) -> GoogleDriveFile:
        service = self.__build_service()
        file_metadata = {"name": file.display_name}
        media = MediaFileUpload(
            file.file_path,
            mimetype=file.mime_type,
        )
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, name, parents")
            .execute()
        )
        parent_id = None
        if file.get("parents", None):
            parent_id = file.get("parents", [None])[0]
        return GoogleDriveFile(
            id=file.get("id"), name=file.get("name"), parent_id=parent_id
        )

    def upload_file_chunks(self, file: LocalFile) -> GoogleDriveFile:
        service = self.__build_service()
        media = MediaFileUpload(
            file.file_path, resumable=True, chunksize=1024 * 1024 * 10
        )  # 10 MB chunks
        file_metadata = {"name": file.display_name}
        request = service.files().create(
            body=file_metadata, media_body=media, fields="id, name, parents"
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%.")
        if response.get("parents", None):
            parent_id = response.get("parents", [None])[0]
        return GoogleDriveFile(
            id=response.get("id"), name=response.get("name"), parent_id=parent_id
        )

    def delete_file(self, file_id):
        service = self.__build_service()
        service.files().delete(fileId=file_id).execute()
        return True

    def download_file(self, file: GoogleDriveFile, out_file: LocalFile):
        service = self.__build_service()
        request = service.files().get_media(fileId=file.id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download Progress: {int(status.progress() * 100)}%")
        fh.seek(0)
        with open(out_file.file_path, "wb") as f:
            f.write(fh.read())
            f.close()
        return out_file

    def share_access(self, file: GoogleDriveFile, email: str, role: Role):
        service = self.__build_service()
        service.permissions().create(
            fileId=file.id,
            body={
                "type": "user",
                "role": role.value,
                "emailAddress": email,
            },
            fields="id",
        ).execute()

    def list_folders(self):
        service = self.__build_service()
        query = f"mimeType = 'application/vnd.google-apps.folder'"
        drive_folders = []
        results = (
            service.files()
            .list(q=query, spaces="drive", fields="files(id, name, parents)")
            .execute()
        )
        folders = results.get("files", [])
        for folder in folders:
            drive_folders.append(
                GoogleDriveFolder(
                    id=folder["id"],
                    name=folder["name"],
                    parent_id=folder["parents"][0],
                )
            )
        return drive_folders

    def list_files(self):
        service = self.__build_service()
        page_token = None
        drive_files = []
        while True:
            results = (
                service.files()
                .list(
                    spaces="drive",
                    fields="nextPageToken, files(id, name, parents)",
                    pageToken=page_token,
                )
                .execute()
            )
            files = results.get("files", [])

            if not files:
                break

            for file in files:
                drive_files.append(
                    GoogleDriveFile(
                        id=file["id"], name=file["name"], parent_id=file["parents"][0]
                    )
                )

            page_token = results.get("nextPageToken", None)
            if not page_token:
                break
        return drive_files

    def about_account(self) -> dict:
        service = self.__build_service()
        about = service.about().get(fields="*").execute()
        return about
