try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

source_code = Annotated[str, "source_code"]

js = Annotated[source_code, "javascript"]
jsx = Annotated[source_code, "jsx"]
coffee = Annotated[source_code, "coffeescript"]