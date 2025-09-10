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
    permissions: dict[str, list[PermissionType]] | None = None

    def check_accessibility(self, dealer_id: UUID | str) -> bool:
        if self.role in {UserRole.super_administrator, UserRole.administrator}:
            return True

        if self.permissions and str(dealer_id) in self.permissions:
            return True

        return False


def get_user_data(
        request: Request,
        user_id: Annotated[UUID | None, Depends(Header(default=None))],
        user_role: Annotated[UserRole | None, Depends(Header(default=None))],
        user_permissions: Annotated[str | None, Depends(Header(default=None))],
) -> UserData:
    return UserData(
        id=user_id if user_id else None,
        role=user_role if user_role else None,
        permissions=json.loads(user_permissions) if user_permissions else None,
    )
