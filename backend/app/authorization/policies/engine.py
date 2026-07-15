from __future__ import annotations

from dataclasses import dataclass

from app.authorization.models import AuthorizationContext, AuthorizationDecision
from app.authorization.repositories.policy_repository import PolicyRepository


@dataclass(slots=True)
class PolicyEngine:
    policy_repository: PolicyRepository

    async def evaluate(self, context: AuthorizationContext, resource: str, action: str) -> AuthorizationDecision:
        policies = await self.policy_repository.active_policies()
        matched: list = []
        for policy in policies:
            if policy.resource not in {resource, "*"} or policy.action not in {action, "*"}:
                continue
            if policy.subject_type == "any":
                matched.append(policy)
                continue
            if policy.subject_type == "role" and policy.subject_value in context.role_codes:
                matched.append(policy)
                continue
            if policy.subject_type == "permission" and policy.subject_value in context.permission_codes:
                matched.append(policy)
                continue
            if policy.subject_type == "user" and policy.subject_value == str(context.user_id):
                matched.append(policy)

        if not matched:
            return AuthorizationDecision(allowed=False, reason="no_matching_policy")

        matched.sort(key=lambda item: item.priority)
        deny = next((policy for policy in matched if policy.effect == "deny"), None)
        if deny is not None:
            return AuthorizationDecision(allowed=False, reason="deny_override", matched_policy=deny.code)

        allow = next((policy for policy in matched if policy.effect == "allow"), None)
        if allow is not None:
            return AuthorizationDecision(allowed=True, reason="allow_override", matched_policy=allow.code)

        return AuthorizationDecision(allowed=False, reason="no_allow_policy")
