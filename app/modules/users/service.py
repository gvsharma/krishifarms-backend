from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.modules.users.models import Role, User
from app.modules.users.schemas import UserCreateRequest, UserUpdateRequest
from app.shared.services.audit import write_audit_log


def list_users(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[User], int]:
    query = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.org_id == org_id, User.deleted_at.is_(None))
        .order_by(User.created_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_user(db: Session, org_id: UUID, user_id: UUID) -> User:
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id, User.org_id == org_id, User.deleted_at.is_(None))
        .first()
    )
    if user is None:
        raise NotFoundError("User not found")
    return user


def get_current_profile(db: Session, user_id: UUID) -> User:
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id, User.deleted_at.is_(None), User.is_active.is_(True))
        .first()
    )
    if user is None:
        raise NotFoundError("User not found")
    return user


def create_user(
    db: Session,
    org_id: UUID,
    payload: UserCreateRequest,
    actor_user_id: UUID,
) -> User:
    existing = (
        db.query(User)
        .filter(User.org_id == org_id, User.email == payload.email, User.deleted_at.is_(None))
        .first()
    )
    if existing:
        raise ConflictError("User with this email already exists")

    role = db.query(Role).filter(Role.id == payload.role_id, Role.org_id == org_id).first()
    if role is None:
        raise NotFoundError("Role not found")

    user = User(
        org_id=org_id,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role_id=payload.role_id,
        preferred_locale=payload.preferred_locale,
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(user)
    db.flush()
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="user",
        entity_id=user.id,
        after_state={"email": user.email, "full_name": user.full_name, "role_id": str(user.role_id)},
    )
    db.commit()
    db.refresh(user)
    return get_user(db, org_id, user.id)


def update_user(
    db: Session,
    org_id: UUID,
    user_id: UUID,
    payload: UserUpdateRequest,
    actor_user_id: UUID,
) -> User:
    user = get_user(db, org_id, user_id)
    before = {"full_name": user.full_name, "role_id": str(user.role_id), "is_active": user.is_active}

    if payload.role_id is not None:
        role = db.query(Role).filter(Role.id == payload.role_id, Role.org_id == org_id).first()
        if role is None:
            raise NotFoundError("Role not found")
        user.role_id = payload.role_id

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.preferred_locale is not None:
        user.preferred_locale = payload.preferred_locale
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)

    user.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="user",
        entity_id=user.id,
        before_state=before,
        after_state={"full_name": user.full_name, "role_id": str(user.role_id), "is_active": user.is_active},
    )
    db.commit()
    return get_user(db, org_id, user.id)


def list_roles(db: Session, org_id: UUID) -> list[Role]:
    return db.query(Role).filter(Role.org_id == org_id).order_by(Role.name).all()
