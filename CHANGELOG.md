# Changelog

## Unreleased

- Dev stack defaults to Zammad **7.2.2** (`7.2.2-0024`): Memcached, scheduler, websocket, PostgreSQL 17, Redis 8, and Elasticsearch 9. Zammad 7.1 stays a supported tag.

## 0.2.1

- `health_check` calls `GET /api/v1/users/me`. `get_server_info` calls `GET /api/v1/version`. The old `/ping` and `/system` paths are not Zammad endpoints.
- `create_article` and `create_ticket` accept `content_type` (`text/plain` or `text/html`) and send it to Zammad. Omitting it leaves Zammad's plain-text default.
- Article responses that use Zammad's `ticket_id` field parse again, so `get_ticket_articles` no longer fails after a successful read.
- `zammad-mcp-server login` runs the OAuth authorization-code callback on `http://127.0.0.1:8765/callback` and prints `ZAMMAD_OAUTH2_TOKEN`.
- Docs point at the live Zammad API introduction instead of the removed admin-docs API URLs.

## 0.2.0

- CLI: `--transport stdio|http|sse` with `MCP_TRANSPORT`, host, port, and path.
- Docker default is Streamable HTTP on port 8000; SSE remains a legacy override.
- Healthcheck uses a TCP listen probe (FastMCP has no `/health` route).
- Access control lists only registered tools (no ghost search tools).
- Tags, attachments, ticket links/merge, and `summarize_ticket`.
- Write-scope enforcement for `MCP_ALLOWED_GROUPS` / `MCP_ALLOWED_ORGANIZATIONS`.
- `MCP_DEFAULT_PERMISSION=read_only`, rate limits, JSON audit log on stderr/file.
- HTML-to-plain article bodies (`MCP_STRIP_HTML`, default on).
- Extra MCP prompts and resources.

## 0.1.1

- Production-ready MCP tools for Zammad 6.0+ / 7.x (tested on 7.1).
- PyPI (`uvx zammad-mcp-server`) and GHCR Docker publish.
