# Examples

This section provides comprehensive examples of fast-django applications, from simple tutorials to complete production-ready applications.

## Blog Application

A complete blog application demonstrating models, routing, admin interface, and database operations.

### Project Setup

```bash
# Create project
fast-django startproject myblog
cd myblog

# Create blog app
fast-django startapp blog
```

### Configuration

Update `myblog/settings.py`:

```python
from fast_django.settings import Settings, OrmConfig

class Settings(Settings):
    app_name: str = "My Blog"
    debug: bool = True
    orm: OrmConfig = OrmConfig(
        models=["myblog.models", "blog.models", "aerich.models"]
    )
    installed_apps: list[str] = ["myblog", "blog"]
```

### Models

Define your blog models in `blog/models.py`:

```python
from fast_django.orm import Model, fields
from datetime import datetime

class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    slug = fields.CharField(max_length=100, unique=True)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    slug = fields.CharField(max_length=50, unique=True)
    color = fields.CharField(max_length=7, default="#000000")  # Hex color

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    slug = fields.CharField(max_length=200, unique=True)
    content = fields.TextField()
    excerpt = fields.TextField(max_length=500, null=True)
    published = fields.BooleanField(default=False)
    featured = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    published_at = fields.DatetimeField(null=True)

    # Relationships
    category = fields.ForeignKeyField('models.Category', related_name='posts')
    tags = fields.ManyToManyField('models.Tag', related_name='posts')

class Comment(Model):
    id = fields.IntField(pk=True)
    post = fields.ForeignKeyField('models.Post', related_name='comments')
    author_name = fields.CharField(max_length=100)
    author_email = fields.CharField(max_length=100)
    content = fields.TextField()
    approved = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
```

### API Routes

Create comprehensive API routes in `blog/urls.py`:

