import sys
from typing import Sequence, Type, TypeVar

from beanie import Document

from .comment import Comment  # noqa: F401
# All database models must be imported here to be able to
# initialize them on startup.
from .post import Post  # noqa: F401

DocType = TypeVar("DocType", bound=Document)


def gather_documents() -> Sequence[Type[DocType]]:
    from inspect import getmembers, isclass

    return [
        doc
        for _, doc in getmembers(sys.modules[__name__], isclass)
        if issubclass(doc, Document) and doc.__name__ != "Document"
    ]
