# logic for trail endpoints.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Trail
from app.schemas import TrailSummarySchema, TrailDetailSchema

router = APIRouter(prefix="/api/trails", tags=["trails"])

@router.get("", response_model=list[TrailSummarySchema])
# Returns list of all trails without the milestones and gps points
def get_trails(db: Session = Depends(get_db)):
    trails = db.query(Trail).all()
    return trails

@router.get("/{trail_id}", response_model=TrailDetailSchema)
# Returns the detail of a specific trail, including all milestones and gps points
def get_trail(trail_id: int, db: Session = Depends(get_db)):
    trail = (
        db.query(Trail)
        .options(joinedload(Trail.milestones))
        .filter(Trail.id == trail_id)
        .first()
    )
    
    if not trail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trail with ID {trail_id} not found"
        )
    return trail