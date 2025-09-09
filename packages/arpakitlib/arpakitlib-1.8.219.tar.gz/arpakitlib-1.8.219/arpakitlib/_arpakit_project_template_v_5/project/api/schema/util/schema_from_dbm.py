from typing import Type

from pydantic import BaseModel

from arpakitlib.ar_sqlalchemy_util import BaseDBM


def schema_from_dbm(*, schema: Type[BaseModel], dbm: BaseDBM, **kwargs) -> BaseModel:
    return schema.model_validate(dbm.simple_dict(
        include_columns_and_sd_properties=schema.model_fields.keys()
    ))
