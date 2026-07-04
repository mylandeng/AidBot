import os
from pathlib import Path

TEST_DB = Path(__file__).with_name("aidbot-test.db")
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

from app import models  # noqa: E402, F401
from app.core.database import Base, engine  # noqa: E402

Base.metadata.create_all(bind=engine)
