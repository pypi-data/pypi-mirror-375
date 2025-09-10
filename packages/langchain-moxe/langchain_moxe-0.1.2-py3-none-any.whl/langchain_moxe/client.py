import os
import json
import uuid
from typing import Any, Dict, Iterable, Optional, Union, List
import requests

MOXE_BASE_URL = os.getenv("MOXE_BASE_URL", "https://api.bemoxie.ai")


class MoxeClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 60):
        self.api_key = api_key or os.getenv("MOXE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing Moxe API key. Set MOXE_API_KEY or pass api_key='...'.")

        self.base_url = (base_url or MOXE_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "x-api-key": self.api_key,
        })

    # --------- helpers ----------
    def _request(
        self,
        method: str,
        endpoint: str,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False,
    ):
        url = f"{self.base_url}{endpoint}"
        hdrs = dict(self.session.headers)
        if headers:
            hdrs.update(headers)

        resp = self.session.request(
            method=method,
            url=url,
            json=json_body,
            params=params,
            headers=hdrs,
            timeout=self.timeout,
            stream=stream,
        )
        resp.raise_for_status()
        return resp

    # --------- inference single ----------
    def invoke_single(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        model_name: str,
        args: Optional[Dict[str, Any]] = None,
        keep_context: bool = False,
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "keep-context": "true" if keep_context else "false",
        }
        if thread_id:
            headers["thread-id"] = thread_id

        payload = {"prompt": prompt, "model_name": model_name}
        if args is not None:
            payload["args"] = args

        resp = self._request("POST", "/inference/single/invoke", json_body=payload, headers=headers)
        return resp.json()

    def stream_single(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        model_name: str,
        args: Optional[Dict[str, Any]] = None,
        keep_context: bool = False,
        thread_id: Optional[str] = None,
    ) -> Iterable[Dict[str, Any]]:
        headers = {
            "Content-Type": "application/json",
            "keep-context": "true" if keep_context else "false",
        }
        if thread_id:
            headers["thread-id"] = thread_id

        payload = {"prompt": prompt, "model_name": model_name}
        if args is not None:
            payload["args"] = args

        resp = self._request("POST", "/inference/single/stream", json_body=payload, headers=headers, stream=True)

        # SSE parse (bem simples; procura por linhas iniciadas com "data:")
        buffer = ""
        for line in resp.iter_lines(decode_unicode=True):
            if line is None:
                continue
            line = line.strip()
            if not line:
                # separador de evento
                if buffer:
                    try:
                        evt = json.loads(buffer)
                        yield evt
                    except Exception:
                        pass
                    buffer = ""
                continue
            if line.startswith("data:"):
                data = line[len("data:"):].strip()
                # alguns servidores mandam múltiplos "data:" para o mesmo evento
                if buffer:
                    # concatena JSONs válidos simples; se não der, fecha anterior
                    try:
                        _ = json.loads(buffer)
                        # já era um JSON completo; emite e substitui
                        yield json.loads(buffer)
                        buffer = data
                    except Exception:
                        buffer += data
                else:
                    buffer = data
            # linhas "event: data" não são estritamente necessárias aqui
        if buffer:
            try:
                yield json.loads(buffer)
            except Exception:
                pass

    # --------- embeddings ----------
    def embedding_generate(self, text: str, model_name: str) -> Dict[str, Any]:
        payload = {"data": text, "model_name": model_name}
        resp = self._request("POST", "/embedding/generate", json_body=payload)
        return resp.json()
