# ORM API Reference

This page provides detailed API documentation for fast-django's ORM components, which are re-exported from Tortoise ORM.

## Models

### `Model`

```python
class Model:
    # Base model class for all database models
```

Base model class for defining database models.

**Example:**
```python
from fast_django.orm import Model, fields

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)
```

## Fields

### Field Types

#### `IntField`

```python
IntField(pk: bool = False, null: bool = False, default: Any = None, unique: bool = False, index: bool = False, description: str = None)
```

Integer field for storing whole numbers.

**Parameters:**
- `pk` (bool): Primary key field.
- `null` (bool): Allow NULL values.
- `default` (Any): Default value.
- `unique` (bool): Unique constraint.
- `index` (bool): Create database index.
- `description` (str): Field description.

#### `CharField`

```python
CharField(max_length: int, null: bool = False, default: Any = None, unique: bool = False, index: bool = False, description: str = None)
```

Character field for storing strings with maximum length.

**Parameters:**
- `max_length` (int): Maximum string length.
- `null` (bool): Allow NULL values.
- `default` (Any): Default value.
- `unique` (bool): Unique constraint.
- `index` (bool): Create database index.
- `description` (str): Field description.

#### `TextField`

```python
TextField(null: bool = False, default: Any = None, description: str = None)
```

Text field for storing long text content.

**Parameters:**
- `null` (bool): Allow NULL values.
- `default` (Any): Default value.
- `description` (str): Field description.

#### `BooleanField`

```python
BooleanField(null: bool = False, default: bool = False, description: str = None)
```

Boolean field for storing true/false values.

**Parameters:**
- `null` (bool): Allow NULL values.
- `default` (bool): Default value.
- `description` (str): Field description.

#### `DateTimeField`

```python
DateTimeField(null: bool = False, default: Any = None, auto_now: bool = False, auto_now_add: bool = False, description: str = None)
```

DateTime field for storing date and time values.

**Parameters:**
- `null` (bool): Allow NULL values.
- `default` (Any): Default value.
- `auto_now` (bool): Update on every save.
- `auto_now_add` (bool): Set on creation only.
- `description` (str): Field description.

#### `ForeignKeyField`

```python
ForeignKeyField(model_name: str, related_name: str = None, null: bool = False, on_delete: str = "CASCADE", description: str = None)
```

Foreign key field for model relationships.

**Parameters:**
- `model_name` (str): Related model name.
- `related_name` (str): Reverse relationship name.
- `null` (bool): Allow NULL values.
- `on_delete` (str): On delete behavior.
- `description` (str): Field description.

#### `ManyToManyField`

```python
ManyToManyField(model_name: str, related_name: str = None, through: str = None, description: str = None)
```

Many-to-many field for model relationships.

**Parameters:**
- `model_name` (str): Related model name.
- `related_name` (str): Reverse relationship name.
- `through` (str): Through model name.
- `description` (str): Field description.

## Database Operations

### `Tortoise`

```python
class Tortoise:
    @staticmethod
    async def init(config: dict, generate_schemas: bool = False) -> None
    @staticmethod
    async def close_connections() -> None
    @staticmethod
    def get_connection(connection_name: str = "default") -> BaseDBAsyncClient
```

Tortoise ORM main class for database management.

**Methods:**
- `init(config)`: Initialize database connections.
- `close_connections()`: Close all database connections.
- `get_connection(name)`: Get database connection.

### `run_async`

```python
def run_async(coroutine: Coroutine) -> Any
```

Run async coroutine in sync context.

**Parameters:**
- `coroutine` (Coroutine): Async coroutine to run.

**Returns:**
- `Any`: Coroutine result.

## Query Operations

### Model Methods

#### `all()`

```python
async def all() -> QuerySet
```

Get all model instances.

**Returns:**
- `QuerySet`: Query set for all instances.

#### `get(**kwargs)`

```python
async def get(**kwargs) -> Model
```

Get single model instance by filters.

**Parameters:**
- `**kwargs`: Field filters.

**Returns:**
- `Model`: Model instance.

**Raises:**
- `DoesNotExist`: If no instance found.

#### `filter(**kwargs)`

```python
def filter(**kwargs) -> QuerySet
```

Filter model instances by field values.

**Parameters:**
- `**kwargs`: Field filters.

**Returns:**
- `QuerySet`: Filtered query set.

#### `create(**kwargs)`

```python
async def create(**kwargs) -> Model
```

Create new model instance.

**Parameters:**
- `**kwargs`: Field values.

**Returns:**
- `Model`: Created model instance.

#### `bulk_create(objects: list[Model])`

```python
async def bulk_create(objects: list[Model]) -> list[Model]
```

Create multiple model instances efficiently.

**Parameters:**
- `objects` (list[Model]): List of model instances.

**Returns:**
- `list[Model]`: Created model instances.

### QuerySet Methods

#### `order_by(*fields)`

```python
def order_by(*fields: str) -> QuerySet
```

Order query set by fields.

**Parameters:**
- `*fields` (str): Field names to order by.

**Returns:**
- `QuerySet`: Ordered query set.

#### `limit(count: int)`

```python
def limit(count: int) -> QuerySet
```

Limit number of results.

**Parameters:**
- `count` (int): Maximum number of results.

**Returns:**
- `QuerySet`: Limited query set.

#### `offset(count: int)`

```python
def offset(count: int) -> QuerySet
```

Skip number of results.

**Parameters:**
- `count` (int): Number of results to skip.

**Returns:**
- `QuerySet`: Offset query set.

#### `prefetch_related(*fields)`

```python
def prefetch_related(*fields: str) -> QuerySet
```

Prefetch related objects to avoid N+1 queries.

**Parameters:**
- `*fields` (str): Related field names.

**Returns:**
- `QuerySet`: Query set with prefetched relations.

#### `update(**kwargs)`

```python
async def update(**kwargs) -> int
```

Update all instances in query set.

**Parameters:**
- `**kwargs`: Field updates.

**Returns:**
- `int`: Number of updated instances.

#### `delete()`

```python
async def delete() -> int
```

Delete all instances in query set.

**Returns:**
- `int`: Number of deleted instances.

## Instance Methods

### `save()`

```python
async def save() -> None
```

Save model instance to database.

### `delete()`

```python
async def delete() -> None
```

Delete model instance from database.

### `update_from_dict(data: dict)`

```python
def update_from_dict(data: dict) -> None
```

Update instance fields from dictionary.

**Parameters:**
- `data` (dict): Field values dictionary.

## Relationships

### Foreign Key

```python
# Access related object
user = await User.get(id=1)
posts = await user.posts.all()

# Create with related object
post = await Post.create(title="Hello", author=user)
```

### Many-to-Many

```python
# Add related objects
post = await Post.get(id=1)
tag = await Tag.get(name="python")
await post.tags.add(tag)

# Remove related objects
await post.tags.remove(tag)

# Clear all related objects
await post.tags.clear()

# Get related objects
tags = await post.tags.all()
```

## Transactions

### `in_transaction`

```python
async def in_transaction() -> AsyncContextManager
```

Transaction context manager.

**Example:**
```python
from fast_django.orm import in_transaction

async with in_transaction():
    user = await User.create(username="john")
    post = await Post.create(title="Hello", author=user)
```

## Exceptions

### `DoesNotExist`

```python
class DoesNotExist(Exception):
    pass
```

Raised when model instance is not found.

### `IntegrityError`

```python
class IntegrityError(Exception):
    pass
```

Raised when database integrity constraint is violated.

### `ValidationError`

```python
class ValidationError(Exception):
    pass
```

Raised when model validation fails.
