"""
obsidian_supabase.py — Exportador base de notas Markdown para o Supabase Storage.

Sprint 1 da integração KRATOS + Obsidian (ver docs/PROPOSTA_OBSIDIAN_KRATOS.md).

Objetivo desta sprint: configurar a ponte cPanel -> Supabase Storage e conseguir
subir arquivos Markdown básicos para um bucket privado (ex.: ``kratos-vault``),
que depois é sincronizado no Obsidian local pelo plugin Remotely Save.

Decisões de implementação:
- Usa apenas a biblioteca padrão (``urllib``), sem dependências novas — importante
  porque o deploy é em cPanel e instalar pacotes (boto3) é frágil.
- O backend fala com o Supabase pela **API REST de Storage** usando a Service Key
  (Bearer). As chaves S3 (``SUPABASE_S3_*``) NÃO são usadas aqui: elas servem ao
  plugin Remotely Save no lado do Obsidian. Mantemo-las documentadas no ``.env``
  para o tutorial de configuração (Sprint 4), mas o upload server-side é REST.
- As notas geradas pelo KRATOS vivem sob um prefixo dedicado (``kratos/`` por
  padrão), separado das notas livres do usuário, para o sincronismo bidirecional
  do Remotely Save nunca sobrescrever edições manuais fora desse prefixo.

Funções principais:
- ``is_configured()``    -> bool
- ``config_status()``    -> dict (diagnóstico sem vazar segredos)
- ``upload_note(...)``   -> sobe um Markdown (síncrono)
- ``upload_note_async`` / ``check_connection_async`` -> wrappers para o loop async
- ``build_note(...)``    -> monta Markdown com frontmatter YAML
"""

import os
import json
import asyncio
import urllib.request
import urllib.error
from urllib.parse import quote
from datetime import datetime


# Prefixo (pasta) das notas geradas pelo KRATOS dentro do bucket.
DEFAULT_NOTE_PREFIX = "kratos"


def _clean(value: str | None) -> str:
    return (value or "").strip()


def get_config() -> dict:
    """Lê a configuração do Supabase a partir do ambiente.

    Backend (REST): precisa de ``SUPABASE_URL``, ``SUPABASE_KEY`` e
    ``SUPABASE_BUCKET``. As chaves S3 são lidas apenas para diagnóstico/tutorial.
    """
    url = _clean(os.getenv("SUPABASE_URL")).rstrip("/")
    return {
        "url": url,
        "key": _clean(os.getenv("SUPABASE_KEY")),
        "bucket": _clean(os.getenv("SUPABASE_BUCKET")) or "kratos-vault",
        "prefix": _clean(os.getenv("OBSIDIAN_NOTE_PREFIX")) or DEFAULT_NOTE_PREFIX,
        # Usadas pelo Obsidian (Remotely Save), não pelo backend:
        "s3_access_key": _clean(os.getenv("SUPABASE_S3_ACCESS_KEY")),
        "s3_secret_key": _clean(os.getenv("SUPABASE_S3_SECRET_KEY")),
    }


def is_configured() -> bool:
    """True quando o backend tem o mínimo para subir notas via REST."""
    cfg = get_config()
    return bool(cfg["url"] and cfg["key"] and cfg["bucket"])


def config_status() -> dict:
    """Diagnóstico seguro (não retorna segredos, apenas se estão presentes)."""
    cfg = get_config()
    return {
        "configured": is_configured(),
        "url": cfg["url"] or None,
        "bucket": cfg["bucket"],
        "prefix": cfg["prefix"],
        "hasKey": bool(cfg["key"]),
        "hasS3AccessKey": bool(cfg["s3_access_key"]),
        "hasS3SecretKey": bool(cfg["s3_secret_key"]),
    }


class ObsidianSupabaseError(RuntimeError):
    """Erro de configuração ou de comunicação com o Supabase Storage."""


def _normalize_object_path(path: str, prefix: str | None) -> str:
    """Resolve o caminho do objeto dentro do bucket, sob o prefixo do KRATOS.

    Caminhos que já comecem com o prefixo não são duplicados. Garante extensão
    ``.md`` por padrão.
    """
    rel = _clean(path).lstrip("/")
    if not rel:
        raise ObsidianSupabaseError("Caminho da nota vazio.")
    prefix = _clean(prefix)
    if prefix and not (rel == prefix or rel.startswith(prefix + "/")):
        rel = f"{prefix}/{rel}"
    if not rel.lower().endswith(".md"):
        rel = f"{rel}.md"
    return rel


