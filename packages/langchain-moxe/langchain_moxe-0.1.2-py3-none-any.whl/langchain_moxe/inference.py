import requests


class MoxieAPI:
    BASE_URL = "https://api.bemoxie.ai"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "x-api-key": self.api_key
        }

    def _request(self, method: str, endpoint: str, params=None, data=None, json=None, extra_headers=None):
        url = f"{self.BASE_URL}{endpoint}"
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json
        )
        response.raise_for_status()
        return response.json()

    # ---------- INFERENCE ----------
    def list_inference_single(self):
        """GET /inference/single/list"""
        return self._request("GET", "/inference/single/list")

    def invoke_inference_single(self, prompt: str, model_name: str, args: dict, keep_context: bool = False):
        """POST /inference/single/invoke"""
        payload = {
            "prompt": prompt,
            "model_name": model_name,
            "args": args
        }
        extra_headers = {
            "Content-Type": "application/json",
            "keep-context": str(keep_context).lower()
        }
        return self._request("POST", "/inference/single/invoke", json=payload, extra_headers=extra_headers)

    def list_prompt_hub(self):
        """GET /inference/prompt-hub/list"""
        return self._request("GET", "/inference/prompt-hub/list")

    # ---------- EMBEDDING ----------
    def list_embeddings(self):
        """GET /embedding/list"""
        return self._request("GET", "/embedding/list")

    # ---------- MANAGEMENT ----------
    def get_quota(self):
        """GET /management/quota"""
        return self._request("GET", "/management/quota")


if __name__ == "__main__":
    api = MoxieAPI("aaZxh3VtGlkQz19qwUe51ULAUScWkPe2upHe9ic3")

    # exemplos de uso
    print("---- Inference Single ----")
    print(api.list_inference_single())

    print("---- Prompt Hub ----")
    print(api.list_prompt_hub())

    print("---- Embeddings ----")
    print(api.list_embeddings())

    print("---- Quota ----")
    print(api.get_quota())

    # exemplo de invocação
    result = api.invoke_inference_single(
        prompt="Escreva um haicai sobre tecnologia",
        model_name="phi4",
        args={
            "format": "json",
            "repeat_last_n": 0,
            "repeat_penalty": 0,
            "seed": 42,
            "stop": ["string"],
            "temperature": 0.7,
            "tfs_z": 0,
            "top_k": 40,
            "top_p": 0.9
        },
        keep_context=False
    )
    print(result)