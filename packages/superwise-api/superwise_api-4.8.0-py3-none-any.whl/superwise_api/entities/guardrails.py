from superwise_api.entities.base import BaseApi
from superwise_api.models.guardrails.guardrails import GuardResponse
from superwise_api.models.guardrails.guardrails import GuardResponses
from superwise_api.models.guardrails.guardrails import Guards


class GuardrailsApi(BaseApi):
    _model_name = "guardrails"
    _resource_path = "/v1/guardrails"
    _model_class = GuardResponse

    def validate(
        self,
        guards: Guards,
        input_query: str,
        only_validate_request: bool = False,
        **kwargs,
    ) -> GuardResponses:
        """
        Validate guards on a given input query.

        Args:
            guards: The guards to validate.
            input_query: The input query to validate.
            only_validate_request: If true, only the guards will be validated.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The validation of each guard.
        """
        response_types_map = {
            "200": self._model_class,
            "401": "HTTPUnauthorized",
            "422": "HTTPValidationError",
        }
        guards = [guard.model_dump() for guard in guards]
        payload = {
            "guards": guards,
            "input_query": input_query,
            "only_validate_request": only_validate_request,
        }

        return self.api_client.post(
            resource_path=self._resource_path,
            model_name=self._model_name,
            data=payload,
            response_types_map=response_types_map,
            **kwargs,
        )
