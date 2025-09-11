try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

source_code = Annotated[str, "source_code"]

mysql = Annotated[source_code, "mysql"]
pgsql = Annotated[source_code, "pgsql"]
sqlite = Annotated[source_code, "sqlite"]
mssql = Annotated[source_code, "mssql"]
oracle = Annotated[source_code, "oracle"]
plsql = Annotated[source_code, "plsql"]

sql = Annotated[source_code, "sql"]