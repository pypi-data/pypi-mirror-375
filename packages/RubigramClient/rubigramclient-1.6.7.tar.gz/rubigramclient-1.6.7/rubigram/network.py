from aiohttp import ClientSession, FormData
from typing import Any, Optional, Union
from pathlib import Path
from urllib.parse import urlparse
import aiofiles
import os


class Network:
    def __init__(self, token: str) -> None:
        self.token: str = token
        self.session: Optional[ClientSession] = None
        self.api: str = f"https://botapi.rubika.ir/v3/{token}/"

    async def start(self):
        if not self.session:
            self.session = ClientSession()

    async def stop(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def request(self, method: str, json: dict[str, Any]):
        await self.start()
        async with self.session.post(self.api + method, json=json) as response:
            response.raise_for_status()
            data: dict = await response.json()
            return data.get("data")

    async def getBytes(self, url: str) -> bytes:
        await self.start()
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.read()

    async def getName(self, url: str) -> str:
        parser = urlparse(url)
        return os.path.basename(parser.path)

    async def requestUpload(self, upload_url: str, file: Union[str, bytes], name: Optional[str] = None):
        data, filename = None, None
        if isinstance(file, str):
            path = Path(file)

            if path.is_file():
                data, filename = path.read_bytes(), name if name else path.name

            elif file.startswith("http"):
                data, filename = await self.getBytes(file), name if name else await self.getName(file)

            else:
                raise Exception(f"Can't find this file : {file}")

        elif isinstance(file, bytes):
            if name:
                data, filename = file, name
            else:
                raise Exception("choice name for bytes file")
        
        form = FormData()
        form.add_field("file", data, filename=filename, content_type="application/octet-stream")
        await self.start()
        async with self.session.post(upload_url, data=form) as response:
            response.raise_for_status()
            data: dict = await response.json()
            return data.get("data", {})["file_id"]

    async def requestDownload(self, url: str, filename: Optional[str] = None):
        file, name = await self.getBytes(url), filename if filename else await self.getName(url)
        async with aiofiles.open(name, "wb") as f:
            await f.write(file)
            return name