from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, Union

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun

from .client import MoxeClient
from .utils import lc_to_moxe_messages


class ChatMoxe(BaseChatModel):
    """LangChain ChatModel para a Moxe (inference single)."""

    model: str = "phi4"
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    seed: Optional[int] = None
    stop: Optional[List[str]] = None
    repeat_last_n: Optional[int] = None
    repeat_penalty: Optional[float] = None
    tfs_z: Optional[float] = None
    format: Optional[str] = None  # "json" ou JSON Schema (ver docs Moxe)

    keep_context: bool = False
    thread_id: Optional[str] = None

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60

    # pydantic v2: evitar validação extra detalhada aqui
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def _llm_type(self) -> str:
        return "moxe-chat"

    # ---- args -> payload.args ----
    def _args_dict(self) -> Dict[str, Any]:
        args: Dict[str, Any] = {}
        if self.temperature is not None:
            args["temperature"] = self.temperature
        if self.top_p is not None:
            args["top_p"] = self.top_p
        if self.top_k is not None:
            args["top_k"] = self.top_k
        if self.seed is not None:
            args["seed"] = self.seed
        if self.stop is not None:
            args["stop"] = self.stop
        if self.repeat_last_n is not None:
            args["repeat_last_n"] = self.repeat_last_n
        if self.repeat_penalty is not None:
            args["repeat_penalty"] = self.repeat_penalty
        if self.tfs_z is not None:
            args["tfs_z"] = self.tfs_z
        if self.format is not None:
            args["format"] = self.format
        return args

    def _client(self) -> MoxeClient:
        return MoxeClient(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    # -------- non-stream --------
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        prompt = lc_to_moxe_messages(messages)
        args = self._args_dict()
        # prioridade ao stop passado no invoke()
        if stop:
            args["stop"] = stop

        client = self._client()
        resp = client.invoke_single(
            prompt=prompt,
            model_name=self.model,
            args=args if args else None,
            keep_context=self.keep_context,
            thread_id=self.thread_id,
        )

        text = resp.get("response", "")
        usage = resp.get("usage", {}) or {}
        gen = ChatGeneration(message=AIMessage(content=text), generation_info={"moxe": resp, "usage": usage})
        return ChatResult(generations=[gen])

    # -------- streaming --------
    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterable[ChatGenerationChunk]:
        prompt = lc_to_moxe_messages(messages)
        args = self._args_dict()
        if stop:
            args["stop"] = stop

        client = self._client()
        for evt in client.stream_single(
                prompt=prompt,
                model_name=self.model,
                args=args if args else None,
                keep_context=self.keep_context,
                thread_id=self.thread_id,
        ):
            # Espera eventos tipo: {"type": "message"|"final_answer"|"usage"|"error", "data": ...}
            evt_type = evt.get("type")
            data = evt.get("data")

            if evt_type in ("message", "final_answer"):
                # 'data' pode vir como string ou objeto; usamos string quando possível
                chunk_text = data if isinstance(data, str) else (data or "")
                if chunk_text:
                    if run_manager:
                        run_manager.on_llm_new_token(chunk_text)
                    # >>> AQUI o ajuste principal: usar AIMessageChunk
                    yield ChatGenerationChunk(message=AIMessageChunk(content=chunk_text))

            elif evt_type == "error":
                # Opcional: propagar para callbacks
                err_text = data if isinstance(data, str) else (data or "")
                if err_text and run_manager:
                    run_manager.on_llm_new_token(f"[MOXE ERROR] {err_text}")

            else:
                # usage / outros -> ignore no stream (pode guardar em estado se quiser)
                continue
