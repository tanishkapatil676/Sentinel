# Sentinel Configuration Reference

## Environment Variables
| Variable | Type | Default | Description | Sensitivity |
| :--- | :--- | :--- | :--- | :--- |
| `APP_NAME` | String | `Sentinel` | Name of the application instance | Public |
| `ENVIRONMENT` | String | `development` | Deployment environment mode | Public |
| `LOG_LEVEL` | String | `INFO` | Application logging verbosity | Public |
| `HOST` | String | `0.0.0.0` | Bind host for Uvicorn ASGI server | Public |
| `PORT` | Integer | `8000` | Bind port for Uvicorn ASGI server | Public |
| `DATABASE_URL` | String | `postgresql+asyncpg://...` | Async PostgreSQL connection string | **Secret** |
| `REDIS_URL` | String | `redis://localhost:6379/0` | Redis broker connection string | **Secret** |

## Security Rules
- Secrets must never be committed to source control or logged.
- Production environments must explicitly configure secure credentials.
