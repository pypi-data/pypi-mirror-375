from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Balance:
    """
    Модель баланса бота

    Attributes:
        sweets (float): Основной баланс ирисок
        donate_score (float): Донат-счет
        available (Optional[float]): Доступный баланс (по умолчанию равен sweets)
    """

    gold: int
    sweets: float
    donate_score: int
    available: Optional[float] = None

    def __post_init__(self):
        """Инициализирует available, если не указан"""
        if self.available is None:
            self.available = self.sweets


@dataclass
class DetailsInfo:
    """
    Дополнительная информация о транзакции

    Attributes:
        total (Optional[float]): общая сумма перевода, включая комиссию
        amount (Optional[float]): сколько единиц получил контрагент
        donate_score (Optional[int]): переданных очков доната
        fee (Optional[float]): комиссия перевода
    """

    total: Optional[float] = None
    amount: Optional[float] = None
    donate_score: Optional[int] = None
    fee: Optional[float] = None


@dataclass
class BaseHistoryEntry:
    """
    Базовая модель записи истории операций

    Attributes:
        id (int):
        type (str): тип операции send — отправка, receive — получение 
        date (int): время операции UNIX-time
        amount (float): количество единиц ирисок или голды
        balance (float): новый баланс
        peer_id (int): новое имя поля для контрагента
        to_user_id (int): DEPRECATED. после v0.4. Используйте peer_id
        comment (str): комментарий к переводу
    """

    id: int
    type: str
    date: int
    amount: float
    balance: float
    peer_id: int
    to_user_id: int
    """DEPRECATED. после v0.4. Используйте peer_id"""
    comment: str

    @property
    def datetime(self) -> datetime:
        """Конвертирует timestamp в datetime объект"""
        return datetime.fromtimestamp(self.date / 1000)

@dataclass
class HistorySweetsEntry(BaseHistoryEntry):
    """
    Модель записи истории операций ирисок

    Attributes:
        details (details): детали перевода
    """

    details: DetailsInfo

@dataclass
class HistoryGoldEntry(BaseHistoryEntry):
    """
    Модель записи истории операций ирис-голд

    Attributes:
        details (details): детали перевода
    """

    details: DetailsInfo