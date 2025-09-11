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


from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


class QueryParameter(BaseModel):
    query: str


class DownloaderBy(BaseModel):
    url: str


class Username(BaseModel):
    username: str


class OpenaiWhisper(BaseModel):
    url: str
    language: Optional[str] = None
    task: Optional[str] = None


class RequestXnxx(BaseModel):
    query: str
    is_download: bool = Field(False, alias="isDownload")
    url: Optional[str] = None


class RequestHumanizer(BaseModel):
    text: str
    writing_style: str
    author_id: str
    timestamp: str

class MakeFetch(BaseModel):
    url: str
    post: bool = False
    head: bool = False
    headers: Optional[dict] = None
    evaluate: Optional[Callable] = None
    object_flag: bool = False
    return_json: bool = False
    return_content: bool = False
    return_json_and_obj: bool = False
