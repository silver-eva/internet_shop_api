# Internet Shop API

## Migration with alembic:
if `alembic` dir not in project root run:
```bash
$ alembic init -t async alembic
```

it's create `alembic` dir, now U need to edit `alembic/env.py` file by:

```python
from src.db.models import Base
from src.db.connect import url

# Set target metadata so Alembic knows where the models are
target_metadata = Base.metadata

# Set URL to the database
config.set_main_option("sqlalchemy.url",  url)
```

Now to make migration run:
```bash
$ alembic revision --autogenerate -m "Message"
```

its create `alembic/versions/<id>.py` file with migration

Now U need to upgrade database, run:

```bash
$ alembic upgrade head
```
>__NOTE__: enshure db is available!

U'r in!