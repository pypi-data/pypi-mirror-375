from cyberfusion.CoreApiClient import models
from typing import Optional, Union, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class CustomConfigSnippets(Resource):
    def create_custom_config_snippet(
        self,
        request: Union[
            models.CustomConfigSnippetCreateFromContentsRequest,
            models.CustomConfigSnippetCreateFromTemplateRequest,
        ],
    ) -> DtoResponse[models.CustomConfigSnippetResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/custom-config-snippets",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.CustomConfigSnippetResource
        )

    def list_custom_config_snippets(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.CustomConfigSnippetResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/custom-config-snippets",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(
            local_response, models.CustomConfigSnippetResource
        )

    def read_custom_config_snippet(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.CustomConfigSnippetResource]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/custom-config-snippets/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.CustomConfigSnippetResource
        )

    def update_custom_config_snippet(
        self,
        request: models.CustomConfigSnippetUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.CustomConfigSnippetResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/custom-config-snippets/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.CustomConfigSnippetResource
        )

    def delete_custom_config_snippet(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/custom-config-snippets/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
