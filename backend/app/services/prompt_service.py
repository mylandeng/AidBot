from dataclasses import dataclass


SUPPORT_SYSTEM_INSTRUCTION = (
    "你是企业内部售后知识助手。请用简洁中文回答售后排查问题。"
    "只能依据给定知识库片段和客户问题作答；知识库没有覆盖时要明确说需要人工复核，可以咨询林工(qq:1960184996@qq.com)。"
    "不要编造引用来源、文档编号、政策条款或工单编号。"
    "知识库片段可能来自Markdown文档；只提取事实，不得复制标题、加粗、编号清单、表格或原文段落结构。"
    "把内容改写成客服可直接发送的自然语言；如需步骤，只使用简短中文句子。"
    "不要输出JSON、Markdown表格或长篇文档，只输出适合客服阅读的自然语言回答。"
)


@dataclass(frozen=True)
class SupportPrompt:
    system_instruction: str
    product_line: str
    knowledge_context: str
    customer_question: str

    def user_instruction(self) -> str:
        return f"产品线：{self.product_line}\n\n知识库片段：\n{self.knowledge_context}\n\n客户问题：{self.customer_question}"


def build_support_prompt(question: str, product_line: str | None = None, context: str | None = None) -> SupportPrompt:
    return SupportPrompt(
        system_instruction=SUPPORT_SYSTEM_INSTRUCTION,
        product_line=product_line or "未指定产品线",
        knowledge_context=context.strip() if context else "当前没有命中的知识库片段。",
        customer_question=question,
    )
