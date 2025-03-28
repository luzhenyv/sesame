import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base_class import Base
from app.db.session import get_db
from app.main import app
from app.core.config import settings
import pytest

SQLALCHEMY_DATABASE_URL = settings.get_database_url


@pytest.fixture
def client():
    # Create the database engine
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Drop all tables
    Base.metadata.drop_all(bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)
    test_db = TestingSessionLocal()

    yield test_client

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    test_db.close()


@pytest.fixture
def db_session(client):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


class TestBase:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.client = client
        yield

    def get_auth_headers(self, email="test@example.com", password="testpassword123"):
        # Register user if not exists
        self.client.post(
            f"{settings.API_V1_STR}/auth/register",
            json={"email": email, "password": password, "full_name": "Test User"},
        )

        # Login to get token
        response = self.client.post(
            f"{settings.API_V1_STR}/auth/token",
            data={"username": email, "password": password},
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
