import json
from enum import Enum
from typing import Annotated
from uuid import UUID

from fastapi import Request, Header, Depends
from pydantic import BaseModel


class UserRole(str, Enum):
    manager = "manager"
    administrator = "administrator"
    super_administrator = "super_administrator"


class PermissionType(str, Enum):
    dealer = "dealer"
    bulk_rule = "bulk_rule"
    inventory = "inventory"
    lead = "lead"
    page = "page"


class UserData(BaseModel):
    id: UUID | None = None
    role: UserRole | None = None
    permissions: dict[UUID, list[PermissionType]] | None = None

    def check_accessibility(self, dealer_id: UUID | str) -> bool:
        if self.role in {UserRole.super_administrator, UserRole.administrator}:
            return True

        uuid_dealer_id = dealer_id if isinstance(dealer_id, UUID) else UUID(dealer_id)

        if self.permissions and uuid_dealer_id in self.permissions:
            return True

        return False


def get_user_data(
    user_id: Annotated[UUID | None, Header(alias="user-id")] = None,
    user_role: Annotated[UserRole | None, Header(alias="user-role")] = None,
    user_permissions: Annotated[str | None, Header(alias="user-permissions")] = None,
) -> UserData:
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user-id header"
        )

    perms = None
    if user_permissions:
        try:
            raw = json.loads(user_permissions)
            perms = {UUID(k): [PermissionType(p) for p in v] for k, v in raw.items()}
        except (json.JSONDecodeError, ValueError, TypeError, ValidationError):
            raise HTTPException(
                status_code=400,
                detail="Invalid user-permissions header JSON"
            )

    return UserData(
        id=user_id,
        role=user_role,
        permissions=perms
    )
