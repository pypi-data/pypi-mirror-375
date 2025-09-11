from irisify.__meta__ import __api_version__

from typing import Callable, Optional, List, Union, Any
import requests
import logging
import time
import typing

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


class Irisify:
    """
    Синхронный клиент для работы с API IRIS-TG

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
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": f"irisify/{self.bot_id}"}
        )
        self._last_id = 0

    def _make_request(self, method: str, params: Optional[dict[str, Any]] = None) -> Any:
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
            response = self.session.get(url, params=params, timeout=self.timeout)
            if response.status_code == 401:
                raise AuthorizationError("Invalid credentials")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 400:
                raise InvalidRequestError("Invalid request parameters")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise IrisAPIError(f"Network error: {str(e)}")

    def balance(self) -> Balance:
        """
        Получает текущий баланс бота

        Returns:
            Balance: Объект с информацией о балансе

        Example:
            >>> balance = api.balance()
            >>> print(balance.sweets)
        """
        data = self._make_request("pocket/balance")
        return Balance(gold=data["gold"], sweets=data["sweets"], donate_score=data["donate_score"])

    def give_sweets(
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
            >>>     api.give_sweets(10.5, 12345, "чаевые")
            >>> except NotEnoughSweetsError as e:
            >>>     print(f"Ошибка: {e}")
        """
        params: dict[str, Any] = {
            "sweets": sweets,
            "user_id": user_id,
            "comment": comment,
        }  # type: ignore

        response = self._make_request("pocket/sweets/give", params)  # type: ignore

        if response.get("result"):
            return True

        if "error" in response:
            error = response["error"]
            if error.get("code") == 0 and "Not enough sweets" in error.get("description", ""):
                raise NotEnoughSweetsError(required=sweets)

        raise IrisAPIError(f"Transfer (sweets) failed: {response}")

    def give_gold(
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
            >>>     api.give_gold(10.5, 12345, "чаевые")
            >>> except NotEnoughGoldError as e:
            >>>     print(f"Ошибка: {e}")
        """
        params: dict[str, Any] = {
            "godl": gold,
            "user_id": user_id,
            "comment": comment,
        }  # type: ignore

        response = self._make_request("pocket/gold/give", params)  # type: ignore

        if response.get("result"):
            return True

        if "error" in response:
            error = response["error"]
            if error.get("code") == 0 and "Not enough gold" in error.get("description", ""):
                raise NotEnoughGoldError(required=gold)

        raise IrisAPIError(f"Transfer (gold) failed: {response}")

    def sweets_history(
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
            >>> sweets_history = api.sweets_history(limit = 10)
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
        data = self._make_request("pocket/sweets/history", params)
        data = typing.cast(list[dict[str, Any]], data)
        return [HistorySweetsEntry(**item) for item in data]

    def gold_history(
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
            >>> gold_history = api.gold_history(limit = 10)
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
        data = self._make_request("pocket/gold/history", params)
        data = typing.cast(list[dict[str, Any]], data)
        return [HistoryGoldEntry(**item) for item in data]

    def bag_show(self, on: bool = True):
        """
        Открывает/Закрывает мешок

        Returns:
            bool: True если открытие/закрытие успешеное
        """
        if on:
            response = self._make_request("pocket/enable")
        else:
            response = self._make_request("pocket/disable")
        return response.get("result")

    def get_sweets_transaction(self, transaction_id: int) -> HistorySweetsEntry:
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
            >>>     tx = api.get_sweets_transaction(123456)
            >>> except TransactionSweetsNotFoundError:
            >>>     print("Транзакция не найдена")
        """
        sweets_history = self.sweets_history()
        for entry in sweets_history:
            if entry.id == transaction_id:
                return entry
        raise TransactionSweetsNotFoundError(f"Transaction (sweets) {transaction_id} not found")

    def get_gold_transaction(self, transaction_id: int) -> HistoryGoldEntry:
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
            >>>     tx = api.get_gold_transaction(123456)
            >>> except TransactionGoldNotFoundError:
            >>>     print("Транзакция не найдена")
        """
        sweets_history = self.gold_history()
        for entry in sweets_history:
            if entry.id == transaction_id:
                return entry
        raise TransactionGoldNotFoundError(f"Transaction (gold) {transaction_id} not found")

    def user_all(self, alls: bool = True) -> bool:
        """
        Отвечает за запрещение или разрешение получения валюты от всех пользователей.

        Args:
            alls (bool): включает или отключает получение валюты (по умолчанию True)

        Returns:
            bool: True при успешнном назначением
        """
        if alls:
            response = self._make_request("pocket/allow_all")
        else:
            response = self._make_request("pocket/deny_all")
        return response.get("result")

    def allow_user(self, user_id: Union[int, str], allow: bool = True) -> bool:
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
            response = self._make_request("pocket/allow_user", params)
        else:
            response = self._make_request("pocket/deny_user", params)

        if response.get("result"):
            return True

        raise IrisAPIError(f"Allow user failed: {response}")

    def track_transactions(
        self,
        callback: Callable[[HistorySweetsEntry], None],
        poll_interval: float = 1.0,
        initial_offset: Optional[int] = None,
    ):
        """
        Отслеживает новые транзакции

        Args:
            callback (Callable[[HistorySweetsEntry], None]): Функция для обработки новых транзакций
            poll_interval (float): Интервал опроса в секундах (по умолчанию 1.0)
            initial_offset (Optional[int]): Начальное смещение (если None, начинает с последней)

        Example:
            >>> def handle_tx(tx):
            >>>     print(f"Новая транзакция: {tx.id}")
            >>>
            >>> api.track_transactions(handle_tx)
        """
        if initial_offset is not None:
            self._last_id = initial_offset
        else:
            last_tx = self.sweets_history(limit=1)
            self._last_id = last_tx[0].id if last_tx else 0

        while True:
            try:
                new_transactions = self.sweets_history(offset=self._last_id + 1)

                if new_transactions:
                    for tx in new_transactions:
                        callback(tx)
                        self._last_id = tx.id
                else:
                    time.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Tracking error: {e}")
                time.sleep(self.RECONNECT_DELAY)
