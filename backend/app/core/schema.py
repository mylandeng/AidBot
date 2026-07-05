from sqlalchemy import Engine, inspect, text


def ensure_runtime_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    if "knowledge_sources" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("knowledge_sources")}
    additions = {
        "space_id": "VARCHAR(36)",
        "content_format": "VARCHAR(24) NOT NULL DEFAULT 'markdown'",
        "filename": "VARCHAR(240) NOT NULL DEFAULT ''",
    }
    with engine.begin() as connection:
        for column_name, ddl in additions.items():
            if column_name not in columns:
                connection.execute(text(f"ALTER TABLE knowledge_sources ADD COLUMN {column_name} {ddl}"))
