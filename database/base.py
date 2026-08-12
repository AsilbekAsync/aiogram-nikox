import sqlalchemy.util.typing
def fixed_make_union(*types):
    import typing
    return typing.Union[types]
sqlalchemy.util.typing.make_union_type = fixed_make_union

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
