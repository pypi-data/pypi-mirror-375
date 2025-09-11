from typing import Callable

from fastapi import Depends

from .dealer import get_dealer_data, DealerData
from .user import PermissionType, UserData, get_user_data, UserRole
from ...core.exception import RequestException


def check_permissions(
        user_data: UserData,
        dealer_data: DealerData,
        required_permissions: list[PermissionType]
) -> bool:
    limited_roles = {UserRole.manager}

    if user_data.role not in limited_roles:
        return True

    if dealer_data.main_dealer_id not in user_data.permissions:
        return False

    user_permissions: list[PermissionType] = user_data.permissions.get(dealer_data.main_dealer_id) or []
    if len(user_permissions) != 0 and not set(required_permissions).issubset(set(user_permissions)):
        return False

    return True



def permission_restriction(
    required_permissions: list[PermissionType],
) -> Callable[[UserData, DealerData], tuple[UserData, DealerData]]:
    controller = f"{__name__}.permission_restriction"

    def dependency(
        user_data: UserData = Depends(get_user_data),
        dealer_data: DealerData = Depends(get_dealer_data),
    ):
        is_permitted = check_permissions(
            user_data=user_data,
            dealer_data=dealer_data,
            required_permissions=required_permissions,
        )
        if not is_permitted:
            raise RequestException(
                status_code=403,
                controller=controller,
                message="You don't have permission to access this dealer or this section.",
            )

        return user_data, dealer_data

    return dependency
