# bics-chatbot

Chatbot em Python para **apontar defeitos em trechos de código** e sugerir correções rápidas.
Foco inicial: **erros sintáticos** comuns (inspirados no BICS) e heurísticas locais, com caminho livre
para plugar um LLM posteriormente.

## ⚙️ Instalação (dev)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pre-commit install
```

## 🧪 Rodando testes e lint

```bash
pytest -q
ruff check .
black --check .
```

## 🚀 Usando via CLI

```bash
python -m codebug_bot.cli --file examples/broken_missing_colon.py --apply-fix
```

## 🌐 API (FastAPI)

```bash
uvicorn codebug_bot.server:app --reload
# POST http://127.0.0.1:8000/analyze  body: {"code": "SEU_CODIGO_AQUI", "apply_fix": true}
```

## 🧰 Como funciona (resumo)

1. Tentamos fazer `ast.parse(code)`. Se houver `SyntaxError`, classificamos a falha em tipos comuns:
   - `missing_colon`, `missing_parenthesis`, `missing_quotation`, `mismatched_bracket`.
2. Aplicamos **heurísticas** para sugerir uma **correção mínima** e retornamos `fixed_code` quando possível.
3. Mesmo quando `ast.parse` passa, rodamos checagens leves (contagem de parênteses/aspas) para flaggar riscos.

> Limites: heurísticas não “entendem” semântica. Para bugs lógicos, plugue um LLM em `codebug_bot/llm.py`.

## 📦 Dataset (opcional)

O script `scripts/prepare_dataset.py` explica como baixar e limpar o dataset
[`iamtarun/python_code_instructions_18k_alpaca`](https://huggingface.co/datasets/iamtarun/python_code_instructions_18k_alpaca)
para gerar um **corpus** local de trechos Python válidos.

## 🤝 Contribuindo

- Veja `CONTRIBUTING.md` e o template de PR. Use uma branch por feature, commits pequenos e descritivos.
- O CI roda lint + testes.

## 📝 Licença

MIT.