def upload_note(path: str, markdown: str, *, content_type: str = "text/markdown; charset=utf-8",
                upsert: bool = True, timeout: float = 20.0) -> dict:
    """Sobe (ou sobrescreve) uma nota Markdown no bucket do Supabase Storage.

    Síncrono — use ``upload_note_async`` dentro do loop async do FastAPI.

    Retorna ``{"ok": True, "path": <object_path>, "bucket": ...}`` em caso de
    sucesso. Levanta ``ObsidianSupabaseError`` em falha de configuração/HTTP.
    """
    cfg = get_config()
    if not (cfg["url"] and cfg["key"] and cfg["bucket"]):
        raise ObsidianSupabaseError(
            "Supabase não configurado (defina SUPABASE_URL, SUPABASE_KEY e SUPABASE_BUCKET)."
        )

    object_path = _normalize_object_path(path, cfg["prefix"])
    # quote preservando as barras de diretório do objeto.
    encoded = quote(object_path, safe="/")
    endpoint = f"{cfg['url']}/storage/v1/object/{cfg['bucket']}/{encoded}"

    body = markdown.encode("utf-8")
    headers = {
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": content_type,
        # x-upsert: true permite criar e sobrescrever com o mesmo POST.
        "x-upsert": "true" if upsert else "false",
        "Cache-Control": "no-cache",
    }
    req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise ObsidianSupabaseError(
            f"HTTP {e.code} ao subir '{object_path}': {detail or e.reason}"
        ) from e
    except urllib.error.URLError as e:
        raise ObsidianSupabaseError(
            f"Falha de rede ao contactar Supabase: {e.reason}"
        ) from e

    return {
        "ok": True,
        "bucket": cfg["bucket"],
        "path": object_path,
        "response": _safe_json(raw),
    }


def _safe_json(raw: str):
    try:
        return json.loads(raw)
    except Exception:
        return raw or None


def build_note(title: str, body: str = "", *, frontmatter: dict | None = None,
               tags: list[str] | None = None) -> str:
    """Monta uma nota Markdown com frontmatter YAML simples.

    Não tenta cobrir YAML completo — apenas escalares e listas de strings, que é
    o suficiente para as notas do KRATOS.
    """
    fm: dict = {}
    if frontmatter:
        fm.update(frontmatter)
    if tags:
        fm["tags"] = list(tags)
    fm.setdefault("gerado_por", "KRATOS")
    fm.setdefault("atualizado_em", datetime.utcnow().isoformat())

    lines = ["---"]
    for key, value in fm.items():
        if isinstance(value, (list, tuple)):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {_yaml_scalar(item)}")
        else:
            lines.append(f"{key}: {_yaml_scalar(value)}")
    lines.append("---")
    lines.append("")
    if title:
        lines.append(f"# {title}")
        lines.append("")
    if body:
        lines.append(body)
    return "\n".join(lines).rstrip() + "\n"


def _yaml_scalar(value) -> str:
    """Serializa um escalar YAML, citando quando há caracteres especiais."""
    if value is None:
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "" or any(c in text for c in ':#[]{}",\n') or text.strip() != text:
        escaped = text.replace('"', '\\"')
        return f'"{escaped}"'
    return text


def check_connection(timeout: float = 20.0) -> dict:
    """Valida a configuração subindo uma nota de saúde no bucket.

    Útil para o botão/endpoint de teste do Exportador Base (Sprint 1).
    """
    note = build_note(
        "KRATOS — Teste de Conexão",
        "Esta nota confirma que o KRATOS consegue escrever no bucket do Supabase "
        "Storage. Pode ser apagada com segurança.",
        frontmatter={"tipo": "diagnostico"},
        tags=["kratos/sistema/health"],
    )
    result = upload_note("_sistema/health", note, timeout=timeout)
    result["message"] = "Conexão OK — nota de saúde gravada no bucket."
    return result


# --- Wrappers assíncronos (para uso dentro do loop do FastAPI) ----------------

async def upload_note_async(path: str, markdown: str, **kwargs) -> dict:
    return await asyncio.to_thread(upload_note, path, markdown, **kwargs)


async def check_connection_async(**kwargs) -> dict:
    return await asyncio.to_thread(check_connection, **kwargs)
