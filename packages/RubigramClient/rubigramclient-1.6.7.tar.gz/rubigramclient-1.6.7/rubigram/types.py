from typing import Optional, Union, Any
from pydantic import BaseModel
from rubigram import enums


class DataManager(BaseModel):
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

    @classmethod
    def from_dict(cls, data: dict):
        return cls.model_validate(data or {})

    def asdict(self, exclude_none: bool = True) -> dict:
        return self.model_dump(exclude_none=exclude_none, exclude={"client"})

    def asjson(self, exclude_none: bool = True) -> str:
        return self.model_dump_json(indent=4, exclude_none=exclude_none, exclude={"client"})


class Chat(DataManager):
    chat_id: Optional[str] = None
    chat_type: Optional[enums.ChatType] = None
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None

    def __init__(
        self,
        chat_id: Optional[str] = None,
        chat_type: Optional[enums.ChatType] = None,
        user_id: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        title: Optional[str] = None,
        username: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            chat_id=chat_id,
            chat_type=chat_type,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            title=title,
            username=username,
            **kwargs
        )


class File(DataManager):
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    size: Optional[str] = None

    def __init__(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        size: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            file_id=file_id,
            file_name=file_name,
            size=size,
            **kwargs
        )


class ForwardedFrom(DataManager):
    type_from: Optional[enums.ForwardedFrom] = None
    message_id: Optional[str] = None
    from_chat_id: Optional[str] = None
    from_sender_id: Optional[str] = None

    def __init__(
        self,
        type_from: Optional[enums.ForwardedFrom] = None,
        message_id: Optional[str] = None,
        from_chat_id: Optional[str] = None,
        from_sender_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            type_from=type_from,
            message_id=message_id,
            from_chat_id=from_chat_id,
            from_sender_id=from_sender_id,
            **kwargs
        )


class PaymentStatus(DataManager):
    payment_id: Optional[str] = None
    status: Optional[enums.PaymentStatus] = None

    def __init__(
        self,
        payment_id: Optional[str] = None,
        status: Optional[enums.PaymentStatus] = None,
        **kwargs
    ):
        super().__init__(
            payment_id=payment_id,
            status=status,
            **kwargs
        )


class MessageTextUpdate(DataManager):
    message_id: Optional[str] = None
    text: Optional[str] = None

    def __init__(
        self,
        message_id: Optional[str] = None,
        text: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message_id=message_id,
            text=text,
            **kwargs
        )


class Bot(DataManager):
    bot_id: Optional[str] = None
    bot_title: Optional[str] = None
    avatar: Optional[File] = None
    description: Optional[str] = None
    username: Optional[str] = None
    start_message: Optional[str] = None
    share_url: Optional[str] = None

    def __init__(
        self,
        bot_id: Optional[str] = None,
        bot_title: Optional[str] = None,
        avatar: Optional[File] = None,
        description: Optional[str] = None,
        username: Optional[str] = None,
        start_message: Optional[str] = None,
        share_url: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            bot_id=bot_id,
            bot_title=bot_title,
            avatar=avatar,
            description=description,
            username=username,
            start_message=start_message,
            share_url=share_url,
            **kwargs
        )


class BotCommand(DataManager):
    command: Optional[str] = None
    description: Optional[str] = None

    def __init__(
        self,
        command: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            command=command,
            description=description,
            **kwargs
        )


class Sticker(DataManager):
    sticker_id: Optional[str] = None
    file: Optional[File] = None
    emoji_character: Optional[str] = None

    def __init__(
        self,
        sticker_id: Optional[str] = None,
        file: Optional[File] = None,
        emoji_character: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            sticker_id=sticker_id,
            file=file,
            emoji_character=emoji_character,
            **kwargs
        )


class ContactMessage(DataManager):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    def __init__(
        self,
        phone_number: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )


