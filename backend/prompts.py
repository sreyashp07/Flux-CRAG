"""Prompt templates for the Flux-CRAG nodes."""
from langchain_core.prompts import ChatPromptTemplate

GRADER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a strict relevance grader in a retrieval pipeline. "
            "Decide whether the retrieved document chunk contains information that helps "
            "answer the user's question. Keyword overlap alone is not enough: the chunk "
            "must contain facts, definitions or context that are useful for the answer. "
            "Respond with 'yes' or 'no' and one short reason.",
        ),
        ("human", "Question: {question}\n\nDocument chunk:\n{document}"),
    ]
)

REWRITER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You rewrite questions into concise, keyword-rich web search queries. "
            "Resolve ambiguity, expand abbreviations when helpful, and keep the original "
            "intent. Return ONLY the rewritten query on a single line, with no quotes "
            "and no explanation.",
        ),
        ("human", "Original question: {question}"),
    ]
)

GENERATOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a precise assistant that answers strictly from the provided context. "
            "Cite the context blocks you used with bracketed numbers such as [1] or [2]. "
            "If the context does not contain the answer, say you could not find it instead "
            "of guessing. Never invent facts. Keep the answer concise and well structured.",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)
