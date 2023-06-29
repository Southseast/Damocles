# @Author: south
# @Date: 2023-06-23 10:40

from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
