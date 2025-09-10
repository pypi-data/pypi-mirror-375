from typing import Annotated
from uuid import UUID

from fastapi import Request, Header, Depends
from pydantic import BaseModel


class DealerData(BaseModel):
    main_dealer_id: UUID | None = None


def get_dealer_data(
        request: Request,
        main_dealer_id: Annotated[UUID | None, Depends(Header(default=None))],
) -> DealerData:
    return DealerData(
        main_dealer_id=main_dealer_id if main_dealer_id else None,
    )
