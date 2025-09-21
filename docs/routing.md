# Routing

fast-django uses FastAPI's routing system with automatic router discovery and inclusion. Routes are defined using APIRouter and automatically included when apps are registered in `installed_apps`.

## Basic Routing

### Creating a Router

```python
from fast_django.routers import APIRouter

router = APIRouter()

@router.get("/healthz")
def healthz():
    return {"status": "ok"}
```

### Auto-Discovery

fast-django automatically discovers routers in your apps by looking for:
- `urls.py` - Primary router file (Django-style)
- `routes.py` - Compatibility shim that can re-export from `urls.py`
- `api.py` - API-specific routes
- `views.py` - View-based routes

The first file found with a `router` variable will be included.

## Route Definition

### HTTP Methods

```python
from fast_django.routers import APIRouter

router = APIRouter()

# GET endpoint
@router.get("/posts")
async def list_posts():
    return {"posts": []}

# POST endpoint
@router.post("/posts")
async def create_post(title: str, content: str):
    return {"message": "Post created", "title": title}

# PUT endpoint
@router.put("/posts/{post_id}")
async def update_post(post_id: int, title: str, content: str):
    return {"message": f"Post {post_id} updated"}

# DELETE endpoint
@router.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    return {"message": f"Post {post_id} deleted"}

# PATCH endpoint
@router.patch("/posts/{post_id}")
async def partial_update_post(post_id: int, **updates):
    return {"message": f"Post {post_id} partially updated", "updates": updates}
```

### Path Parameters

```python
@router.get("/posts/{post_id}")
async def get_post(post_id: int):
    return {"post_id": post_id, "title": "Sample Post"}

@router.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

### Query Parameters

```python
@router.get("/posts")
async def list_posts(
    skip: int = 0,
    limit: int = 10,
    published: bool = True,
    category: str = None
):
    return {
        "skip": skip,
        "limit": limit,
        "published": published,
        "category": category
    }
```

### Request Body

```python
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = False

@router.post("/posts")
async def create_post(post: PostCreate):
    return {"message": "Post created", "post": post.dict()}
```

## Advanced Routing

### Router Prefixes

```python
# In blog/urls.py
from fast_django.routers import APIRouter

router = APIRouter(prefix="/api/v1", tags=["blog"])

@router.get("/posts")
async def list_posts():
    return {"posts": []}
```

### Router Tags

```python
router = APIRouter(tags=["posts", "public"])

@router.get("/posts")
async def list_posts():
    return {"posts": []}
```

### Dependencies

```python
from fastapi import Depends, HTTPException
from fast_django.orm import Model

async def get_current_user():
    # Your authentication logic here
    return {"user_id": 1, "username": "john"}

@router.get("/posts")
async def list_posts(user: dict = Depends(get_current_user)):
    return {"posts": [], "user": user}
```

### Response Models

```python
from pydantic import BaseModel

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    return PostResponse(
        id=post_id,
        title="Sample Post",
        content="This is a sample post",
        created_at=datetime.now()
    )
```

## Database Integration

### Using Models in Routes

```python
from fast_django.orm import Model, fields
from fast_django.routers import APIRouter

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

router = APIRouter()

@router.get("/posts")
async def list_posts():
    posts = await Post.all()
    return [{"id": post.id, "title": post.title} for post in posts]

@router.post("/posts")
async def create_post(title: str, content: str):
    post = await Post.create(title=title, content=content)
    return {"id": post.id, "title": post.title}

@router.get("/posts/{post_id}")
async def get_post(post_id: int):
    try:
        post = await Post.get(id=post_id)
        return {"id": post.id, "title": post.title, "content": post.content}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")
```

## Error Handling

### HTTP Exceptions

```python
from fastapi import HTTPException

@router.get("/posts/{post_id}")
async def get_post(post_id: int):
    if post_id < 1:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    # Your logic here
    return {"post_id": post_id}
```

### Custom Exception Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)}
    )
```

## Middleware Integration

### CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom Middleware

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## App Structure

### Project-level Routes

```python
# mysite/urls.py
from fast_django.routers import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Welcome to MySite"}

@router.get("/health")
def health():
    return {"status": "healthy"}
```

### App-level Routes

```python
# blog/urls.py
from fast_django.routers import APIRouter

router = APIRouter(prefix="/blog", tags=["blog"])

@router.get("/posts")
async def list_posts():
    return {"posts": []}
```

## URL Configuration

### Including Routers

Routers are automatically included when apps are in `installed_apps`:

```python
# mysite/settings.py
class Settings(Settings):
    installed_apps: list[str] = ["mysite", "blog"]
```

### Manual Router Inclusion

```python
# mysite/asgi.py
from fast_django import create_app
from fast_django.routers import APIRouter
from blog.routes import router as blog_router

app = create_app(Settings())
app.include_router(blog_router, prefix="/api")
```

## Best Practices

1. **Use descriptive route names** that clearly indicate their purpose
2. **Group related routes** using router prefixes and tags
3. **Validate input data** using Pydantic models
4. **Handle errors gracefully** with appropriate HTTP status codes
5. **Use async/await** for database operations
6. **Document your API** with proper docstrings and response models
7. **Keep routes focused** - one responsibility per route
8. **Use dependency injection** for shared functionality

## Examples

### Complete Blog API

```python
from fast_django.routers import APIRouter
from fast_django.orm import Model, fields
from pydantic import BaseModel
from typing import List, Optional

# Models
class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    published = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

# Pydantic models
class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = False

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime

# Router
router = APIRouter(prefix="/api/posts", tags=["posts"])

@router.get("/", response_model=List[PostResponse])
async def list_posts(skip: int = 0, limit: int = 10):
    posts = await Post.all().offset(skip).limit(limit)
    return [PostResponse.from_orm(post) for post in posts]

@router.post("/", response_model=PostResponse)
async def create_post(post: PostCreate):
    db_post = await Post.create(**post.dict())
    return PostResponse.from_orm(db_post)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    post = await Post.get(id=post_id)
    return PostResponse.from_orm(post)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostCreate):
    db_post = await Post.get(id=post_id)
    await db_post.update_from_dict(post.dict())
    await db_post.save()
    return PostResponse.from_orm(db_post)

@router.delete("/{post_id}")
async def delete_post(post_id: int):
    post = await Post.get(id=post_id)
    await post.delete()
    return {"message": "Post deleted"}
```
