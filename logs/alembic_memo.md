I'll help you set up Alembic to manage your database migrations and create tables. Since you're using Alembic with SQLAlchemy in your FastAPI application, here's how to do it:

1. First, make sure Alembic is installed:
```bash
pip install alembic
```

2. Initialize Alembic in your project (if not already done):
```bash
cd backend
alembic init alembic
```

3. Configure Alembic by updating `alembic.ini` in your project root to point to your database URL:
```ini
sqlalchemy.url = your_database_url
```

4. Create a new migration:
```bash
alembic revision --autogenerate -m "create tables"
```
This will automatically detect your SQLAlchemy models and create a migration script in the `alembic/versions` directory.

5. Apply the migration to create the tables:
```bash
alembic upgrade head
```

For your specific case, since you're dropping tables in tests (as seen in test_base.py), you'll want to ensure that your tables are recreated properly in your production/development environment. Here's how to modify your workflow:

```python:backend/tests/integration/test_base.py
# ... existing code ...

@pytest.fixture
def client():
    # This is fine for testing
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Drop all tables - this only happens in tests
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables for testing
    Base.metadata.create_all(bind=engine)
    
    # ... existing code ...
```

For your actual database (non-test environment), you should:

1. Make sure your models are properly defined in your SQLAlchemy models
2. Run Alembic migrations instead of using `Base.metadata.create_all()`
3. Never use `Base.metadata.drop_all()` in production

Common Alembic commands you'll need:

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current migration status
alembic current

# Show migration history
alembic history
```

Note: If you need to look at your project's specific Alembic configuration and migrations, you might want to try using agent mode, as it can look through your actual codebase to provide more specific guidance about your existing Alembic setup.

Remember to always backup your database before running migrations in production!
