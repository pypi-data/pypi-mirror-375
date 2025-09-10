from typing import List, Dict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


def lc_to_moxe_messages(messages: List[BaseMessage]) -> List[Dict[str, str]]:
    out = []
    for m in messages:
        if isinstance(m, HumanMessage):
            role = "user"   # a API aceita "human" ou "user"; usamos "user"
        elif isinstance(m, AIMessage):
            role = "assistant"  # ou "ai"
        elif isinstance(m, SystemMessage):
            role = "system"
        else:
            # fallback genérico
            role = "user"
        out.append({"role": role, "content": m.content})
    return out
