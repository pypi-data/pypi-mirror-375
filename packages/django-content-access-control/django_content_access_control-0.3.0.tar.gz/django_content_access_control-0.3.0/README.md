# Content Access Control

> [!NOTE]
> **Acknowledgements & License Notice**
>
> This project utilizes the [pycasbin](https://github.com/casbin/pycasbin) library and is heavily inspired by and incorporates code from the following open-source projects, which are distributed under the Apache 2.0 License:
>
> - **[pycasbin/django-authorization](https://github.com/pycasbin/django-authorization/)**: Much of the core logic and structure is adapted from this library.
> - **[pycasbin/django-orm-adapter](https://github.com/pycasbin/django-orm-adapter/)**: The adapter implementation for Django ORM is based on this project.
>
> We are grateful to the original authors for their work. In accordance with the Apache 2.0 License, we acknowledge that significant portions of this codebase are derived from their efforts. You can view the full license [here](https://www.apache.org/licenses/LICENSE-2.0).

This Django app provides a flexible and powerful way to manage fine-grained
access control for your models and API endpoints using `pycasbin`. It allows you
to define permissions based on subjects (users or groups), resources (any Django
model instance or a URL), and actions.

## Key Concepts

- **Subject**: Represents who is requesting access. This can be a
  `PolicySubject` (linked to a Django `User`) or a `PolicySubjectGroup`.
- **Resource**: Represents what is being accessed. This can be any Django
  model instance or a URL path.
- **Action**: Represents the operation being performed (e.g., `read`, `write`,
  `delete`, or an HTTP method like `GET`, `POST`).

Policies are stored as `CasbinRule` instances and can be managed through the
Django admin panel.

## Setup

1. **Install the app:**

```sh
pip install django-content-access-control
```

Then, add `django_content_access_control` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_content_access_control",
    # ...
]
```

Do not forget to run migrations:

```sh
python manage.py migrate
```

2. **Configure Casbin:**

In your `settings.py`, you need to specify the path to your Casbin model
configuration file.

```python
# settings.py
CASBIN_MODEL = str(BASE_DIR / "casbin_model.conf")
```

An example `casbin_model.conf` files are in the `model_examples/` directory.

3.**Protect DRF Endpoints (Optional):**
  To automatically protect your Django Rest Framework views, add
  `SubjectHasUrlPermission` to your `DEFAULT_PERMISSION_CLASSES`.

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "content_access_control.permissions.SubjectHasUrlPermission",
    ],
    # ...
}
```

This permission class will check if the current subject has the right to
perform the request's method on the request's path.

4.**Enable Subject Switching (Optional):**
  If you want to allow users to act as different "subjects" (e.g., personas
  with different permissions), you can use the `PolicySubjectMiddleware`. Add
  it to your `MIDDLEWARE` settings.

```python
# settings.py
MIDDLEWARE = [
    # ...
    "content_access_control.middleware.PolicySubjectMiddleware",
    # ...
]
```

When this middleware is active, an authenticated user can specify a subject
to act as by sending the `X-Policy-Subject-Act-As` header with the name of
one of their `PolicySubject`s.

## Usage

### Defining Permissions for Models

To manage permissions for a specific Django model, you need to register it in
the admin panel. This creates a user-friendly interface for creating, viewing,
and deleting access rules for instances of that model.

In the `admin.py` of one of your apps, use the `register_permission_admin`
function.

#### Examples

##### Single Action
Registering the `Feature` model with a single "access" action.

```python
from django.contrib import admin
from .models import Feature
from content_access_control.admin_permission import register_permission_admin

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    ...

register_permission_admin(Feature, ["access"])
```

##### Multiple Actions
Registering the `Chunk` model with multiple actions.

```python
from django.contrib import admin
from .models import Chunk
from content_access_control.admin_permission import register_permission_admin

@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    ...

register_permission_admin(Chunk, ["create", "read", "update", "delete"])
```

After registering, a new section for "Chunk Content Access Permission" will
appear in the admin panel, allowing you to grant subjects (like `PolicySubject`
or `PolicySubjectGroup`) specific actions on `Chunk` objects.

### Enforcing Permissions

- **For DRF Views:** If you've set up `SubjectHasUrlPermission`, enforcement
  is automatic. To grant a user access to an endpoint, you need to create a
  `CasbinRule` that allows it. For example, to allow the user `john.doe` to
  make `GET` requests to `/api/chunks/`, you would create a policy rule: `p,
  john.doe, /api/chunks/, GET`. This can be done via the "Casbin Rules"
  section in the admin panel.

- **For Model Instances:** The permissions you define using the dynamically
  created admin panels (e.g., "Feature Content Access Permission") create
  policies that link subjects to specific model instances. You can integrate
  Pycasbin with Django authentication system. To enable the backend, you need to
  specify it in settings.py.

```py
AUTHENTICATION_BACKENDS = [
  "dauthz.backends.CasbinBackend",
  "django.contrib.auth.backends.ModelBackend",
]
```

### Customizing Admin Widgets

You can customize the widgets used for selecting subjects and resources in the
permission admin forms. This is useful for integrating with libraries like
`django-select2` to provide autocomplete fields for large datasets.

Example of passing a custom widget:

```python
from django.urls import reverse_lazy
from django_select2.forms import Select2Widget
from content_access_control.admin_permission import register_permission_admin
from .models import Feature

register_permission_admin(
    Feature,
    ['access'],
    subject_widget=Select2Widget(
        attrs={
            'data-ajax--url': reverse_lazy('subject_autocomplete'),
            'data-ajax--cache': 'true',
            'data-minimum-input-length': '1',
        }
    ),
    resource_widget=Select2Widget(
        attrs={
            'data-ajax--url': reverse_lazy('resource_autocomplete'),
            'data-ajax--cache': 'true',
            'data-minimum-input-length': '1',
        }
    ),
)
```
