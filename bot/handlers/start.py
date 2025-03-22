from typing import Any

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from db import User, Referral

router = Router()

@router.message(CommandStart())
async def start(message: Message, command: CommandObject, session: AsyncSession) -> Any:
    user = await session.scalar(select(User).where(User.id == message.from_user.id))
    me = await message.bot.get_me()

    if not user:
        user = User(id=message.from_user.id)
        session.add(user)
        await session.commit()

    if command.args:
        option, value = command.args.split("_")
        match option:
            case "r":
                try:
                    inviter_id = int(value)
                except ValueError:
                    return None
                
                inviter = await session.scalar(select(User).where(User.id == inviter_id))
                if not inviter:
                    return None
                
                check_guest = await session.scalar(
                    select(Referral).where(
                        or_(
                            Referral.user_id == user.id,
                            Referral.referral_id == inviter_id,
                            Referral.referral_id == user.id
                        )
                    )
                )

                if check_guest:
                    return None
                if inviter.id == user.id:
                    return None
                
                session.add(Referral(user_id=inviter_id, referral_id=user.id))
                await session.commit()

                await message.bot.send_message(
                    chat_id=inviter.id, text="У вас появился реферал!"
                )
                return await message.answer("Вы стали рефералом!")
            
    return await message.answer(
        f"Реф. ссылка: https://t.me/{me.username}?start=r_{message.from_user.id}"
    )


