from uuid import UUID


def user_permissions_key(user_id: UUID) -> str:
    return f"user_permissions:{user_id}"
