try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

source_code = Annotated[str, "source_code"]

css = Annotated[source_code, "css"]
scss = Annotated[source_code, "scss"]
sass = Annotated[source_code, "sass"]
less = Annotated[source_code, "less"]
stylus = Annotated[source_code, "stylus"]