class PollStatus(DataManager):
    state: Optional[enums.PollStatus] = None
    selection_index: Optional[int] = None
    percent_vote_options: Optional[list[int]] = None
    total_vote: Optional[int] = None
    show_total_votes: Optional[bool] = None

    def __init__(
        self,
        state: Optional[enums.PollStatus] = None,
        selection_index: Optional[int] = None,
        percent_vote_options: Optional[list[int]] = None,
        total_vote: Optional[int] = None,
        show_total_votes: Optional[bool] = None,
        **kwargs
    ):
        super().__init__(
            state=state,
            selection_index=selection_index,
            percent_vote_options=percent_vote_options,
            total_vote=total_vote,
            show_total_votes=show_total_votes,
            **kwargs
        )


class Poll(DataManager):
    question: Optional[str] = None
    options: Optional[list[str]] = None
    poll_status: Optional[PollStatus] = None

    def __init__(
        self,
        question: Optional[str] = None,
        options: Optional[list[str]] = None,
        poll_status: Optional[PollStatus] = None,
        **kwargs
    ):
        super().__init__(
            question=question,
            options=options,
            poll_status=poll_status,
            **kwargs
        )


class Location(DataManager):
    longitude: Optional[str] = None
    latitude: Optional[str] = None

    def __init__(
        self,
        longitude: Optional[str] = None,
        latitude: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            longitude=longitude,
            latitude=latitude,
            **kwargs
        )


class LiveLocation(DataManager):
    start_time: Optional[str] = None
    live_period: Optional[int] = None
    current_location: Optional[Location] = None
    user_id: Optional[str] = None
    status: Optional[enums.LiveLocationStatus] = None
    last_update_time: Optional[str] = None

    def __init__(
        self,
        start_time: Optional[str] = None,
        live_period: Optional[int] = None,
        current_location: Optional[Location] = None,
        user_id: Optional[str] = None,
        status: Optional[enums.LiveLocationStatus] = None,
        last_update_time: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            start_time=start_time,
            live_period=live_period,
            current_location=current_location,
            user_id=user_id,
            status=status,
            last_update_time=last_update_time,
            **kwargs
        )


class ButtonSelectionItem(DataManager):
    text: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[enums.ButtonSelectionType] = None

    def __init__(
        self,
        text: Optional[str] = None,
        image_url: Optional[str] = None,
        type: Optional[enums.ButtonSelectionType] = None,
        **kwargs
    ):
        super().__init__(
            text=text,
            image_url=image_url,
            type=type,
            **kwargs
        )


class ButtonSelection(DataManager):
    selection_id: Optional[str] = None
    search_type: Optional[str] = None
    get_type: Optional[str] = None
    items: Optional[list[ButtonSelectionItem]] = None
    is_multi_selection: Optional[bool] = None
    columns_count: Optional[str] = None
    title: Optional[str] = None

    def __init__(
        self,
        selection_id: Optional[str] = None,
        search_type: Optional[str] = None,
        get_type: Optional[str] = None,
        items: Optional[list[ButtonSelectionItem]] = None,
        is_multi_selection: Optional[bool] = None,
        columns_count: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            selection_id=selection_id,
            search_type=search_type,
            get_type=get_type,
            items=items,
            is_multi_selection=is_multi_selection,
            columns_count=columns_count,
            title=title,
            **kwargs
        )


class ButtonCalendar(DataManager):
    default_value: Optional[str] = None
    type: Optional[enums.ButtonCalendarType] = None
    min_year: Optional[str] = None
    max_year: Optional[str] = None
    title: Optional[str] = None

    def __init__(
        self,
        default_value: Optional[str] = None,
        type: Optional[enums.ButtonCalendarType] = None,
        min_year: Optional[str] = None,
        max_year: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            default_value=default_value,
            type=type,
            min_year=min_year,
            max_year=max_year,
            title=title,
            **kwargs
        )


class ButtonNumberPicker(DataManager):
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    default_value: Optional[str] = None
    title: Optional[str] = None

    def __init__(
        self,
        min_value: Optional[str] = None,
        max_value: Optional[str] = None,
        default_value: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            min_value=min_value,
            max_value=max_value,
            default_value=default_value,
            title=title,
            **kwargs
        )


class ButtonStringPicker(DataManager):
    items: Optional[list[str]] = None
    default_value: Optional[str] = None
    title: Optional[str] = None

    def __init__(
        self,
        items: Optional[list[str]] = None,
        default_value: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            items=items,
            default_value=default_value,
            title=title,
            **kwargs
        )


