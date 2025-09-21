# ORM

fast-django uses Tortoise ORM, providing a Django-like ORM experience with async support. All Tortoise ORM components are re-exported through `fast_django.orm` for convenience.

## Quick Start

```python
from fast_django.orm import Model, fields, Tortoise, run_async

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    is_published = fields.BooleanField(default=False)
```

## Models

### Basic Model Definition

```python
from fast_django.orm import Model, fields

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)
```

### Field Types

fast-django supports all Tortoise ORM field types:

#### Text Fields
```python
# CharField with max length
title = fields.CharField(max_length=200)

# TextField for longer content
content = fields.TextField()

# JSONField for structured data
metadata = fields.JSONField(default=dict)
```

#### Numeric Fields
```python
# Integer fields
id = fields.IntField(pk=True)
age = fields.IntField(null=True)

# Float fields
price = fields.FloatField()
rating = fields.FloatField(null=True)

# Decimal fields
amount = fields.DecimalField(max_digits=10, decimal_places=2)
```

#### Date/Time Fields
```python
# DateTime fields
created_at = fields.DatetimeField(auto_now_add=True)
updated_at = fields.DatetimeField(auto_now=True)
published_at = fields.DatetimeField(null=True)

# Date fields
birth_date = fields.DateField(null=True)

# Time fields
start_time = fields.TimeField(null=True)
```

#### Boolean Fields
```python
is_active = fields.BooleanField(default=True)
is_verified = fields.BooleanField(default=False)
```

#### Foreign Key Relationships
```python
class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    category = fields.ForeignKeyField('models.Category', related_name='posts')
    author = fields.ForeignKeyField('models.User', related_name='posts')
```

#### Many-to-Many Relationships
```python
class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    tags = fields.ManyToManyField('models.Tag', related_name='posts')
```

## Database Operations

### Creating Records

```python
# Create a single record
user = await User.create(
    username="john_doe",
    email="john@example.com"
)

# Create multiple records
users = await User.bulk_create([
    User(username="user1", email="user1@example.com"),
    User(username="user2", email="user2@example.com"),
])
```

### Querying Records

```python
# Get all records
all_users = await User.all()

# Get a single record
user = await User.get(id=1)

# Get with error handling
try:
    user = await User.get(username="john_doe")
except DoesNotExist:
    print("User not found")

# Filter records
active_users = await User.filter(is_active=True)
recent_users = await User.filter(created_at__gte=datetime.now() - timedelta(days=7))

# Ordering
users = await User.all().order_by('-created_at')

# Limiting
recent_users = await User.all().order_by('-created_at').limit(10)
```

### Updating Records

```python
# Update a single record
user = await User.get(id=1)
user.email = "newemail@example.com"
await user.save()

# Bulk update
await User.filter(is_active=False).update(is_active=True)

# Update with values
await User.filter(id=1).update(email="updated@example.com")
```

### Deleting Records

```python
# Delete a single record
user = await User.get(id=1)
await user.delete()

# Bulk delete
await User.filter(is_active=False).delete()
```

## Relationships

### One-to-Many

```python
class Author(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)

class Book(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    author = fields.ForeignKeyField('models.Author', related_name='books')

# Query with relationships
books = await Book.all().prefetch_related('author')
for book in books:
    print(f"{book.title} by {book.author.name}")

# Reverse relationship
author = await Author.get(id=1)
author_books = await author.books.all()
```

### Many-to-Many

```python
class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    tags = fields.ManyToManyField('models.Tag', related_name='posts')

# Add tags to a post
post = await Post.get(id=1)
tag = await Tag.get(name="python")
await post.tags.add(tag)

# Get posts with tags
posts = await Post.all().prefetch_related('tags')
```

## Database Configuration

### Settings Configuration

```python
from fast_django.settings import Settings, OrmConfig

class Settings(Settings):
    orm: OrmConfig = OrmConfig(
        connections={
            "default": "sqlite://db.sqlite3",
            # "default": "postgres://user:pass@localhost/db",
            # "default": "mysql://user:pass@localhost/db",
        },
        models=["myapp.models", "aerich.models"],
        apps={
            "models": {
                "models": ["myapp.models", "aerich.models"],
                "default_connection": "default",
            }
        }
    )
```

### Environment Variables

```bash
# .env file
FD_ORM_CONNECTIONS_DEFAULT=sqlite://db.sqlite3
FD_ORM_MODELS_0=myapp.models
FD_ORM_MODELS_1=aerich.models
```

## Migrations

fast-django uses Aerich for database migrations:

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create migrations for specific app
python manage.py makemigrations --app myapp
```

## Async Context

### Using with FastAPI

```python
from fastapi import FastAPI
from fast_django import create_app, Settings

app = create_app(Settings())

@app.get("/users")
async def get_users():
    users = await User.all()
    return [{"id": u.id, "username": u.username} for u in users]
```

### Manual Database Operations

```python
from fast_django.orm import Tortoise, run_async

async def main():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["myapp.models"]}
    )

    # Your database operations here
    users = await User.all()

    await Tortoise.close_connections()

# Run the async function
run_async(main())
```

## Advanced Features

### Custom Managers

```python
class PostManager:
    @staticmethod
    async def published():
        return await Post.filter(is_published=True)

    @staticmethod
    async def recent(limit=10):
        return await Post.all().order_by('-created_at').limit(limit)

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    is_published = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    objects = PostManager()
```

### Model Methods

```python
class User(Model):
    id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    async def get_posts(self):
        return await Post.filter(author=self)
```

### Transactions

```python
from fast_django.orm import in_transaction

async def transfer_money(from_user, to_user, amount):
    async with in_transaction():
        from_user.balance -= amount
        to_user.balance += amount
        await from_user.save()
        await to_user.save()
```

## Best Practices

1. **Always use async/await** for database operations
2. **Use prefetch_related()** for related objects to avoid N+1 queries
3. **Use select_related()** for foreign key relationships
4. **Handle DoesNotExist exceptions** when using `.get()`
5. **Use transactions** for operations that must succeed or fail together
6. **Index frequently queried fields** for better performance

## Troubleshooting

### Common Issues

1. **"Database not initialized"**
   - Ensure `Tortoise.init()` is called before database operations
   - Check your database URL format

2. **"Model not found"**
   - Verify models are included in `Settings.orm.models`
   - Check import paths are correct

3. **Migration errors**
   - Run `python manage.py makemigrations` after model changes
   - Check for conflicting field changes
