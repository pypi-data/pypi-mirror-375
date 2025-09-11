from typing import Any, Awaitable, Callable, Dict

from ...types import VKEvent
from ..middleware import BaseMiddleware
from .context import FSMContext
from .storage import BaseStorage


class FSMMiddleware(BaseMiddleware):
    """
    Встроенный middleware для поддержки FSM.
    Автоматически создает и внедряет FSMContext в каждый обработчик.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[VKEvent, Dict[str, Any]], Awaitable[Any]],
        event: VKEvent,
        data: Dict[str, Any],
    ) -> Any:
        # Создаем FSMContext, используя переданное хранилище
        context = FSMContext(
            storage=self.storage, user_id=event.user_id, peer_id=event.peer_id
        )
        # Внедряем его в данные под ключом 'state'
        data["state"] = context
        return await handler(event, data)
