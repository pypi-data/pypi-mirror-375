try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

source_code = Annotated[str, "source_code"]

ts = Annotated[source_code, "typescript"]
tsx = Annotated[source_code, "tsx"]
dts = Annotated[source_code, "dts"]