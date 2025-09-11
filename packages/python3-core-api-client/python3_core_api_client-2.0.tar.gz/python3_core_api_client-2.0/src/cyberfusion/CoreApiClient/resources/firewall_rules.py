from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class FirewallRules(Resource):
    def create_firewall_rule(
        self,
        request: models.FirewallRuleCreateRequest,
    ) -> DtoResponse[models.FirewallRuleResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/firewall-rules",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.FirewallRuleResource)

    def list_firewall_rules(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.FirewallRuleResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/firewall-rules",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.FirewallRuleResource)

    def read_firewall_rule(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.FirewallRuleResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/firewall-rules/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.FirewallRuleResource)

    def delete_firewall_rule(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/firewall-rules/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
