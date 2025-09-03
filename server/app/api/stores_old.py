# In server/app/api/stores.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

# Note: These are dependencies you will need to create
from app.database import get_db
from app.models.store import Store
from app.schemas.store import StoreResponse
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[StoreResponse])
def get_stores(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1)
):
    """Get all stores."""
    stores = db.query(Store).offset(skip).limit(limit).all()
    return stores