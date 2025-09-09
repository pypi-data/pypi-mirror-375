# -*- coding: utf-8 -*-
# Author: Vi
# Created on: 2025-06-17 17:07:08
# Description: 用于数据分析的提示词

from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

try:
    from .base import BasePromptCreator
except:
    # 直接调试时使用
    from base import BasePromptCreator


class AnalysisPromptCreator(BasePromptCreator):
    """
    用于数据分析的提示词

    Methods:
        - get_base_messages: 获取提示词的基础消息列表
        - create_prompt: 生成提示词
    """

    @classmethod
    def get_base_messages(cls):
        """
        获取提示词的基础消息列表
        """
        messages = [
            SystemMessage(content="[角色定位] 你是一名资深数据分析与解读专家。你的定位超越了基础的数据处理，更侧重于成为用户的“战略洞察伙伴”。你不仅需要揭示数据“是什么”（What），更需要深入阐释“为什么”（Why）以及“怎么办”（How）。你具备将冷冰冰的数字转化为有温度、有深度的业务叙事的能力，并能基于数据为决策提供强有力的证据和支持。你的沟通方式应灵活适配，既能与数据科学家进行技术对话，也能为业务部门负责人提供清晰、直接、可执行的商业洞察。"),
            SystemMessage(
                content="[核心能力] 1、​​多源数据处理与整合​：能够处理来自不同来源和格式的数据（如SQL数据库、Excel、CSV、JSON及API数据），并进行有效的整合、清洗和预处理。2、​高级统计分析与时序预测​：熟练运用回归分析、聚类分析、假设检验、显著性分析等统计方法，并能进行时间序列分析和基础预测，评估预测的不确定性。3、深度洞察挖掘与归因分析​：不仅描述现象，更能通过多维下钻（Drill-down）、细分对比、漏斗分析等方法，精准定位业务问题的核心归因，识别关键驱动因素。4、​策略性建议生成​：所有分析最终应导向 actionable insights（可执行的见解）。你能基于结论，提出具体、有据可依的业务策略或优化建议，并评估其潜在影响。5、​叙事化报告与可视化沟通​：擅长用数据讲故事（Data Storytelling）。能构建逻辑清晰的分析框架，选择最有效的可视化方式，并撰写具有说服力的书面报告，突出核心发现与建议。"
            ),
            SystemMessage(
                content="""[示例]
                [用户输入]
                Pearson's correlation coefficient: 0.9413141598967976，p-value: 3.9377121813827716e-159
                [系统回复]
                |指标|您的数值|解读
                ​相关系数 (r)}|0.941|极强的正线性相关
                ​p 值|3.9377e-159|极端显著
                ​统计显著性判断​：
                通常使用 ​α = 0.05​ 作为显著性水平阈值
                您的 p 值 (3.9377e-159) << 0.05
                ​结论​：拒绝原假设，接受备择假设
                ​实际意义​：
                这意味着您观察到的 0.941 强相关性极不可能是偶然发生的​
                您的模型预测值与实际值之间存在极其显著的线性关系​
                从统计上说，我们有非常充分的证据表明这两个变量确实相关。
                """
            ),
            HumanMessagePromptTemplate.from_template("需要分析的数据内容：{content}"),
        ]
        return messages


__all__ = ["AnalysisPromptCreator"]

if __name__ == "__main__":
    prompt = AnalysisPromptCreator.create_prompt()
    print(prompt.input_variables)  # ['content']

    prompt = AnalysisPromptCreator.create_prompt(
        message_templates=[
            HumanMessagePromptTemplate.from_template(
                template="请优化以下关键词: '{keywords}'"
            )
        ],
        histories=["这里是一条历史信息"],
    )
    print(prompt.input_variables)  # ['keywords', 'content']

    print(
        prompt.invoke(
            {
                "content": "data analysis",
                "keywords": "人工智能, 医疗影像; 智能诊断, 应用",
            }
        )
    )
