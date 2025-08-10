import uuid
from typing import Optional
from fastapi import APIRouter, Cookie


router = APIRouter(prefix="/firstai", tags=["ai"])


def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())


# @router.get('/', response_model=AIJobRes)
