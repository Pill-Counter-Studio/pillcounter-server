## Alembic

> For database migration, it should used with sqlalchemy

### Commands

- `cd ./src`
- `alembic init db_migration_tool`: Initialize my alembic project.
- `alembic revision --autogenerate -m "YOUR MESSAGE"`: Alembic will detect the entity model defined in `env.py`'s `target_metadata`, and it will automatically create upgrade and downgrade function. **But, we still need to manually check if the SQL is properly setup.**
- `alembic upgrade head`: Execute upgrade function in migration script, and update to latest(head).
- `alembic current`: Look up the current alembic version.
  ```
  INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
  INFO  [alembic.runtime.migration] Will assume transactional DDL.
  de8bb94a1dff (head)
  ```
- `alembic history`: List alembic history messages and versions.
  ```
  <base> -> de8bb94a1dff (head), Add available_predict_count column for User table
  ```
- `alembic downgrade <version>`: Downgrade to specific version.
  - `alembic downgrade -1`: Downgrade to previous version.
