from .network import Network
from rubigram import enums
from typing import Optional, Union
from rubigram.types import Bot, Chat, Keypad, MessageId, Updates, BotCommand


class Method(Network):
    def __init__(self, token: str):
        super().__init__(token)
        
    def clean_data(self, data: dict):
        return {key: value for key, value in data.items() if value is not None}
        
    async def get_me(self) -> "Bot":
        response = await self.request("getMe", {})
        return Bot.from_dict(response["bot"])

    async def get_chat(self, chat_id: str) -> "Chat":
        response = await self.request("getChat", {"chat_id": chat_id})
        return Chat.from_dict(response["chat"])

    async def get_update(self, limit: int = 1, offset_id: Optional[int] = None) -> "Updates":
        response = await self.request("getUpdates", {"limit": limit, "offset_id": offset_id})
        return Updates.from_dict(response)

    async def get_file(self, file_id: str) -> str:
        response = await self.request("getFile", {"file_id": file_id})
        return response["download_url"]

    async def set_command(self, commands: list[BotCommand]):
        response = await self.request("setCommands", {"bot_commands": [command.asdict() for command in commands]})
        return response

    async def update_bot_endpoint(self, url: str, type: enums.UpdateEndpointType):
        response = await self.request("updateBotEndpoints", {"url": url, "type": type})
        return response

    async def delete_message(self, chat_id: str, message_id: str):
        await self.request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def remove_chat_keypad(self, chat_id: str):
        await self.request("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "Remove"})

    async def edit_chat_keypad(self, chat_id: str, chat_keypad: Keypad):
        await self.request("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "New", "chat_keypad": chat_keypad.asdict()})

    async def edit_message_keypad(self, chat_id: str, message_id: str, inline_keypad: Keypad):
        await self.request("editMessageKeypad", {"chat_id": chat_id, "message_id": message_id, "inline_keypad": inline_keypad.asdict()})

    async def edit_message_text(self, chat_id: str, message_id: str, text: str):
        await self.request("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    async def forward_message(self, from_chat_id: str, message_id: str, to_chat_id: str, disable_notification: bool = False) -> "MessageId":
        data = {"from_chat_id": from_chat_id, "message_id": message_id, "to_chat_id": to_chat_id, "disable_notification": disable_notification}
        response = await self.request("forwardMessage", data)
        message = MessageId.from_dict(response)
        message.chat_id = to_chat_id
        message.client = self
        return message

    async def send_message(
        self,
        chat_id: str,
        text: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = None,
        reply_to_message_id=None
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "text": text,
            "chat_keypad": chat_keypad.asdict() if chat_keypad else None,
            "inline_keypad": inline_keypad.asdict() if inline_keypad else None,
            "chat_keypad_type": chat_keypad_type,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id
        }
        response = await self.request("sendMessage", self.clean_data(data))
        message = MessageId.from_dict(response)
        message.chat_id = chat_id
        message.client = self
        return message

    async def send_poll(
        self,
        chat_id: str,
        question: str,
        options: list[str],
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": options,
            "chat_keypad": chat_keypad.asdict() if chat_keypad else None,
            "inline_keypad": inline_keypad.asdict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        response = await self.request("sendPoll", self.clean_data(data))
        message = MessageId.from_dict(response)
        message.chat_id = chat_id
        message.client = self
        return message

    async def send_location(
        self,
        chat_id: str,
        latitude: str,
        longitude: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "chat_keypad": chat_keypad.asdict() if chat_keypad else None,
            "inline_keypad": inline_keypad.asdict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        response = await self.request("sendLocation", self.clean_data(data))
        message = MessageId.from_dict(response)
        message.chat_id = chat_id
        message.client = self
        return message

    async def send_contact(
        self,
        chat_id: str,
        first_name: str,
        last_name: str,
        phone_number: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "chat_keypad": chat_keypad.asdict() if chat_keypad else None,
            "inline_keypad": inline_keypad.asdict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        response = await self.request("sendContact", self.clean_data(data))
        message = MessageId.from_dict(response)
        message.chat_id = chat_id
        message.client = self
        return message

    async def send_sticker(
        self,
        chat_id: str,
        sticker_id: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "sticker_id": sticker_id,
            "chat_keypad": chat_keypad.asdict() if chat_keypad else None,
            "inline_keypad": inline_keypad.asdict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        response = await self.request("sendSticker", self.clean_data(data))
        message = MessageId.from_dict(response)
        message.chat_id = chat_id
        message.client = self
        return message

    async def request_send_file(self, type: str):
        response = await self.request("requestSendFile", {"type": type})
        return response["upload_url"]

    async def upload_file(self, file: Union[str, bytes], name: Optional[str] = None, type: str = "File"):
        upload_url = await self.request_send_file(type)
        response = await self.requestUpload(upload_url, file, name)
        return response

    async def download_file(self, file_id: str, filename: Optional[str] = None):
        download_url = await self.get_file(file_id)
        response = await self.requestDownload(download_url, filename)
        return response

    async def send_file(
        self,
        chat_id: str,
        file: Union[str, bytes],
        caption: Optional[str] = None,
        file_name: Optional[str] = None,
        type: enums.FileType = enums.FileType.File,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
    ) -> "MessageId":
        file_id = await self.upload_file(file, file_name, type)
        
        data = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": caption,
            "chat_keypad": chat_keypad.asdict() if chat_keypad else None,
            "inline_keypad": inline_keypad.asdict() if inline_keypad else None,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type,
        }
        response = await self.request("sendFile", self.clean_data(data))
        message = MessageId.from_dict(response)
        message.chat_id = chat_id
        message.file_id = file_id
        message.client = self
        return message



    async def send_document(self, chat_id: str, document: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs):
        return await self.send_file(chat_id, document, caption, file_name, "File", **kwargs)

    async def send_photo(self, chat_id: str, photo: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs):
        return await self.send_file(chat_id, photo, caption, file_name, "Image", **kwargs)

    async def send_video(self, chat_id: str, video: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs):
        return await self.send_file(chat_id, video, caption, file_name, "Video", **kwargs)

    async def send_gif(self, chat_id: str, gif: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs):
        return await self.send_file(chat_id, gif, caption, file_name, "Gif", **kwargs)

    async def send_music(self, chat_id: str, music: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs):
        return await self.send_file(chat_id, music, caption, file_name, "Music", **kwargs)

    async def send_voice(self, chat_id: str, voice: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs):
        return await self.send_file(chat_id, voice, caption, file_name, "Voice", **kwargs)