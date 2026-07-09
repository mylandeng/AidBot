from sqlalchemy import Engine, inspect, text


def ensure_runtime_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.begin() as connection:
        if "knowledge_sources" in table_names:
            columns = {column["name"] for column in inspector.get_columns("knowledge_sources")}
            additions = {
                "space_id": "VARCHAR(36)",
                "content_format": "VARCHAR(24) NOT NULL DEFAULT 'markdown'",
                "filename": "VARCHAR(240) NOT NULL DEFAULT ''",
                "search_metadata": "JSON NOT NULL DEFAULT '{}'",
            }
            for column_name, ddl in additions.items():
                if column_name not in columns:
                    connection.execute(text(f"ALTER TABLE knowledge_sources ADD COLUMN {column_name} {ddl}"))

        if "knowledge_documents" in table_names:
            columns = {column["name"] for column in inspector.get_columns("knowledge_documents")}
            additions = {
                "sections": "JSON NOT NULL DEFAULT '[]'",
            }
            for column_name, ddl in additions.items():
                if column_name not in columns:
                    connection.execute(text(f"ALTER TABLE knowledge_documents ADD COLUMN {column_name} {ddl}"))

        if "knowledge_chunks" in table_names:
            columns = {column["name"] for column in inspector.get_columns("knowledge_chunks")}
            additions = {
                "section_path": "VARCHAR(500) NOT NULL DEFAULT ''",
                "section_content": "TEXT NOT NULL DEFAULT ''",
                "entities": "JSON NOT NULL DEFAULT '{}'",
                "embedding_provider": "VARCHAR(32) NOT NULL DEFAULT 'hash'",
                "embedding_model": "VARCHAR(120) NOT NULL DEFAULT 'hash-v1'",
                "embedding_dimensions": "INTEGER NOT NULL DEFAULT 96",
            }
            for column_name, ddl in additions.items():
                if column_name not in columns:
                    connection.execute(text(f"ALTER TABLE knowledge_chunks ADD COLUMN {column_name} {ddl}"))

        if "conversations" in table_names:
            columns = {column["name"] for column in inspector.get_columns("conversations")}
            if "status" not in columns:
                connection.execute(text("ALTER TABLE conversations ADD COLUMN status VARCHAR(24) NOT NULL DEFAULT 'active'"))
            if "retrieval_provider" not in columns:
                connection.execute(text("ALTER TABLE conversations ADD COLUMN retrieval_provider VARCHAR(24) NOT NULL DEFAULT 'local'"))
