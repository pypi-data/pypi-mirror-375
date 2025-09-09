# Vention Storage

A framework for storing and managing component and application data with persistence, validation, and audit trails for machine applications.

## 🎯 Overview

Vention Storage provides a modular, component-based storage system that offers:

- **🔒 Persistent Data Storage** - Data survives reboots with SQLite
- **🔄 Automatic Audit Trails** - Track who made changes and when
- **🛡️ Strong Type Safety** - Full type hints and validation
- **⚡ Lifecycle Hooks** - Before/after insert/update/delete operations
- **🗑️ Soft Delete Support** - Optional soft deletion with `deleted_at` fields
- **🌐 REST API Endpoints** - Automatic CRUD API generation with audit trails
- **📊 Database Health & Monitoring** - Health checks and database schema visualization
- **Batch Operations** - Efficient bulk insert/delete operations
- **Session Management** - Smart session reuse and transaction handling
- **🚀 Bootstrap System** - One-command setup for entire storage system
- **📊 CSV Export/Import** - Easy data backup and migration
- **💾 Database Backup/Restore** - Full SQLite backup and restore functionality

### Basic Usage

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from storage import database
from storage.accessor import ModelAccessor
from storage.router_model import build_crud_router
from storage.router_database import build_db_router
from storage.bootstrap import bootstrap
from fastapi import FastAPI

# 1. Define your models
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    deleted_at: Optional[datetime] = Field(default=None, index=True)  # Optional soft delete

# 2. Quick setup with bootstrap
app = FastAPI()
user_accessor = ModelAccessor(User, "users")

bootstrap(
    app,
    accessors=[user_accessor],
    database_url="sqlite:///./my_app.db",
    create_tables=True
)

# Now you have full CRUD API at /users with audit trails, backup/restore, and CSV export!
```

## 🚀 Bootstrap System

The `bootstrap` function provides a convenient way to set up the entire storage system for a FastAPI application:

```python
from fastapi import FastAPI
from storage.bootstrap import bootstrap
from storage.accessor import ModelAccessor

app = FastAPI()

# Define your accessors
user_accessor = ModelAccessor(User, "users")
product_accessor = ModelAccessor(Product, "products")

# Bootstrap the entire system
bootstrap(
    app,
    accessors=[user_accessor, product_accessor],
    database_url="sqlite:///./my_app.db",
    create_tables=True,
    max_records_per_model=100,
    enable_db_router=True
)
```

### Bootstrap Features

- **Automatic database setup** with optional table creation
- **CRUD router generation** for all registered accessors
- **Database monitoring endpoints** (health, audit, diagram)
- **Configurable record limits** to prevent abuse
- **Optional database URL override**

## 📊 CSV Export

Export your entire database as CSV files for backup and migration:

```python
# Export all tables as CSV
response = requests.get("http://localhost:8000/db/export.zip")
with open("backup.zip", "wb") as f:
    f.write(response.content)
```

The export creates a ZIP file containing one CSV file per table, with proper handling of datetime fields and data types.

## 💾 Backup & Restore

Full database backup and restore functionality using SQLite's native backup API:

### Backup
```python
# Create a complete database backup
response = requests.get("http://localhost:8000/db/backup.sqlite")
with open("backup.sqlite", "wb") as f:
    f.write(response.content)
```

### Restore
```python
# Restore from a backup file
with open("backup.sqlite", "rb") as f:
    files = {"file": ("backup.sqlite", f, "application/x-sqlite3")}
    response = requests.post(
        "http://localhost:8000/db/restore",
        files=files,
        params={"integrity_check": True, "dry_run": False}
    )
```

### Backup/Restore Features

- **Atomic operations** - Database replacement is atomic to prevent corruption
- **Integrity checking** - Optional PRAGMA integrity_check before restore
- **Dry run mode** - Validate backup files without actually restoring
- **Consistent backups** - Uses SQLite's backup API for data consistency
- **Automatic engine disposal** - Properly handles database connections during restore

## 🔧 Core Components

### Database Management

```python
from storage import database

# Configure database URL (must be called before first use)
database.set_database_url("sqlite:///./my_app.db")

# Get the engine
engine = database.get_engine()

# Use transactions for atomic operations
with database.transaction() as session:
    # All operations in this block are atomic
    user1 = user_accessor.insert(User(name="Alice"), actor="system")
    user2 = user_accessor.insert(User(name="Bob"), actor="system")
    # If any operation fails, both are rolled back