class ButtonTextbox(DataManager):
    type_line: Optional[enums.ButtonTextboxTypeLine] = None
    type_keypad: Optional[enums.ButtonTextboxTypeKeypad] = None
    place_holder: Optional[str] = None
    title: Optional[str] = None
    default_value: Optional[str] = None

    def __init__(
        self,
        type_line: Optional[enums.ButtonTextboxTypeLine] = None,
        type_keypad: Optional[enums.ButtonTextboxTypeKeypad] = None,
        place_holder: Optional[str] = None,
        title: Optional[str] = None,
        default_value: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            type_line=type_line,
            type_keypad=type_keypad,
            place_holder=place_holder,
            title=title,
            default_value=default_value,
            **kwargs
        )


class ButtonLocation(DataManager):
    default_pointer_location: Optional[Location] = None
    default_map_location: Optional[Location] = None
    type: Optional[enums.ButtonLocationType] = None
    title: Optional[str] = None
    location_image_url: Optional[str] = None

    def __init__(
        self,
        default_pointer_location: Optional[Location] = None,
        default_map_location: Optional[Location] = None,
        type: Optional[enums.ButtonLocationType] = None,
        title: Optional[str] = None,
        location_image_url: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            default_pointer_location=default_pointer_location,
            default_map_location=default_map_location,
            type=type,
            title=title,
            location_image_url=location_image_url,
            **kwargs
        )


class OpenChatData(DataManager):
    object_guid: Optional[str] = None
    object_type: Optional[enums.ChatType] = None

    def __init__(
        self,
        object_guid: Optional[str] = None,
        object_type: Optional[enums.ChatType] = None,
        **kwargs
    ):
        super().__init__(
            object_guid=object_guid,
            object_type=object_type,
            **kwargs
        )


class JoinChannelData(DataManager):
    username: Optional[str] = None
    ask_join: bool = False

    def __init__(
        self,
        username: Optional[str] = None,
        ask_join: bool = False,
        **kwargs
    ):
        super().__init__(
            username=username,
            ask_join=ask_join,
            **kwargs
        )


class ButtonLink(DataManager):
    type: Optional[enums.ButtonLinkType] = None
    link_url: Optional[str] = None
    joinchannel_data: Optional[JoinChannelData] = None
    open_chat_data: Optional[OpenChatData] = None

    def __init__(
        self,
        type: Optional[enums.ButtonLinkType] = None,
        link_url: Optional[str] = None,
        joinchannel_data: Optional[JoinChannelData] = None,
        open_chat_data: Optional[OpenChatData] = None,
        **kwargs
    ):
        super().__init__(
            type=type,
            link_url=link_url,
            joinchannel_data=joinchannel_data,
            open_chat_data=open_chat_data,
            **kwargs
        )


class AuxData(DataManager):
    start_id: Optional[str] = None
    button_id: Optional[str] = None

    def __init__(
        self,
        start_id: Optional[str] = None,
        button_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            start_id=start_id,
            button_id=button_id,
            **kwargs
        )


class Button(DataManager):
    id: Optional[str] = None
    button_text: Optional[str] = None
    type: enums.ButtonType = enums.ButtonType.Simple
    button_selection: Optional[ButtonSelection] = None
    button_calendar: Optional[ButtonCalendar] = None
    button_number_picker: Optional[ButtonNumberPicker] = None
    button_string_picker: Optional[ButtonStringPicker] = None
    button_location: Optional[ButtonLocation] = None
    button_textbox: Optional[ButtonTextbox] = None
    button_link: Optional[ButtonLink] = None

    def __init__(
        self,
        id: Optional[str] = None,
        button_text: Optional[str] = None,
        type: enums.ButtonType = enums.ButtonType.Simple,
        button_selection: Optional[ButtonSelection] = None,
        button_calendar: Optional[ButtonCalendar] = None,
        button_number_picker: Optional[ButtonNumberPicker] = None,
        button_string_picker: Optional[ButtonStringPicker] = None,
        button_location: Optional[ButtonLocation] = None,
        button_textbox: Optional[ButtonTextbox] = None,
        button_link: Optional[ButtonLink] = None,
        **kwargs
    ):
        super().__init__(
            id=id,
            button_text=button_text,
            type=type,
            button_selection=button_selection,
            button_calendar=button_calendar,
            button_number_picker=button_number_picker,
            button_string_picker=button_string_picker,
            button_location=button_location,
            button_textbox=button_textbox,
            button_link=button_link,
            **kwargs
        )


