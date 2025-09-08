# DRF Action Kit

**DRF Action Kit** is a Python package that enables **action-based serializer selection** in Django REST Framework.  
It allows defining different serializers for **actions** (list, retrieve, create, update, etc.) and provides **fallback serializers** based on HTTP methods.

## Features

- Action-based serializer support:
  - `list_serializer_class`, `retrieve_serializer_class`, `create_serializer_class`, `update_serializer_class`, etc.
- Fallback serializer support:
  - `read_serializer_class` for GET requests
  - `write_serializer_class` for POST, PUT, PATCH, DELETE
  - `serializer_class` as ultimate fallback
- Works with:
  - `ModelViewSet`
  - `ReadOnlyModelViewSet`
  - `GenericViewSet + mixins`
  - `APIView` and `GenericAPIView`
- Custom exception handling: `SerializerNotFoundError`
- Clean, extendable, and testable

## Installation

Install from PyPI:

```bash
pip install drf-action-kit
```

## Usage

1. ModelViewSet Example

```python
from rest_framework import routers
from myapp.models import Post
from myapp.serializers import PostListSerializer, PostDetailSerializer, PostCreateSerializer, PostUpdateSerializer
from drf_action_kit.action_serializer import ActionSerializerModelViewSet

class PostViewSet(ActionSerializerModelViewSet):
    serializer_class = PostDetailSerializer       # Fallback
    read_serializer_class = PostDetailSerializer
    write_serializer_class = PostCreateSerializer

    # Action-specific serializers
    list_serializer_class = PostListSerializer
    retrieve_serializer_class = PostDetailSerializer
    create_serializer_class = PostCreateSerializer
    update_serializer_class = PostUpdateSerializer

router = routers.DefaultRouter()
router.register(r"posts", PostViewSet)

```

2. GenericViewSet + Mixins Example

```python
from rest_framework import mixins, viewsets
from myapp.serializers import PostListSerializer, PostCreateSerializer
from drf_action_kit.action_serializer import ActionSerializerGenericViewSet

class PostListCreateView(ActionSerializerGenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = PostListSerializer
    read_serializer_class = PostListSerializer
    write_serializer_class = PostCreateSerializer

    list_serializer_class = PostListSerializer
    create_serializer_class = PostCreateSerializer

```

3. APIView Example

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from myapp.serializers import PostDetailSerializer, PostCreateSerializer
from drf_action_kit.action_serializer import ActionSerializerAPIView

class PostAPIView(ActionSerializerAPIView):
    read_serializer_class = PostDetailSerializer
    write_serializer_class = PostCreateSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data={"title": "example"})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

```

## Serializer Selection Logic

1. Action-specific serializer

- Uses list_serializer_class, create_serializer_class, etc. if defined.

2. Fallback by HTTP method

- GET/HEAD/OPTIONS → read_serializer_class

- POST/PUT/PATCH/DELETE → write_serializer_class

3. Default serializer

Uses serializer_class if no action or HTTP-specific serializer is found.

4. Error handling

- Raises SerializerNotFoundError if no suitable serializer is available.

## Custom Exception

```python
from drf_action_kit.exceptions import SerializerNotFoundError

```

## Contact

- [Erdi Mollahüseyinoğlu](https://github.com/erdimollahuseyin) - Author, Maintainer
