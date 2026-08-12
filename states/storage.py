import json
import logging
from typing import Any, Mapping

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert

from database.engine import session_factory
from models.fsm import FSMState

logger = logging.getLogger(__name__)


class SQLAlchemyStorage(BaseStorage):
    async def set_state(self, key: StorageKey, state: StateType = None):
        state_value = state.state if isinstance(state, State) else state
        logger.debug(f"set_state {key.user_id=} {key.chat_id=} {state_value=}")
        try:
            stmt = insert(FSMState).values(
                bot_id=key.bot_id,
                chat_id=key.chat_id,
                user_id=key.user_id,
                destiny=key.destiny,
                state=state_value,
            )
            stmt = stmt.on_duplicate_key_update(state=stmt.inserted.state)
            async with session_factory() as session:
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            logger.error(f"set_state error: {e}", exc_info=True)

    async def get_state(self, key: StorageKey) -> str | None:
        try:
            async with session_factory() as session:
                stmt = select(FSMState.state).where(
                    FSMState.bot_id == key.bot_id,
                    FSMState.chat_id == key.chat_id,
                    FSMState.user_id == key.user_id,
                    FSMState.destiny == key.destiny,
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                return row
        except Exception as e:
            logger.error(f"get_state error: {e}", exc_info=True)
            return None

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]):
        data_json = json.dumps(data, ensure_ascii=False) if data else None
        logger.debug(f"set_data {key.user_id=} {data_json=}")
        try:
            stmt = insert(FSMState).values(
                bot_id=key.bot_id,
                chat_id=key.chat_id,
                user_id=key.user_id,
                destiny=key.destiny,
                data=data_json,
            )
            stmt = stmt.on_duplicate_key_update(data=stmt.inserted.data)
            async with session_factory() as session:
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            logger.error(f"set_data error: {e}", exc_info=True)

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        try:
            async with session_factory() as session:
                stmt = select(FSMState.data).where(
                    FSMState.bot_id == key.bot_id,
                    FSMState.chat_id == key.chat_id,
                    FSMState.user_id == key.user_id,
                    FSMState.destiny == key.destiny,
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                if row:
                    return json.loads(row) if row else {}
                return {}
        except Exception as e:
            logger.error(f"get_data error: {e}", exc_info=True)
            return {}

    async def close(self):
        pass
