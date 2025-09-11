try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

source_code = Annotated[str, "source_code"]

html = Annotated[source_code, "html"]
django = Annotated[source_code, "django"]
jinja = Annotated[source_code, "jinja"]
hbs = Annotated[source_code, "hbs"]
mustache = Annotated[source_code, "mustache"]
pug = Annotated[source_code, "pug"]
haml = Annotated[source_code, "haml"]
slim = Annotated[source_code, "slim"]
ejs = Annotated[source_code, "ejs"]