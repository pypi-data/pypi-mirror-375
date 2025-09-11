from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class MariaDBEncryptionKeys(Resource):
    def create_mariadb_encryption_key(
        self,
        request: models.MariaDBEncryptionKeyCreateRequest,
    ) -> DtoResponse[models.MariaDBEncryptionKeyResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/mariadb-encryption-keys",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.MariaDBEncryptionKeyResource
        )

    def list_mariadb_encryption_keys(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.MariaDBEncryptionKeyResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/mariadb-encryption-keys",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(
            local_response, models.MariaDBEncryptionKeyResource
        )

    def read_mariadb_encryption_key(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.MariaDBEncryptionKeyResource]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/mariadb-encryption-keys/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.MariaDBEncryptionKeyResource
        )
