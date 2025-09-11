from irisify.__meta__ import __api_version__

from typing import Any, Callable, List, Optional, Type, Union
import asyncio
import logging
import typing
import aiohttp

from .models import Balance, HistorySweetsEntry, HistoryGoldEntry
from .exceptions import (
    InvalidRequestError,
    AuthorizationError,
    RateLimitError,
    IrisAPIError,
    NotEnoughSweetsError,
    NotEnoughGoldError,
    TransactionSweetsNotFoundError,
    TransactionGoldNotFoundError,
)

logger = logging.getLogger(__name__)


class IrisAPIAsync:
    """
    Асинхронный клиент для работы с API IRIS-TG

    Args:
        bot_id (int): ID бота в системе IRIS-TG
        iris_token (str): Токен авторизации
        base_url (Optional[str]): Базовый URL API (по умолчанию 'https://iris-tg.ru/api')
        timeout (Optional[int]): Таймаут запросов в секундах (по умолчанию 10)
    """

    BASE_URL = f"https://iris-tg.ru/api/v{__api_version__}"
    DEFAULT_TIMEOUT = 10
    RECONNECT_DELAY = 5

    def __init__(
        self,
        bot_id: int,
        iris_token: str,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.bot_id = f"{bot_id}"
        self.iris_token = iris_token
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.session = None
        self._last_id = 0

    async def __aenter__(self):
        """Контекстный менеджер для автоматического подключения"""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Контекстный менеджер для автоматического закрытия"""
        await self.close()

    async def connect(self):
        """Устанавливает соединение с API"""
        self.session = aiohttp.ClientSession(
            headers={
                "Accept": "application/json",
                "User-Agent": f"IrisAPIAsync/{self.bot_id}",
            },
            timeout=aiohttp.ClientTimeout(total=self.timeout),
        )

    async def close(self):
        """Закрывает соединение с API"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _make_request(
        self, method: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Базовый метод для выполнения запросов к API

        Args:
            method (str): Метод API (например 'balance')
            params (Optional[dict]): Параметры запроса

        Returns:
            dict: Ответ API

        Raises:
            AuthorizationError: При ошибках авторизации
            RateLimitError: При превышении лимита запросов
            InvalidRequestError: При неверных параметрах запроса
            IrisAPIError: При других ошибках API
        """
        url = f"{self.base_url}/{self.bot_id}_{self.iris_token}/{method}"

        try:
            if self.session is None:
                raise IrisAPIError("Session is not initialized. Call connect() first.")
            async with self.session.get(url, params=params) as response:
                if response.status == 401:
                    raise AuthorizationError("Invalid credentials")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status == 400:
                    raise InvalidRequestError("Invalid request parameters")

                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            raise IrisAPIError(f"Network error: {str(e)}")

    async def balance(self) -> Balance:
        """
        Получает текущий баланс бота

        Returns:
            Balance: Объект с информацией о балансе

        Example:
            >>> balance = await api.balance()
            >>> print(balance.sweets)
        """
        data = await self._make_request("pocket/balance")
        return Balance(gold=data["gold"], sweets=data["sweets"], donate_score=data["donate_score"])

    async def give_sweets(
        self, sweets: Union[int, float], user_id: Union[int, str], comment: str = ""
    ) -> bool:
        """
        Отправляет ириски пользователю

        Args:
            sweets (Union[int, float]): Количество ирисок для отправки
            user_id (Union[int, str]): ID пользователя-получателя
            comment (str): Комментарий к переводу

        Returns:
            bool: True если перевод успешен

        Raises:
            NotEnoughSweetsError: Если недостаточно ирисок
            IrisAPIError: При других ошибках

        Example:
            >>> try:
            >>>     await api.give_sweets(10.5, 12345, "чаевые")
            >>> except NotEnoughSweetsError as e:
            >>>     print(f"Ошибка: {e}")
        """
        params: dict[str, Any] = {
            "sweets": sweets,
            "user_id": user_id,
            "comment": comment,
        }  # type: ignore

        response = await self._make_request("pocket/sweets/give", params)  # type: ignore

        if response.get("result"):
            return True

        if "error" in response:
            error = response["error"]
            if error.get("code") == 409 and "Not enough sweets" in error.get("description", ""):
                raise NotEnoughSweetsError(required=sweets)

        raise IrisAPIError(f"Transfer (sweets) failed: {response}")

    async def give_gold(
        self, gold: Union[int, float], user_id: Union[int, str], comment: str = ""
    ) -> bool:
        """
        Отправляет ирис-голд пользователю

        Args:
            gold (Union[int, float]): Количество ирис-голд для отправки
            user_id (Union[int, str]): ID пользователя-получателя
            comment (str): Комментарий к переводу

        Returns:
            bool: True если перевод успешен

        Raises:
            NotEnoughGoldError: Если недостаточно ирис-голд
            IrisAPIError: При других ошибках

        Example:
            >>> try:
            >>>     await api.give_gold(10.5, 12345, "чаевые")
            >>> except NotEnoughGoldError as e:
            >>>     print(f"Ошибка: {e}")
        """
        params: dict[str, Any] = {
            "godl": gold,
            "user_id": user_id,
            "comment": comment,
        }  # type: ignore

        response = await self._make_request("pocket/gold/give", params)  # type: ignore

        if response.get("result"):
            return True

        if "error" in response:
            error = response["error"]
            if error.get("code") == 409 and "Not enough gold" in error.get("description", ""):
                raise NotEnoughGoldError(required=gold)

        raise IrisAPIError(f"Transfer (gold) failed: {response}")

    async def sweets_history(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        user_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
    ) -> List[HistorySweetsEntry]:
        """
        Получает историю транзакций с возможностью фильтрации

        Args:
            offset (Optional[int]): Смещение для пагинации
            limit (Optional[int]): Лимит записей
            user_id (Optional[int]): Фильтр по ID пользователя
            transaction_type (Optional[str]): Фильтр по типу ("give" или "take")

        Returns:
            List[HistorySweetsEntry]: Список транзакций

        Example:
            >>> sweets_history = await api.sweets_history(limit = 10)
            >>> for tx in sweets_history:
            >>>     print(tx.amount)
        """
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if user_id is not None:
            params["user_id"] = user_id
        if transaction_type is not None:
            params["type"] = transaction_type
        data = await self._make_request("pocket/sweets/history", params)
        data = typing.cast(list[dict[str, Any]], data)
        return [HistorySweetsEntry(**item) for item in data]

    async def gold_history(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        user_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
    ) -> List[HistoryGoldEntry]:
        """
        Получает историю транзакций с возможностью фильтрации

        Args:
            offset (Optional[int]): Смещение для пагинации
            limit (Optional[int]): Лимит записей
            user_id (Optional[int]): Фильтр по ID пользователя
            transaction_type (Optional[str]): Фильтр по типу ("give" или "take")

        Returns:
            List[HistoryGoldEntry]: Список транзакций

        Example:
            >>> gold_history = await api.gold_history(limit = 10)
            >>> for tx in gold_history:
            >>>     print(tx.amount)
        """
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if user_id is not None:
            params["user_id"] = user_id
        if transaction_type is not None:
            params["type"] = transaction_type
        data = await self._make_request("pocket/gold/history", params)
        data = typing.cast(list[dict[str, Any]], data)
        return [HistoryGoldEntry(**item) for item in data]

    async def bag_show(self, on: bool = True) -> bool:
        """
        Открывает/Закрывает мешок

        Args:
            on (bool): включает или отключает получение валюты (по умолчанию True)

        Returns:
            bool: True если открытие/закрытие успешеное
        """
        if on:
            response = await self._make_request("pocket/enable")
        else:
            response = await self._make_request("pocket/disable")
        return response.get("result")

    async def get_sweets_transaction(self, transaction_id: int) -> HistorySweetsEntry:
        """
        Получает информацию о конкретной транзакции

        Args:
            transaction_id (int): ID транзакции

        Returns:
            HistorySweetsEntry: Информация о транзакции

        Raises:
            TransactionSweetsNotFoundError: Если транзакция не найдена

        Example:
            >>> try:
            >>>     tx = await api.get_sweets_transaction(123456)
            >>> except TransactionSweetsNotFoundError:
            >>>     print("Транзакция не найдена")
        """
        sweets_history = await self.sweets_history()
        for entry in sweets_history:
            if entry.id == transaction_id:
                return entry
        raise TransactionSweetsNotFoundError(f"Transaction (sweets) {transaction_id} not found")

    async def get_gold_transaction(self, transaction_id: int) -> HistoryGoldEntry:
        """
        Получает информацию о конкретной транзакции

        Args:
            transaction_id (int): ID транзакции

        Returns:
            HistoryGoldEntry: Информация о транзакции

        Raises:
            TransactionGoldNotFoundError: Если транзакция не найдена

        Example:
            >>> try:
            >>>     tx = await api.get_gold_transaction(123456)
            >>> except TransactionGoldNotFoundError:
            >>>     print("Транзакция не найдена")
        """
        sweets_history = await self.gold_history()
        for entry in sweets_history:
            if entry.id == transaction_id:
                return entry
        raise TransactionGoldNotFoundError(f"Transaction (gold) {transaction_id} not found")

    async def user_all(self, alls: bool = True) -> bool:
        """
        Отвечает за запрещение или разрешение получения валюты от всех пользователей.

        Args:
            alls (bool): включает или отключает получение валюты (по умолчанию True)

        Returns:
            bool: True при успешнном назначением
        """
        if alls:
            response = await self._make_request("pocket/allow_all")
        else:
            response = await self._make_request("pocket/deny_all")
        return response.get("result")

    async def allow_user(self, user_id: Union[int, str], allow: bool = True) -> bool:
        """
        Отвечает за запрещение или разрешение получения валюты от конкретного пользователей.

        Args:
            user_id (Union[int, str]): ID пользователя
            allow (bool): запрещает или разрешает получение валюты (по умолчанию True)

        Raises:
            IrisAPIError: При ошибках

        Returns:
            bool: True при успешнном назначением
        """
        params = {"user_id": user_id}

        if allow:
            response = await self._make_request("pocket/allow_user", params)
        else:
            response = await self._make_request("pocket/deny_user", params)

        if response.get("result"):
            return True

        raise IrisAPIError(f"Allow user failed: {response}")

    async def track_transactions(
        self,
        callback: Callable[[HistorySweetsEntry], None],
        poll_interval: float = 1.0,
        initial_offset: Optional[int] = None,
    ):
        """
        Отслеживает новые транзакции в реальном времени

        Args:
            callback (Callable[[HistorySweetsEntry], None]): Функция для обработки новых транзакций
            poll_interval (float): Интервал опроса в секундах (по умолчанию 1.0)
            initial_offset (Optional[int]): Начальное смещение (если None, начинает с последней)

        Example:
            >>> async def handle_tx(tx):
            >>>     print(f"Новая транзакция: {tx.id}")
            >>>
            >>> await api.track_transactions(handle_tx)
        """
        import inspect

        if initial_offset is not None:
            self._last_id = initial_offset
        else:
            last_tx = await self.sweets_history(limit=1)
            self._last_id = last_tx[0].id if last_tx else 0

        while True:
            try:
                new_transactions = await self.sweets_history(offset=self._last_id + 1)

                if new_transactions:
                    for tx in new_transactions:
                        if inspect.iscoroutinefunction(callback):
                            await callback(tx)
                        else:
                            callback(tx)
                        self._last_id = tx.id
                else:
                    await asyncio.sleep(poll_interval)

            except asyncio.CancelledError:
                logger.info("Transaction tracking stopped")
                break
            except Exception as e:
                logger.error(f"Tracking error: {e}")
                await asyncio.sleep(self.RECONNECT_DELAY)
