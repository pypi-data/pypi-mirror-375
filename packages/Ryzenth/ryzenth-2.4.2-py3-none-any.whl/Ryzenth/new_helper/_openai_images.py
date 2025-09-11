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
from typing import Union

from .._benchmark import Benchmark
from .._client import RyzenthApiClient
from .._errors import (
    AuthenticationError,
    EmptyMessageError,
    EmptyResponseError,
    InitializeAPIError,
    InternalServerOpenaiError,
    InvalidMessageError,
    WhatFuckError,
)
from .._export_class import GeneratedImageOrVideo
from ..enums import ResponseType
from ..helper import AutoRetry, HelpersUseStatic


class ImagesOpenAIAsync:
    def __init__(self, parent):
        self.parent = parent
        self._client = None
        self.request = HelpersUseStatic
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    def _get_client(self) -> RyzenthApiClient:
        if self._client is None:
            api_key = getattr(
                self.parent,
                "_api_key",
                None) or os.environ.get("OPENAI_API_KEY")

            if not api_key or not isinstance(
                    api_key, str) or not api_key.strip():
                raise AuthenticationError(
                    "Missing or invalid API key for openAI client initialization.")
            try:
                self._client = RyzenthApiClient(
                    tools_name=["openai"],
                    api_key={"openai": [
                        {
                            "Authorization": f"Bearer {api_key}",
                            "Content-type": "application/json"
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
    async def create(
        self,
        prompt: str,
        *,
        timeout: Union[int, float] = 100,
        model: str = "gpt-image-1",
    ) -> GeneratedImageOrVideo:
        if not prompt or not prompt.strip():
            raise EmptyMessageError("Prompt cannot be empty")

        try:
            async with self._get_client() as client:
                response = await client.post(
                    tool="openai",
                    path="/images/generations",
                    timeout=timeout,
                    json={
                        "model": model,
                        "prompt": prompt
                    },
                    use_type=ResponseType.JSON
                )
                if not response:
                    raise EmptyResponseError(
                        "Empty response from openai image generation API")
                return GeneratedImageOrVideo(client=client, content=response)
        except Exception as e:
            self.logger.error(f"Openai image generation failed: {e}")
            raise InternalServerOpenaiError(f"Openai image generation failed: {e}") from e
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
