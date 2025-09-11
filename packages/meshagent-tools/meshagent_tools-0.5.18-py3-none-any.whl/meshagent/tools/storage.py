from meshagent.api.messaging import JsonResponse, LinkResponse
from .toolkit import Tool, ToolContext
from .hosting import RemoteToolkit
from .blob import BlobStorage, get_bytes_from_url
import os
from meshagent.api import RoomException
from typing import Optional


class ReadFileTool(Tool):
    def __init__(self):
        super().__init__(
            name="read_file",
            title="read text file",
            description="read the contents of a text file (for example a .txt file or a source code file). Will not work with binary files.",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "required": ["path"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "the full path of the file",
                    }
                },
            },
        )

    async def execute(self, *, context: ToolContext, path: str):
        file = await context.room.storage.download(path=path)
        return file.data.decode("utf-8")


class WriteFileTool(Tool):
    def __init__(self):
        super().__init__(
            name="write_file",
            title="write text file",
            description="write the contents of a text file (for example a .txt file or a source code file). Will not work with binary files.",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "required": ["path", "text", "overwrite"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "the full path of the file",
                    },
                    "text": {
                        "type": "string",
                        "description": "the text to write to the file",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "whether to overwrite the current file if it exists at the path",
                    },
                },
            },
        )

    async def execute(
        self, *, context: ToolContext, path: str, text: str, overwrite: bool
    ):
        handle = await context.room.storage.open(path=path, overwrite=overwrite)
        await context.room.storage.write(handle=handle, data=text.encode("utf-8"))
        await context.room.storage.close(handle=handle)
        return "the file was saved"


class GetFileDownloadUrl(Tool):
    def __init__(self):
        super().__init__(
            name="get_file_download_url",
            title="get file download url",
            description="get a url that can be used to download a file in the room",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "required": ["path"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "the full path of the file",
                    }
                },
            },
        )

    async def execute(self, *, context: ToolContext, path: str):
        name = os.path.basename(path)
        url = await context.room.storage.download_url(path=path)
        return LinkResponse(name=name, url=url)


class ListFilesTool(Tool):
    def __init__(self):
        super().__init__(
            name="list_files_in_room",
            title="list files in room",
            description="list the files at a specific path in the room",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "required": ["path"],
                "properties": {"path": {"type": "string"}},
            },
        )

    async def execute(self, *, context: ToolContext, path: str):
        files = await context.room.storage.list(path=path)
        return JsonResponse(json={"files": list(map(vars, files))})


class SaveFileFromUrlTool(Tool):
    def __init__(self, blob_storage: Optional[BlobStorage] = None):
        super().__init__(
            name="save_file_from_url",
            title="save file from url",
            description="save a file from a url to a path in the room",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "required": ["url", "path", "overwrite"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "the url of a file that should be saved to the room",
                    },
                    "path": {
                        "type": "string",
                        "description": "the destination path (including the filename)",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "whether to overwrite the existing file) (default false)",
                    },
                },
            },
        )
        self.blob_storage = blob_storage

    async def execute(
        self, *, context: ToolContext, url: str, path: str, overwrite: bool
    ):
        blob = await get_bytes_from_url(url=url, blob_storage=self.blob_storage)

        if not overwrite:
            result = await context.room.storage.exists(path=path)
            if result:
                raise RoomException(
                    f"a file already exists at the path: {path}, try another filename"
                )

        handle = await context.room.storage.open(path=path, overwrite=overwrite)
        try:
            await context.room.storage.write(handle=handle, data=blob.data)
        finally:
            await context.room.storage.close(handle=handle)


class StorageToolkit(RemoteToolkit):
    def __init__(self, *, blob_storage: Optional[BlobStorage] = None):
        super().__init__(
            name="storage",
            title="storage",
            description="tools for interacting with meshagent room storage",
            tools=[
                ListFilesTool(),
                WriteFileTool(),
                ReadFileTool(),
                GetFileDownloadUrl(),
                SaveFileFromUrlTool(blob_storage=blob_storage),
            ],
        )
