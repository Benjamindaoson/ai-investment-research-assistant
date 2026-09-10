# Production Runbook

## 1) Build and Test
Run from repository root:

```powershell
.\.tools\apache-maven-3.9.12\bin\mvn.cmd -T 1C clean verify
```

## 2) Preflight Check

```powershell
.\scripts\preflight.ps1
```

If this is the final release gate:

```powershell
.\scripts\preflight.ps1 -StrictApi
```

## 3) Prepare Production Env File
Copy `.env.prod.example` to `.env.prod` and fill values.

```powershell
Copy-Item .env.prod.example .env.prod
```

## 3.1) Generate TLS Cert For Gateway
Generate a local certificate for `localhost`:

```powershell
.\scripts\generate-tls-cert.ps1 -Domain localhost
```

## 3.2) Migrate Plaintext Secrets To Files
Move plaintext secrets in `.env.prod` into `infra/secrets/*.txt` and auto-update `*_FILE` settings:

```powershell
.\scripts\migrate-secrets-to-files.ps1
```

## 4) Start Production Stack

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

## 5) Run Smoke Test

```powershell
.\scripts\smoke-test.ps1
```

Optional gateway path validation:

```powershell
.\scripts\smoke-test.ps1 -GatewayBase http://127.0.0.1:8080
```

HTTPS gateway validation (self-signed cert):

```powershell
.\scripts\smoke-test.ps1 -GatewayBase https://127.0.0.1:8443 -InsecureTls
```

## 6) Final Step: Configure Real API Keys
Do this last, immediately before cutover:

1. Set `APP_SECURITY_API_KEY` in `.env.prod` with a strong random value.
2. Set `OPENAI_API_KEY` in `.env.prod` (if AI external inference is required).
3. Optional: use secret files instead of plaintext values:
   - `APP_SECURITY_API_KEY_FILE`
   - `OPENAI_API_KEY_FILE`
   - `DB_PASSWORD_FILE`
   - `MAIL_PASSWORD_FILE`
   - Suggested local mount path: `infra/secrets/*.txt` (already gitignored)
3. Restart services:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

4. Re-run smoke test:

```powershell
.\scripts\smoke-test.ps1
```

## 7) Health Endpoints
- Web: `http://127.0.0.1:6060/actuator/health`
- MCP: `http://127.0.0.1:7070/actuator/health`
- Gateway: `http://127.0.0.1:8080/healthz`
- Gateway TLS: `https://127.0.0.1:8443/healthz`
- Gateway -> Web: `http://127.0.0.1:8080/actuator/health`
- Gateway -> MCP: `http://127.0.0.1:8080/mcp/actuator/health`
- Gateway TLS -> Web: `https://127.0.0.1:8443/actuator/health`
- Gateway TLS -> MCP: `https://127.0.0.1:8443/mcp/actuator/health`

## 8) Rollback
If release fails:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml down
```

Then redeploy last known good image/tag.
