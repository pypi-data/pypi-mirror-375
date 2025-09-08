from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, model_validator


class BaseEvent(BaseModel):
    user_id: int
    peer_id: int
    payload: Optional[Dict[str, Any]] = None
    bot: Optional["Bot"] = Field(None, exclude=True)

    class Config:
        extra = "allow"
        populate_by_name = True


class Message(BaseEvent):
    user_id: int = Field(..., alias="from_id")
    text: str
    conversation_message_id: Optional[int] = None

    async def answer(
        self, text: str, keyboard: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """
        Упрощенная отправка сообщения в ответ на текущее.
        Автоматически использует peer_id из события.
        """
        if not self.bot:
            raise RuntimeError("Bot instance is not attached to the event.")
        return await self.bot.send_message(
            peer_id=self.peer_id, text=text, keyboard=keyboard, **kwargs
        )

    @model_validator(mode="before")
    @classmethod
    def extract_message_from_event(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if "message" in data and isinstance(data["message"], dict):
            if "client_info" in data:
                data["message"]["client_info"] = data["client_info"]
            return data["message"]
        return data

    @model_validator(mode="before")
    @classmethod
    def parse_payload_from_str(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        payload_str = data.get("payload")
        if payload_str and isinstance(payload_str, str):
            data["payload"] = json.loads(payload_str)
        return data


class Callback(BaseEvent):
    event_id: str
    conversation_message_id: int

    async def edit_text(self, text: str, keyboard: Optional[str] = None, **kwargs: Any):
        """
        Упрощенное редактирование сообщения в ответ на callback.
        Автоматически убирает "часики" и редактирует сообщение.
        """
        if not self.bot:
            raise RuntimeError("Bot instance is not attached to the event.")

        await asyncio.gather(
            self.bot.answer_callback(self),
            self.bot.edit_message(
                peer_id=self.peer_id,
                conversation_message_id=self.conversation_message_id,
                text=text,
                keyboard=keyboard,
                **kwargs,
            ),
        )

    @model_validator(mode="before")
    @classmethod
    def parse_payload_from_str(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        payload_str = data.get("payload")
        if payload_str and isinstance(payload_str, str):
            data["payload"] = json.loads(payload_str)
        return data


VKEvent = Union[Message, Callback]

from .bot import Bot
