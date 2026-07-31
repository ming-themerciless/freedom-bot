# Database migrations

Run migrations with a migration-owner URL, never with the restricted runtime role:

```bash
DATABASE_URL='postgresql+psycopg://...' ./venv/bin/alembic upgrade head
```

Applied migrations are immutable. The initial migration is structurally
reversible while the database is empty; after operational data exists, recovery
uses a verified backup rather than a destructive production downgrade.
