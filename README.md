# KRATOS — Inteligência Naval Estratégica (Backend Python)

Este projeto é o backend em Python do **KRATOS** (antigo AISStream Brasil App). Ele fornece endpoints REST, relay WebSocket e integração com AISStream, mantendo compatibilidade com o frontend existente.

## Tecnologias
- Python 3.10+
- FastAPI
- WebSockets
- python-dotenv

## Como rodar
1. Crie um arquivo `.env` com as variáveis necessárias (PORT, AIS_MODE, AISSTREAM_API_KEY, DEFAULT_AREA).
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

## Endpoints
- `/api/status` - Status do backend
- `/api/areas` - Áreas disponíveis
- `/api/mode` - Troca entre modo live/mock

## Observações
- O backend faz relay dos dados AIS para o frontend via WebSocket.
- O modo mock está disponível para testes locais.

Consulte o código e comentários para detalhes de implementação.

## Documentacao complementar
- Guia de documentacao (PT-BR): `DOCUMENTACAO_CODIGO_PTBR.md`
- Indice da pasta de docs: `docs/README.md`
- Contrato inicial da API: `docs/api/openapi.yaml`

## Licença e Copyright

**Copyright (c) 2026 Jossian Brito**

Este projeto é licenciado sob a **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.

- Uso comercial não é permitido sem autorização expressa prévia do autor.
- A atribuição ao autor original é obrigatória.

O texto completo da licença está no arquivo [LICENSE](LICENSE).