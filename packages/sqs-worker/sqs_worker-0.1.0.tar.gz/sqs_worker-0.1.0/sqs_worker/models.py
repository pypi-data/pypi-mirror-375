import typing

import pydantic


T = typing.TypeVar('T', bound=pydantic.BaseModel)


class Message(
    pydantic.BaseModel,
    typing.Generic[T],
):
    version: str
    msg_type: str
    queue_name: str | None = None
    receipt_handle: str | None = None
    payload: T = pydantic.Field(
        repr=False,
    )
    retry_attempt: int = 0