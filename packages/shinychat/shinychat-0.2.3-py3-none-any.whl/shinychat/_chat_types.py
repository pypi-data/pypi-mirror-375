from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from htmltools import HTML, Tag, TagChild, Tagifiable, TagList
from shiny.session import get_current_session

from ._typing_extensions import NotRequired

Role = Literal["assistant", "user", "system"]


# TODO: content should probably be [{"type": "text", "content": "..."}, {"type": "image", ...}]
# in order to support multiple content types...
class ChatMessageDict(TypedDict):
    content: str
    role: Role


class ChatMessage:
    def __init__(
        self,
        content: TagChild,
        role: Role = "assistant",
    ):
        self.role: Role = role

        is_html = isinstance(content, (Tag, TagList, HTML, Tagifiable))

        # content _can_ be a TagChild, but it's most likely just a string (of
        # markdown), so only process it if it's not a string.
        deps = []
        if not isinstance(content, str):
            session = get_current_session()
            if session and not session.is_stub_session():
                res = session._process_ui(content)
                deps = res["deps"]
            else:
                res = TagList(content).render()
                deps = [d.as_dict() for d in res["dependencies"]]
            content = res["html"]

        if is_html:
            # Code blocks with `{=html}` infostrings are rendered as-is by a
            # custom rendering method in markdown-stream.ts
            content = f"\n\n````````{{=html}}\n{content}\n````````\n\n"

        self.content = content
        self.html_deps = deps


# A message once transformed have been applied
@dataclass
class TransformedMessage:
    content_client: str | HTML
    content_server: str
    role: Role
    transform_key: Literal["content_client", "content_server"]
    pre_transform_key: Literal["content_client", "content_server"]
    html_deps: list[dict[str, str]] | None = None

    @classmethod
    def from_chat_message(cls, message: ChatMessage) -> "TransformedMessage":
        if message.role == "user":
            transform_key = "content_server"
            pre_transform_key = "content_client"
        else:
            transform_key = "content_client"
            pre_transform_key = "content_server"

        return TransformedMessage(
            content_client=message.content,
            content_server=message.content,
            role=message.role,
            transform_key=transform_key,
            pre_transform_key=pre_transform_key,
            html_deps=message.html_deps,
        )


# A message that can be sent to the client
class ClientMessage(TypedDict):
    content: str
    role: Literal["assistant", "user"]
    content_type: Literal["markdown", "html"]
    chunk_type: Literal["message_start", "message_end"] | None
    operation: Literal["append", "replace"]
    icon: NotRequired[str]
    html_deps: NotRequired[list[dict[str, str]]]
