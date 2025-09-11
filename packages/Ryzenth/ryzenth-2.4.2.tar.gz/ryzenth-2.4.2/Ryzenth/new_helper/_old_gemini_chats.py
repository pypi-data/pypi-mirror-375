#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2025 (c) Randy W @xtdevs, @xtsea
#
# from : https://github.com/TeamKillerX
# Channel : @RendyProjects
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import logging
import os
from typing import Dict, List, Union

from .._benchmark import Benchmark
from .._client import RyzenthApiClient
from .._errors import (
    AuthenticationError,
    EmptyMessageError,
    EmptyResponseError,
    InitializeAPIError,
    InternalServerGeminiError,
    InvalidEmptyError,
    WhatFuckError,
)
from .._export_class import ResponseResult
from ..enums import ResponseType
from ..helper import AutoRetry


class OldChatsGeminiAsync:
    def __init__(self, parent):
        self.parent = parent
        self._client = None
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    def _get_client(self) -> RyzenthApiClient:
        if self._client is None:
            api_key = getattr(
                self.parent,
                "_api_key",
                None) or os.environ.get("GEMINI_API_KEY")

            if not api_key or not isinstance(
                    api_key, str) or not api_key.strip():
                raise AuthenticationError(
                    "Missing or invalid API key for Gemini client initialization.")
            try:
                self._client = RyzenthApiClient(
                    tools_name=["gemini"],
                    api_key={"gemini": [
                        {
                            "x-goog-api-key": api_key
                        }
                    ]},
                    rate_limit=100,
                    use_default_headers=True
                )
            except Exception as e:
                raise InitializeAPIError(
                    f"Failed to initialize API client: {e}") from e
        return self._client

    @Benchmark.performance(level=logging.DEBUG)
    @AutoRetry(max_retries=3, delay=1.5)
    async def ask(
        self,
        messages: str | List[Dict],
        *,
        timeout: Union[int, float] = 100,
        model: str = "gemini-2.5-flash",
        use_multi_chat: bool = False
    ) -> ResponseResult:
        if isinstance(messages, str):
            if not messages.strip():
                raise EmptyMessageError("messages cannot be empty")
        elif isinstance(messages, list):
            if not messages or all(
                isinstance(
                    item,
                    dict) and not item for item in messages):
                raise EmptyMessageError("messages cannot be empty")
        else:
            raise InvalidEmptyError(
                f"messages type is invalid: received type '{type(messages).__name__}'")

        try:
            if use_multi_chat:
                json = {"contents": messages}
            else:
                json = {
                    "contents": [
                        {
                            "parts": [{"text": messages}]
                        }
                    ]
                }
            async with self._get_client() as client:
                response = await client.post(
                    tool="gemini",
                    path=f"/models/{model}:generateContent",
                    timeout=timeout,
                    json=json,
                    use_type=ResponseType.JSON
                )
                if not response:
                    raise EmptyResponseError(
                        "Empty response from chat completion API")
                return ResponseResult(client=client, response=response)
        except Exception as e:
            self.logger.error(f"Gemini chats failed: {e}")
            raise InternalServerGeminiError(f"Gemini chats failed: {e}") from e
        finally:
            pass

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
