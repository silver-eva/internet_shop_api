# Internet Shop API

## Migration with alembic:
if `alembic` dir not in `app` run `cd app/` and execute:
```bash
alembic init -t async alembic
```

it's create `alembic` dir, now U need to edit `app/alembic/env.py` file by:

```python
from models.db import Base

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", "postgresql+asyncpg://<user>:<password>@<address>:<port>/<database>")

```

Now to make migration run:
```bash
$ alembic revision --autogenerate -m "Message"
```

its create `app/alembic/versions/<id>.py` file with migration

Now U need to upgrade database, run:

```bash
$ alembic upgrade head
```
>__NOTE__: ensure db is available!

U'r in!