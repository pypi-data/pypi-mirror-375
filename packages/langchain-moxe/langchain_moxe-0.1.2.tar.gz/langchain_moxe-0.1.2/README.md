# langchain-moxe

Este pacote fornece a integração oficial do **LangChain** com os modelos generativos da **Moxe**.  
Com ele, você pode usar os modelos de chat, completions e embeddings da Moxe dentro dos fluxos do LangChain.

---

## 🚀 Instalação

```bash
pip install -U langchain-moxe
```

🔑 Configuração da chave de API  
Antes de utilizar, configure sua chave de API da Moxe como variável de ambiente:

```bash
export MOXE_API_KEY="sua-chave-aqui"
```

Ou defina diretamente no código ao instanciar o cliente:

```python
chat = ChatMoxe(model="phi4", api_key="sua-chave-aqui")
```

## 💬 Uso com Modelos de Chat

Os modelos de chat são recomendados para a maioria dos casos de uso.  
Eles permitem interações mais ricas e suporte a mensagens com diferentes papéis (system, user, assistant).

### Exemplo simples

```python
from langchain_moxe import ChatMoxe
from langchain_core.messages import HumanMessage, SystemMessage

chat = ChatMoxe(model="phi4", temperature=0.7)

response = chat.invoke([
    SystemMessage(content="Você é um assistente criativo e útil."),
    HumanMessage(content="Escreva um haicai sobre tecnologia.")
])

print(response.content)
```

### Exemplo com streaming

```python
from langchain_moxe import ChatMoxe
from langchain_core.messages import HumanMessage

chat = ChatMoxe(model="phi4", temperature=0.7)

for chunk in chat.stream([HumanMessage(content="Resuma LangChain em 1 frase.")]):
    print(chunk.content, end="", flush=True)

print()
```

## ✍️ Uso como LLM (modo completion)

Também é possível utilizar os modelos da Moxe como completions de texto (input string → output string).

```python
from langchain_moxe import MoxeLLM

llm = MoxeLLM(model="phi4", temperature=0.3)

response = llm.invoke("Complete a frase: Python é ótimo para")

print(response)
```

## 🔎 Embeddings

A Moxe também fornece modelos de embeddings para busca semântica e indexação.

```python
from langchain_moxe import MoxeEmbeddings

emb = MoxeEmbeddings(model="text-embedding-001")

vector = emb.embed_query("busca semântica em documentos")

print("Dimensão do embedding:", len(vector))
```

Também é possível gerar embeddings para uma lista de textos:

```python
embeddings = emb.embed_documents([
    "Primeiro documento",
    "Segundo documento",
    "Terceiro documento"
])

print(len(embeddings), "vetores gerados")
```

## ⚙️ Parâmetros suportados

Você pode controlar a geração dos modelos passando parâmetros compatíveis com a API da Moxe:

- **temperature**: controla a criatividade da resposta.
- **top_p**: nucleus sampling (probabilidade acumulada).
- **top_k**: restringe a escolha de tokens aos K mais prováveis.
- **seed**: define a semente aleatória para respostas reproduzíveis.
- **stop**: lista de tokens de parada.
- **repeat_last_n**: janela de tokens considerada para penalidade de repetição.
- **repeat_penalty**: força da penalidade de repetição.
- **tfs_z**: tail free sampling.
- **format**: formato da saída (ex.: "json" ou schema JSON).

### Exemplo

```python
chat = ChatMoxe(
    model="phi4",
    temperature=0.5,
    top_p=0.9,
    stop=["\n"]
)
```

## 📚 Recursos adicionais

- Documentação da Moxe
- Documentação do LangChain

## 📄 Licença

Este projeto é distribuído sob a licença MIT.
