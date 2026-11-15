from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now() -> datetime:
    #curent UTC time, used for default values in DateTime columns
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    last_active_date = Column(Date, nullable=True)
    points = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # relationships
    interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")
    user_trails = relationship("UserTrail", back_populates="user", cascade="all, delete-orphan")
    unlocked_milestones = relationship(
        "UnlockedMilestone", back_populates="user", cascade="all, delete-orphan"
    )
    step_logs = relationship("StepLog", back_populates="user", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    # relationships
    user_interests = relationship("UserInterest", back_populates="tag", cascade="all, delete-orphan")
    milestone_tags = relationship("MilestoneTag", back_populates="tag", cascade="all, delete-orphan")


class UserInterest(Base):
    __tablename__ = "user_interests"
    __table_args__ = (UniqueConstraint("users_id", "tags_id", name="uq_user_interest"),)

    id = Column(Integer, primary_key=True, index=True)
    users_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tags_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    # relationships
    user = relationship("User", back_populates="interests")
    tag = relationship("Tag", back_populates="user_interests")


class Trail(Base):
    __tablename__ = "trails"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    total_distance_km = Column(Float, nullable=False)
    cover_image_url = Column(String(500), nullable=True)
    gpx_data = Column(JSON, nullable=False, default=list)  # Formát: [[lat, lng], ...]

    # relationships (sorting milestones directly by their position on the trail)
    milestones = relationship(
        "Milestone",
        back_populates="trail",
        order_by="Milestone.km_position",
        cascade="all, delete-orphan",
    )
    user_trails = relationship("UserTrail", back_populates="trail", cascade="all, delete-orphan")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    trail_id = Column(Integer, ForeignKey("trails.id", ondelete="CASCADE"), nullable=False, index=True)
    km_position = Column(Float, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    mapillary_image_url = Column(String(500), nullable=True)
    is_360 = Column(Boolean, default=False, nullable=False)
    wiki_image_url = Column(String(500), nullable=True)

    # relationships
    trail = relationship("Trail", back_populates="milestones")
    milestone_tags = relationship(
        "MilestoneTag", back_populates="milestone", cascade="all, delete-orphan"
    )
    unlocked_by = relationship(
        "UnlockedMilestone", back_populates="milestone", cascade="all, delete-orphan"
    )


class MilestoneTag(Base):
    __tablename__ = "milestone_tags"
    __table_args__ = (UniqueConstraint("milestones_id", "tags_id", name="uq_milestone_tag"),)

    id = Column(Integer, primary_key=True, index=True)
    milestones_id = Column(Integer, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    tags_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    # relationships
    milestone = relationship("Milestone", back_populates="milestone_tags")
    tag = relationship("Tag", back_populates="milestone_tags")


class UserTrail(Base):
    __tablename__ = "user_trails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    trail_id = Column(Integer, ForeignKey("trails.id", ondelete="CASCADE"), nullable=False, index=True)
    current_position = Column(Float, default=0.0, nullable=False)
    status = Column(String(20), default="active", nullable=False)  # 'active', 'done', 'abandoned'
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # relationships
    user = relationship("User", back_populates="user_trails")
    trail = relationship("Trail", back_populates="user_trails")


class UnlockedMilestone(Base):
    __tablename__ = "unlocked_milestones"
    __table_args__ = (UniqueConstraint("user_id", "milestone_id", name="uq_user_milestone"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    milestone_id = Column(
        Integer, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unlocked_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # relationships
    user = relationship("User", back_populates="unlocked_milestones")
    milestone = relationship("Milestone", back_populates="unlocked_by")


class StepLog(Base):
    __tablename__ = "step_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    step_count = Column(Integer, nullable=False)

    # relationships
    user = relationship("User", back_populates="step_logs")