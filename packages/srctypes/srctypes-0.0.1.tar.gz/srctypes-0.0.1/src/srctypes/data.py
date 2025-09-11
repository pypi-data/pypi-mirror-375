try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

source_code = Annotated[str, "source_code"]

json = Annotated[source_code, "json"]
yaml = Annotated[source_code, "yaml"]
toml = Annotated[source_code, "toml"]
ini = Annotated[source_code, "ini"]
xml = Annotated[source_code, "xml"]
csv = Annotated[source_code, "csv"]
tsv = Annotated[source_code, "tsv"]