```python
from fast_django.routers import APIRouter
from fast_django.orm import DoesNotExist
from fastapi import HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/blog", tags=["blog"])

# Pydantic models for request/response
class PostCreate(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    category_id: int
    tag_ids: List[int] = []
    published: bool = False
    featured: bool = False

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    published: Optional[bool] = None
    featured: Optional[bool] = None

class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    excerpt: Optional[str]
    published: bool
    featured: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    category: dict
    tags: List[dict]

    class Config:
        from_attributes = True

# Category endpoints
@router.get("/categories", response_model=List[dict])
async def list_categories():
    categories = await Category.all()
    return [{"id": c.id, "name": c.name, "slug": c.slug} for c in categories]

@router.post("/categories")
async def create_category(name: str, slug: str, description: str = None):
    category = await Category.create(
        name=name,
        slug=slug,
        description=description
    )
    return {"id": category.id, "name": category.name}

# Tag endpoints
@router.get("/tags", response_model=List[dict])
async def list_tags():
    tags = await Tag.all()
    return [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color} for t in tags]

@router.post("/tags")
async def create_tag(name: str, slug: str, color: str = "#000000"):
    tag = await Tag.create(name=name, slug=slug, color=color)
    return {"id": tag.id, "name": tag.name}

# Post endpoints
@router.get("/posts", response_model=List[PostResponse])
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    published: Optional[bool] = None,
    category_id: Optional[int] = None,
    featured: Optional[bool] = None
):
    query = Post.all()

    if published is not None:
        query = query.filter(published=published)
    if category_id is not None:
        query = query.filter(category_id=category_id)
    if featured is not None:
        query = query.filter(featured=featured)

    posts = await query.offset(skip).limit(limit).prefetch_related('category', 'tags')

    return [
        PostResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            content=post.content,
            excerpt=post.excerpt,
            published=post.published,
            featured=post.featured,
            created_at=post.created_at,
            updated_at=post.updated_at,
            published_at=post.published_at,
            category={"id": post.category.id, "name": post.category.name},
            tags=[{"id": tag.id, "name": tag.name} for tag in post.tags]
        ) for post in posts
    ]

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    try:
        post = await Post.get(id=post_id).prefetch_related('category', 'tags')
        return PostResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            content=post.content,
            excerpt=post.excerpt,
            published=post.published,
            featured=post.featured,
            created_at=post.created_at,
            updated_at=post.updated_at,
            published_at=post.published_at,
            category={"id": post.category.id, "name": post.category.name},
            tags=[{"id": tag.id, "name": tag.name} for tag in post.tags]
        )
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")

@router.post("/posts", response_model=PostResponse)
async def create_post(post: PostCreate):
    # Create slug from title
    slug = post.title.lower().replace(" ", "-").replace("_", "-")

    # Get category
    try:
        category = await Category.get(id=post.category_id)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Category not found")

    # Create post
    db_post = await Post.create(
        title=post.title,
        slug=slug,
        content=post.content,
        excerpt=post.excerpt,
        published=post.published,
        featured=post.featured,
        category=category,
        published_at=datetime.now() if post.published else None
    )

    # Add tags
    if post.tag_ids:
        tags = await Tag.filter(id__in=post.tag_ids)
        await db_post.tags.add(*tags)

    return PostResponse.from_orm(db_post)

@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostUpdate):
    try:
        db_post = await Post.get(id=post_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update fields
    update_data = post.dict(exclude_unset=True)
    if 'category_id' in update_data:
        try:
            category = await Category.get(id=update_data['category_id'])
            update_data['category'] = category
            del update_data['category_id']
        except DoesNotExist:
            raise HTTPException(status_code=400, detail="Category not found")

    for field, value in update_data.items():
        if field != 'tag_ids':
            setattr(db_post, field, value)

    await db_post.save()

    # Update tags
    if 'tag_ids' in update_data:
        tags = await Tag.filter(id__in=update_data['tag_ids'])
        await db_post.tags.clear()
        await db_post.tags.add(*tags)

    return PostResponse.from_orm(db_post)

@router.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    try:
        post = await Post.get(id=post_id)
        await post.delete()
        return {"message": "Post deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")

# Comment endpoints
@router.get("/posts/{post_id}/comments")
async def list_comments(post_id: int, approved_only: bool = True):
    try:
        post = await Post.get(id=post_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")

    query = Comment.filter(post=post)
    if approved_only:
        query = query.filter(approved=True)

    comments = await query.order_by('-created_at')
    return [{"id": c.id, "author_name": c.author_name, "content": c.content, "created_at": c.created_at} for c in comments]

@router.post("/posts/{post_id}/comments")
async def create_comment(post_id: int, author_name: str, author_email: str, content: str):
    try:
        post = await Post.get(id=post_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = await Comment.create(
        post=post,
        author_name=author_name,
        author_email=author_email,
        content=content
    )

    return {"id": comment.id, "message": "Comment created successfully"}
```

### Admin Configuration

Set up admin interface in `blog/admin.py`:

```python
from fastapi import FastAPI
from fast_django.admin import AdminSite
from fast_django.settings import Settings

def init_admin(app: FastAPI, settings: Settings) -> None:
    site = AdminSite(title="Blog Admin")
    site.mount(app, settings)

    # Register models when model registration is implemented
    # site.register_model(Post)
    # site.register_model(Category)
    # site.register_model(Tag)
    # site.register_model(Comment)
```

### Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser --email admin@example.com

# Start development server
python manage.py runserver
```

## E-commerce API

A more complex example showing user management, product catalog, and order processing.

### Models

```python
# users/models.py
from fast_django.orm import Model, fields
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100, unique=True)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=128)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

# products/models.py
class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    slug = fields.CharField(max_length=100, unique=True)
    description = fields.TextField(null=True)
    parent = fields.ForeignKeyField('models.Category', null=True, related_name='children')

