from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class RootSSHKeys(Resource):
    def create_public_root_ssh_key(
        self,
        request: models.RootSSHKeyCreatePublicRequest,
    ) -> DtoResponse[models.RootSSHKeyResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/root-ssh-keys/public",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.RootSSHKeyResource)

    def create_private_root_ssh_key(
        self,
        request: models.RootSSHKeyCreatePrivateRequest,
    ) -> DtoResponse[models.RootSSHKeyResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/root-ssh-keys/private",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.RootSSHKeyResource)

    def list_root_ssh_keys(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.RootSSHKeyResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/root-ssh-keys",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.RootSSHKeyResource)

    def read_root_ssh_key(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.RootSSHKeyResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/root-ssh-keys/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.RootSSHKeyResource)

    def delete_root_ssh_key(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/root-ssh-keys/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