```

### Model Accessors

The `ModelAccessor` provides a strongly-typed interface for CRUD operations:

```python
# Create accessor for your model
accessor = ModelAccessor(MyModel, "component_name")

# Basic CRUD operations
obj = accessor.insert(MyModel(...), actor="user")
obj = accessor.get(123)
obj = accessor.save(updated_obj, actor="user")
success = accessor.delete(123, actor="user")

# Batch operations
objects = accessor.insert_many([MyModel(...), MyModel(...)], actor="user")
deleted_count = accessor.delete_many([123, 456], actor="user")

# Soft delete operations
success = accessor.restore(123, actor="user")  # Only for models with deleted_at
```

### Lifecycle Hooks

Register hooks to run before/after operations:

```python
@accessor.before_insert()
def validate_email(session, instance):
    """Enforce schema-level validation (safe here)."""
    if not instance.email or "@" not in instance.email:
        raise ValueError("Invalid email")

@accessor.after_insert()
def log_creation(session, instance):
    """Lightweight side-effect: write to a log or metrics system."""
    print(f"Row created in {session.bind.url}: {instance}")

# Hooks run in the same transaction as the operation
# If a hook fails, the entire operation is rolled back
```

### Audit Trails

All operations are automatically audited:

```python
from storage.auditor import AuditLog
from sqlmodel import select

# Audit logs are automatically created for all operations
with database.transaction() as session:
    # This operation will be audited
    user = user_accessor.insert(User(name="Alice"), actor="admin")
    
    # Query audit logs
    logs = session.exec(select(AuditLog).where(AuditLog.component == "users")).all()
    for log in logs:
        print(f"{log.timestamp}: {log.operation} by {log.actor}")
        print(f"  Before: {log.before}")
        print(f"  After: {log.after}")
```

## 🌐 REST API Generation

### Automatic CRUD Endpoints

The `build_crud_router` function automatically generates full CRUD endpoints for any model:

```python
from storage.router_model import build_crud_router
from fastapi import FastAPI

app = FastAPI()

# Create router for User model
user_router = build_crud_router(user_accessor)
app.include_router(user_router)

# Automatically generates these endpoints:
# GET    /users/           - List all users
# GET    /users/{id}       - Get specific user
# POST   /users/           - Create new user
# PUT    /users/{id}       - Update user
# DELETE /users/{id}       - Delete user
# POST   /users/{id}/restore - Restore soft-deleted user
```

### API Features

- **Automatic validation** using your SQLModel schemas
- **Audit trails** for all operations (requires `X-User` header, which is used to identify users in the audit trail)
- **Soft delete support** for models with `deleted_at` fields
- **Configurable record limits** to prevent abuse
- **Proper HTTP status codes** and error handling
- **OpenAPI documentation** automatically generated

### Usage Example

```python
import requests

# Create user, X-User is the user who will be blamed in the audit log: Operator, Supervisor, Admin, etc.
response = requests.post(
    "http://localhost:8000/users/",
    json={"name": "Alice", "email": "alice@example.com"},
    headers={"X-User": "admin"}
)
user = response.json()

# Update user
response = requests.put(
    f"http://localhost:8000/users/{user['id']}",
    json={"name": "Alice Smith"},
    headers={"X-User": "admin"}
)

# List users
response = requests.get("http://localhost:8000/users/")
users = response.json()

# Soft delete user
requests.delete(f"http://localhost:8000/users/{user['id']}", headers={"X-User": "admin"})

# Restore user
requests.post(f"http://localhost:8000/users/{user['id']}/restore", headers={"X-User": "admin"})
```

### Database Health & Monitoring

The `build_db_router` function provides database health and monitoring endpoints:

```python
from storage.router_database import build_db_router

app.include_router(build_db_router())

# Available endpoints:
# GET /db/health     - Database health check
# GET /db/audit      - Query audit logs with filters
# GET /db/diagram.svg - Database schema visualization
# GET /db/export.zip - Export all tables as CSV
# GET /db/backup.sqlite - Full database backup
# POST /db/restore   - Restore from backup file
```

### Audit Log Querying

```python
# Query audit logs with filters
response = requests.get("http://localhost:8000/db/audit", params={
    "component": "users",
    "operation": "create",
    "actor": "admin",
    "since": "2023-01-01T00:00:00Z",
    "limit": 100,
    "offset": 0
})