class Product(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    slug = fields.CharField(max_length=200, unique=True)
    description = fields.TextField()
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = fields.IntField(default=0)
    sku = fields.CharField(max_length=100, unique=True)
    active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    category = fields.ForeignKeyField('models.Category', related_name='products')
    tags = fields.ManyToManyField('models.Tag', related_name='products')

class Order(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='orders')
    status = fields.CharField(max_length=20, default='pending')  # pending, paid, shipped, delivered, cancelled
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    items = fields.ManyToManyField('models.OrderItem', related_name='order')

class OrderItem(Model):
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField('models.Order', related_name='order_items')
    product = fields.ForeignKeyField('models.Product', related_name='order_items')
    quantity = fields.IntField()
    unit_price = fields.DecimalField(max_digits=10, decimal_places=2)
    total_price = fields.DecimalField(max_digits=10, decimal_places=2)
```

### API Routes

```python
# products/routes.py
from fast_django.routers import APIRouter
from fastapi import HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/products", tags=["products"])

class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: float
    stock_quantity: int
    sku: str
    active: bool
    category: dict
    tags: List[dict]

@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None
):
    query = Product.filter(active=True)

    if category_id:
        query = query.filter(category_id=category_id)
    if min_price is not None:
        query = query.filter(price__gte=min_price)
    if max_price is not None:
        query = query.filter(price__lte=max_price)
    if search:
        query = query.filter(name__icontains=search)

    products = await query.offset(skip).limit(limit).prefetch_related('category', 'tags')

    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            slug=p.slug,
            description=p.description,
            price=float(p.price),
            stock_quantity=p.stock_quantity,
            sku=p.sku,
            active=p.active,
            category={"id": p.category.id, "name": p.category.name},
            tags=[{"id": t.id, "name": t.name} for t in p.tags]
        ) for p in products
    ]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    try:
        product = await Product.get(id=product_id, active=True).prefetch_related('category', 'tags')
        return ProductResponse.from_orm(product)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")
```

## Real-time Chat Application

An example using WebSockets for real-time communication.

### Models

```python
# chat/models.py
from fast_django.orm import Model, fields
from datetime import datetime

class ChatRoom(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    created_by = fields.ForeignKeyField('models.User', related_name='created_rooms')
    created_at = fields.DatetimeField(auto_now_add=True)
    is_private = fields.BooleanField(default=False)

    members = fields.ManyToManyField('models.User', related_name='chat_rooms')

class Message(Model):
    id = fields.IntField(pk=True)
    room = fields.ForeignKeyField('models.ChatRoom', related_name='messages')
    sender = fields.ForeignKeyField('models.User', related_name='sent_messages')
    content = fields.TextField()
    message_type = fields.CharField(max_length=20, default='text')  # text, image, file
    created_at = fields.DatetimeField(auto_now_add=True)
    edited_at = fields.DatetimeField(null=True)
    is_deleted = fields.BooleanField(default=False)
```

### WebSocket Routes

```python
# chat/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from fast_django.routers import APIRouter
import json

router = APIRouter(prefix="/ws", tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.room_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        self.room_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: int):
        self.active_connections.remove(websocket)
        if room_id in self.room_connections:
            self.room_connections[room_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_room(self, message: str, room_id: int):
        if room_id in self.room_connections:
            for connection in self.room_connections[room_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.room_connections[room_id].remove(connection)

manager = ConnectionManager()

@router.websocket("/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Save message to database
            message = await Message.create(
                room_id=room_id,
                sender_id=message_data['user_id'],
                content=message_data['content'],
                message_type=message_data.get('type', 'text')
            )

            # Broadcast to room
            await manager.broadcast_to_room(
                json.dumps({
                    "id": message.id,
                    "content": message.content,
                    "sender": message_data['username'],
                    "timestamp": message.created_at.isoformat(),
                    "type": message.message_type
                }),
                room_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
```

## Best Practices

1. **Structure your code** with clear separation of concerns
2. **Use Pydantic models** for request/response validation
3. **Handle errors gracefully** with appropriate HTTP status codes
4. **Use async/await** for all database operations
5. **Implement proper authentication** and authorization
6. **Add comprehensive logging** for debugging and monitoring
7. **Write tests** for your API endpoints
8. **Use environment variables** for configuration
9. **Implement rate limiting** for production APIs
10. **Add API documentation** with clear examples

## Next Steps

- Explore the API Reference:
  - [Core API](api/core.md)
  - [ORM API](api/orm.md)
  - [CLI API](api/cli.md)
- Read about [Migrations](migrations.md) and [Settings](settings.md)
- Review [Middleware](middleware.md) and [Routing](routing.md)