class KeypadRow(DataManager):
    buttons: list[Button]

    def __init__(
        self,
        buttons: list[Button],
        **kwargs
    ):
        super().__init__(
            buttons=buttons,
            **kwargs
        )


class Keypad(DataManager):
    rows: list[KeypadRow]
    resize_keyboard: bool = True
    on_time_keyboard: bool = False

    def __init__(
        self,
        rows: list[KeypadRow],
        resize_keyboard: bool = True,
        on_time_keyboard: bool = False,
        **kwargs
    ):
        super().__init__(
            rows=rows,
            resize_keyboard=resize_keyboard,
            on_time_keyboard=on_time_keyboard,
            **kwargs
        )


class MessageKeypadUpdate(DataManager):
    message_id: Optional[str] = None
    inline_keypad: Optional[Keypad] = None

    def __init__(
        self,
        message_id: Optional[str] = None,
        inline_keypad: Optional[Keypad] = None,
        **kwargs
    ):
        super().__init__(
            message_id=message_id,
            inline_keypad=inline_keypad,
            **kwargs
        )


class Message(DataManager):
    message_id: Optional[str] = None
    text: Optional[str] = None
    time: Optional[str] = None
    is_edited: Optional[bool] = None
    sender_type: Optional[enums.MessageSender] = None
    sender_id: Optional[str] = None
    aux_data: Optional[AuxData] = None
    file: Optional[File] = None
    reply_to_message_id: Optional[str] = None
    forwarded_from: Optional[ForwardedFrom] = None
    forwarded_no_link: Optional[str] = None
    location: Optional[Location] = None
    sticker: Optional[Sticker] = None
    contact_message: Optional[ContactMessage] = None
    poll: Optional[Poll] = None
    live_location: Optional[LiveLocation] = None

    def __init__(
        self,
        message_id: Optional[str] = None,
        text: Optional[str] = None,
        time: Optional[str] = None,
        is_edited: Optional[bool] = None,
        sender_type: Optional[enums.MessageSender] = None,
        sender_id: Optional[str] = None,
        aux_data: Optional[AuxData] = None,
        file: Optional[File] = None,
        reply_to_message_id: Optional[str] = None,
        forwarded_from: Optional[ForwardedFrom] = None,
        forwarded_no_link: Optional[str] = None,
        location: Optional[Location] = None,
        sticker: Optional[Sticker] = None,
        contact_message: Optional[ContactMessage] = None,
        poll: Optional[Poll] = None,
        live_location: Optional[LiveLocation] = None,
        **kwargs
    ):
        super().__init__(
            message_id=message_id,
            text=text,
            time=time,
            is_edited=is_edited,
            sender_type=sender_type,
            sender_id=sender_id,
            aux_data=aux_data,
            file=file,
            reply_to_message_id=reply_to_message_id,
            forwarded_from=forwarded_from,
            forwarded_no_link=forwarded_no_link,
            location=location,
            sticker=sticker,
            contact_message=contact_message,
            poll=poll,
            live_location=live_location,
            **kwargs
        )


class MessageId(DataManager):
    message_id: Optional[str] = None
    file_id: Optional[str] = None
    chat_id: Optional[str] = None
    client: Optional[Any] = None

    def __init__(
        self,
        message_id: Optional[str] = None,
        file_id: Optional[str] = None,
        chat_id: Optional[str] = None,
        client: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message_id=message_id,
            file_id=file_id,
            chat_id=chat_id,
            client=client,
            **kwargs
        )

    async def delete(self):
        return await self.client.delete_message(self.chat_id, self.message_id)

    async def edit_text(self, text: str):
        return await self.client.edit_message_text(self.chat_id, self.message_id, text)

    async def edit_message_keypad(self, keypad: Keypad):
        return await self.client.edit_message_keypad(self.chat_id, self.message_id, keypad)

    async def forward(self, chat_id: str):
        return await self.client.forward_message(self.chat_id, self.message_id, chat_id)


