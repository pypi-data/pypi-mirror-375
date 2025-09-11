try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

source_code = Annotated[str, "source_code"]

from .sql import *
from .css import *
from .js import *
from .ts import *
from .web import *
from .data import *

md = Annotated[source_code, "markdown"]
graphql = Annotated[source_code, "graphql"]
py = Annotated[source_code, "python"]
rs = Annotated[source_code, "rust"]
go = Annotated[source_code, "go"]
java = Annotated[source_code, "java"]
c = Annotated[source_code, "c"]
cpp = Annotated[source_code, "c++"]
cs = Annotated[source_code, "c#"]
php = Annotated[source_code, "php"]
rb = Annotated[source_code, "ruby"]
swift = Annotated[source_code, "swift"]
kt = Annotated[source_code, "kotlin"]
scala = Annotated[source_code, "scala"]
hs = Annotated[source_code, "haskell"]
ex = Annotated[source_code, "elixir"]
erl = Annotated[source_code, "erlang"]
clj = Annotated[source_code, "clojure"]
fs = Annotated[source_code, "f#"]
ml = Annotated[source_code, "ocaml"]
r = Annotated[source_code, "r"]
lua = Annotated[source_code, "lua"]
pl = Annotated[source_code, "perl"]
sh = Annotated[source_code, "bash"]
zsh = Annotated[source_code, "zsh"]
fish = Annotated[source_code, "fish"]
ps1 = Annotated[source_code, "powershell"]
dockerfile = Annotated[source_code, "dockerfile"]
tf = Annotated[source_code, "terraform"]
yaml = Annotated[source_code, "ansible"]
pp = Annotated[source_code, "puppet"]
rb = Annotated[source_code, "chef"]