from typing import List
from abc import ABC, abstractmethod

from langchain_core.messages import SystemMessage
from langchain_core.messages.base import BaseMessage

from langchain_core.prompts.base import BasePromptTemplate
from langchain_core.prompts import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)


class BasePromptCreator(ABC):
    """Base prompt creator.

    Abstact Methods:
        - get_base_messages: 获取基础消息列表

    Methods:
        - create_prompt: 生成提示词

    """

    @abstractmethod
    def get_base_messages(self) -> List[BaseMessage]:
        pass

    @classmethod
    def create_prompt(
        cls,
        *,
        message_templates: List[
            SystemMessagePromptTemplate | HumanMessagePromptTemplate
        ] = None,
        histories: List[str] = None,
    ) -> BasePromptTemplate:
        """
        生成提示词
        Args:
            - message_templates: 消息模板列表, 优先于历史消息列表
            - histories: 历史消息列表
        Returns:
            - prompt: 聊天提示词模板
        """
        messages = cls.get_base_messages()
        messages = cls.add_message_templates(messages, message_templates)
        messages = cls.add_histories(messages, histories)
        prompt = ChatPromptTemplate.from_messages(messages)
        return prompt

    @classmethod
    def add_message_templates(
        cls, messages: list, message_templates: List[HumanMessagePromptTemplate] = None
    ):
        """
        添加模板到消息列表中
        """

        if message_templates is not None:
            for message_template in message_templates:
                messages.append(message_template)
        return messages

    @classmethod
    def add_histories(cls, messages: list, histories: List[str] = None):
        """
        添加历史记录到消息列表中
        """

        if histories is not None:
            messages.append(SystemMessage(f"以下为历史信息: {';'.join(histories)}"))
        return messages