class Update(DataManager):
    client: Optional[Any] = None
    type: Optional[enums.UpdateType] = None
    chat_id: Optional[str] = None
    removed_message_id: Optional[str] = None
    new_message: Optional[Message] = None
    updated_message: Optional[Message] = None
    updated_payment: Optional[PaymentStatus] = None

    def __init__(
        self,
        type: Optional[enums.UpdateType] = None,
        chat_id: Optional[str] = None,
        removed_message_id: Optional[str] = None,
        new_message: Optional[Message] = None,
        updated_message: Optional[Message] = None,
        updated_payment: Optional[PaymentStatus] = None,
        **kwargs
    ):
        super().__init__(
            type=type,
            chat_id=chat_id,
            removed_message_id=removed_message_id,
            new_message=new_message,
            updated_message=updated_message,
            updated_payment=updated_payment,
            **kwargs
        )

    async def download(self, file_name: str):
        return await self.client.download_file(self.new_message.file.file_id, file_name)

    async def forward(self, chat_id: str):
        return await self.client.forward_message(self.chat_id, self.new_message.message_id, chat_id)

    async def reply(
        self,
        text: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = None,
    ) -> "MessageId":
        return await self.client.send_message(
            self.chat_id,
            text,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

    async def reply_poll(
        self,
        question: str,
        options: list[str],
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_poll(
            self.chat_id,
            question,
            options,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

    async def reply_location(
        self,
        latitude: str,
        longitude: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_location(
            self.chat_id,
            latitude,
            longitude,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

    async def reply_contact(
        self,
        first_name: str,
        last_name: str,
        phone_number: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_location(
            self.chat_id,
            first_name,
            last_name,
            phone_number,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

    async def reply_sticker(
        self,
        sticker_id: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_message(
            self.chat_id,
            sticker_id,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

    async def reply_file(
        self,
        file: Union[str, bytes],
        caption: Optional[str] = None,
        file_name: Optional[str] = None,
        type: enums.FileType = enums.FileType.File,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Optional[enums.ChatKeypadType] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_file(
            self.chat_id,
            file,
            caption,
            file_name,
            type,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id,
        )

    async def reply_document(self, document: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(document, caption, file_name, "File", **kwargs)

    async def reply_photo(self, photo: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(photo, caption, file_name, "Image", **kwargs)

    async def reply_video(self, video: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(video, caption, file_name, "Video", **kwargs)

    async def reply_gif(self, gif: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(gif, caption, file_name, "Gif", **kwargs)

    async def reply_music(self, music: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(music, caption, file_name, "Music", **kwargs)

    async def reply_voice(self, voice: Union[str, bytes], caption: Optional[str] = None, file_name: Optional[str] = None, **kwargs) -> "MessageId":
        return await self.reply_file(voice, caption, file_name, "Voice", **kwargs)


class InlineMessage(DataManager):
    client: Optional[Any] = None
    sender_id: Optional[str] = None
    text: Optional[str] = None
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    file: Optional[File] = None
    location: Optional[Location] = None
    aux_data: Optional[AuxData] = None

    def __init__(
        self,
        sender_id: Optional[str] = None,
        text: Optional[str] = None,
        message_id: Optional[str] = None,
        chat_id: Optional[str] = None,
        file: Optional[File] = None,
        location: Optional[Location] = None,
        aux_data: Optional[AuxData] = None,
        **kwargs
    ):
        super().__init__(
            sender_id=sender_id,
            text=text,
            message_id=message_id,
            chat_id=chat_id,
            file=file,
            location=location,
            aux_data=aux_data,
            **kwargs
        )


class Updates(DataManager):
    updates: Optional[list[Update]] = None
    next_offset_id: Optional[str] = None

    def __init__(
        self,
        updates: Optional[list[Update]] = None,
        next_offset_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            updates=updates,
            next_offset_id=next_offset_id,
            **kwargs
        )