audit_logs = response.json()
```

### Database Schema Visualization

```python
# Get database schema as SVG diagram
response = requests.get("http://localhost:8000/db/diagram.svg")
# Returns SVG image of your database schema
# Requires sqlalchemy-schemadisplay and Graphviz
```

## API Reference

### Bootstrap Function

```python
def bootstrap(
    app: FastAPI,
    *,
    accessors: Iterable[ModelAccessor[Any]],
    database_url: Optional[str] = None,
    create_tables: bool = True,
    max_records_per_model: Optional[int] = 5,
    enable_db_router: bool = True,
) -> None:
    """Bootstrap the storage system for a FastAPI app."""
```

### ModelAccessor

#### Constructor
```python
ModelAccessor(model: Type[ModelType], component_name: str)
```

#### Read Operations
```python
# Get single record
accessor.get(id: int, *, include_deleted: bool = False) -> Optional[ModelType]

# Get all records
accessor.all(*, include_deleted: bool = False) -> List[ModelType]
```

#### Write Operations
```python
# Insert new record
accessor.insert(obj: ModelType, *, actor: str = "internal") -> ModelType

# Save record (insert if new, update if exists)
accessor.save(obj: ModelType, *, actor: str = "internal") -> ModelType

# Delete record
accessor.delete(id: int, *, actor: str = "internal") -> bool

# Restore soft-deleted record
accessor.restore(id: int, *, actor: str = "internal") -> bool
```

#### Batch Operations
```python
# Insert multiple records
accessor.insert_many(objs: Sequence[ModelType], *, actor: str = "internal") -> List[ModelType]

# Delete multiple records
accessor.delete_many(ids: Sequence[int], *, actor: str = "internal") -> int
```

#### Hook Decorators
```python
@accessor.before_insert()
@accessor.after_insert()
@accessor.before_update()
@accessor.after_update()
@accessor.before_delete()
@accessor.after_delete()
```

### Router Functions

#### build_crud_router
```python
def build_crud_router(
    accessor: ModelAccessor[ModelType],
    *,
    max_records: Optional[int] = 100
) -> APIRouter:
    """Generate CRUD router for a model with audit trails."""
```

#### build_db_router
```python
def build_db_router(
    *,
    audit_default_limit: int = 100,
    audit_max_limit: int = 1000
) -> APIRouter:
    """Generate database health and monitoring router."""
```

### Database Management

```python
# Configure database URL
database.set_database_url(url: str) -> None

# Get database engine
database.get_engine() -> Engine

# Transaction context manager
database.transaction() -> Iterator[Session]

# Session context manager
database.use_session(session: Optional[Session] = None) -> Iterator[Session]
```

## 🔍 Audit System

### AuditLog Model

```python
class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(index=True)
    component: str = Field(index=True)
    record_id: int = Field(index=True)
    operation: str
    actor: str
    before: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    after: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
```

### Querying Audit Logs

```python
from storage.auditor import AuditLog
from sqlmodel import select

# Get all audit logs for a component
logs = session.exec(select(AuditLog).where(AuditLog.component == "users")).all()

# Get audit logs for a specific record
logs = session.exec(select(AuditLog).where(AuditLog.record_id == 123)).all()

# Get audit logs by operation type
logs = session.exec(select(AuditLog).where(AuditLog.operation == "create")).all()

# Get audit logs by actor
logs = session.exec(select(AuditLog).where(AuditLog.actor == "admin")).all()
```

### Audit Log API Endpoints

```python
# Query audit logs via REST API
GET /db/audit?component=users&operation=create&actor=admin&limit=100

# Query parameters:
# - component: Filter by component name
# - record_id: Filter by specific record ID
# - actor: Filter by user who made the change
# - operation: Filter by operation type (create, update, delete, etc.)
# - since: Filter records since this timestamp
# - until: Filter records until this timestamp
# - limit: Maximum number of records to return (1-1000)
# - offset: Number of records to skip for pagination
```

## Dependencies

- **SQLModel**: Modern SQL database toolkit for Python
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping library
- **FastAPI**: Modern web framework for building APIs
- **sqlalchemy-schemadisplay**: Database schema visualization (optional)
- **Graphviz**: Graph visualization software (optional, for schema diagrams)
- **Python 3.9+**: Required for type hints and modern Python features