from typing import Any, Dict, List, Optional
from langchain_core.language_models import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from .client import MoxeClient


class MoxeLLM(LLM):
    """LLM estilo completion (string → string) usando /inference/single."""

    model: str = "phi4"
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    seed: Optional[int] = None
    stop: Optional[List[str]] = None

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60

    @property
    def _llm_type(self) -> str:
        return "moxe-llm"

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
        return args

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        args = self._args_dict()
        if stop:
            args["stop"] = stop

        client = MoxeClient(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        resp = client.invoke_single(prompt=prompt, model_name=self.model, args=args if args else None)
        return resp.get("response", "")
