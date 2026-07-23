from sqlalchemy import select

from app.models import UsersORM
from app.schemas import SUserCreate
from app.database import SessionDep


async def get_user_by_id(session: SessionDep, user_id: int) -> UsersORM | None:
    result = await session.execute(select(UsersORM).where(UsersORM.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(session: SessionDep, username: str) -> UsersORM | None:
    result = await session.execute(
        select(UsersORM).where(UsersORM.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(session: SessionDep, email: str) -> UsersORM | None:
    result = await session.execute(select(UsersORM).where(UsersORM.email == email))
    return result.scalar_one_or_none()


async def get_all_users(session: SessionDep) -> list[UsersORM]:
    result = await session.execute(select(UsersORM))
    return list(result.scalars().all())


async def create_user(
    session: SessionDep, user_data: SUserCreate, hashed_password: str
) -> UsersORM:
    new_user = UsersORM(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def update_user(session: SessionDep, user_id: int, **fields) -> UsersORM | None:
    user = await get_user_by_id(session, user_id)
    if not user:
        return None
    for key, value in fields.items():
        setattr(user, key, value)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(session: SessionDep, user_id: int) -> bool:
    user = await get_user_by_id(session, user_id)
    if not user:
        return False
    await session.delete(user)
    await session.commit()
    return True
