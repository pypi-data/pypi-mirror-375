from typing import Optional, List

from cyberfusion.CoreApiClient import models
from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class URLRedirects(Resource):
    def create_url_redirect(
        self,
        request: models.URLRedirectCreateRequest,
    ) -> DtoResponse[models.URLRedirectResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/url-redirects",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.URLRedirectResource)

    def list_url_redirects(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.URLRedirectResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/url-redirects",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.URLRedirectResource)

    def read_url_redirect(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.URLRedirectResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/url-redirects/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.URLRedirectResource)

    def update_url_redirect(
        self,
        request: models.URLRedirectUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.URLRedirectResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/url-redirects/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.URLRedirectResource)

    def delete_url_redirect(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/url-redirects/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
