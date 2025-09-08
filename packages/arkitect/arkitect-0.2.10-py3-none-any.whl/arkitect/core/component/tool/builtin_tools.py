# Copyright 2025 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from volcenginesdkarkruntime._models import BaseModel

from arkitect.core.client.http import default_ark_client


async def link_reader(url_list: list[str]) -> dict:
    """
    当你需要获取网页、pdf、抖音视频内容时，使用此工具。可以获取url链接下的标题和内容。


    examples: {"url_list":["abc.com", "xyz.com"]}
    Args:
        url_list (list[str]): 需要解析网页链接,最多3个,以列表返回
    """
    client = default_ark_client()
    body = {
        "action_name": "LinkReader",
        "tool_name": "LinkReader",
        "parameters": {"url_list": url_list},
    }

    response = await client.post(path="/tools/execute", body=body, cast_to=BaseModel)
    return response.model_dump()


async def calculator(input: str) -> dict:
    """Evaluate a given mathematical expression

    Args:
    input(str): The mathematical expression in WolframLanguage InputForm


    """
    client = default_ark_client()
    body = {
        "action_name": "Calculator",
        "tool_name": "Calculator",
        "parameters": {"input": input},
    }

    response = await client.post(path="/tools/execute", body=body, cast_to=BaseModel)
    return response.model_dump()
