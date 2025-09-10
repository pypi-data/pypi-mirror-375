from typing import Annotated
from typing import List
from typing import Literal
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from superwise_api.models.agent.agent import GuardModelLLM


class BaseGuard(BaseModel):
    model_config = ConfigDict(extra="allow")


class AllowedTopicsGuard(BaseGuard):
    topics: List[str]
    type: Literal["allowed_topics"] = Field(default="allowed_topics")
    model: GuardModelLLM


class RestrictedTopicsGuard(BaseGuard):
    topics: List[str]
    type: Literal["restricted_topics"] = Field(default="restricted_topics")
    model: GuardModelLLM


class ToxicityGuard(BaseGuard):
    type: Literal["toxicity"] = Field(default="toxicity")
    threshold: float = 0.5
    validation_method: Literal["sentence"] | Literal["full"] = "sentence"


Guard = Annotated[Union[ToxicityGuard, AllowedTopicsGuard, RestrictedTopicsGuard], Field(discriminator="type")]
Guards = List[Guard]


class GuardResponse(BaseModel):
    valid: bool
    message: str

    @classmethod
    def from_dict(cls, obj: dict):
        if obj is None:
            return None

        return GuardResponse.model_validate(obj)


GuardResponses = List[GuardResponse]
