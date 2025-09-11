from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class HtpasswdFiles(Resource):
    def create_htpasswd_file(
        self,
        request: models.HtpasswdFileCreateRequest,
    ) -> DtoResponse[models.HtpasswdFileResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/htpasswd-files",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.HtpasswdFileResource)

    def list_htpasswd_files(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.HtpasswdFileResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/htpasswd-files",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.HtpasswdFileResource)

    def read_htpasswd_file(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.HtpasswdFileResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/htpasswd-files/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.HtpasswdFileResource)

    def delete_htpasswd_file(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/htpasswd-files/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
