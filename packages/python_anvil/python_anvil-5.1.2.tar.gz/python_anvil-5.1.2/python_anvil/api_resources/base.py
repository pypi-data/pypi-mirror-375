# pylint: disable=no-self-argument
import re

# Disabling pylint no-name-in-module because this is the documented way to
# import `BaseModel` and it's not broken, so let's keep it.
from pydantic import (  # pylint: disable=no-name-in-module
    BaseModel as _BaseModel,
    ConfigDict,
)


under_pat = re.compile(r"_([a-z])")


def underscore_to_camel(name):
    ret = under_pat.sub(lambda x: x.group(1).upper(), name)
    return ret


class BaseModel(_BaseModel):
    """Config override for all models.

    This override is mainly so everything can go from snake to camel-case.
    """

    # Allow extra fields even if it is not defined. This will allow models
    # to be more flexible if features are added in the Anvil API, but
    # explicit support hasn't been added yet to this library.
    model_config = ConfigDict(
        alias_generator=underscore_to_camel, populate_by_name=True, extra="allow"
    )
