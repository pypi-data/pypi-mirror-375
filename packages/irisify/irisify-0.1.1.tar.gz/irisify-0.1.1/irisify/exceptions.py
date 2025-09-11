from typing import Optional


class IrisAPIError(Exception):
    """Базовый класс для всех ошибок API"""

    pass


class AuthorizationError(IrisAPIError):
    """Ошибка авторизации (неверные учетные данные)"""

    pass


class RateLimitError(IrisAPIError):
    """Превышен лимит запросов к API"""

    pass


class InvalidRequestError(IrisAPIError):
    """Некорректные параметры запроса"""

    pass


class NotEnoughSweetsError(IrisAPIError):
    """Недостаточно ирисок для выполнения операции"""

    def __init__(self, required: float, available: Optional[float] = None):
        """
        Args:
            required (float): Требуемое количество ирисок
            available (Optional[float]): Доступное количество ирисок
        """
        self.required = required
        self.available = available
        message = f"Недостаточно ирисок. Требуется: {required}"
        if available is not None:
            message += f", доступно: {available}"
        super().__init__(message)

class NotEnoughGoldError(IrisAPIError):
    """Недостаточно ирис-голд для выполнения операции"""

    def __init__(self, required: float, available: Optional[float] = None):
        """
        Args:
            required (float): Требуемое количество ирис-голд
            available (Optional[float]): Доступное количество ирис-голд
        """
        self.required = required
        self.available = available
        message = f"Недостаточно ирис-голд. Требуется: {required}"
        if available is not None:
            message += f", доступно: {available}"
        super().__init__(message)


class TransactionSweetsNotFoundError(IrisAPIError):
    """Транзакция (sweets) не найдена"""

    pass

class TransactionGoldNotFoundError(IrisAPIError):
    """Транзакция (gold) не найдена"""

    pass
