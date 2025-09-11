# Документация

## Заготовка
```python
from irisify import IrisAPIAsync
from irisify.models import HistorySweetsEntry
import asyncio

async def main():
    async with IrisAPIAsync(bot_id = 12345, iris_token = "YOUR_IRIS_TOKEN") as api:
        pass # Cюда код который работает с Iris API

asyncio.run(main())
```

## Все методы библиотеки
### Получение баланса
```python
balance = await api.balance()
print(balance.sweets, balance.donate_score)
```
| Статичные переменные  | Типы  |
| ------------- | ------------- |
| sweets        |    float      |
| donate_score  |    float      |
| available     |Optional[float]|

### Передача ирисок
```python
try:
    await api.give_sweets(
        sweets = 10.5,
        user_id = 123456789,
        comment = "Чаевые"
    )
except NotEnoughSweetsError as e:
    print(f"Недостаточно ирисок! Требуется: {e.required}")
```
| Входные данные  | Типы  |
| ------------- | --------------- |
| sweets        |Union[int, float]|
| user_id       | Union[int, str] |
| comment       |       str       |
#### Если не хватает ирисок для передачи вызывается исключение NotEnoughSweetsError

#### Если операция не прошла вызывается исключение IrisAPIError

#### По умолчанию пустая строка в comment

### Получение истории операций
```python
sweets_history = await api.sweets_history(limit = 10)
for tx in sweets_history:
    print(f"{tx.datetime}: {tx.type} {tx.amount}")
```
| Входные данные  | Типы  |
| ------------- | --------------- |
| offset        |  Optional[int]  |
| limit         |  Optional[int]  |
| user_id       |  Optional[int]  |
| transaction_type |  Optional[str]  |
#### Указание входных данных необязательно

### Получение информации о конкретной операции
```python
t = await api.get_sweets_transaction(transaction_id = 10)

print(f"{t.datetime}: {t.type} {t.amount}")
```
| Входные данные  | Типы  |
| ------------- | --------------- |
| transaction_id|  Optional[int]  |
#### Если операция с transaction_id не найдена вызывается исключение TransactionSweetsNotFoundError

#### Указание входных данных обязательно

### Получение информации о новых операциях
```python
async def handle_transaction(tx):
    print(f"Новая операция: {tx.id}")

await api.track_transactions(
    callback = handle_transaction,
    poll_interval = 1.0
)
```
| Входные данные  | Типы  |
| ------------- | --------------- |
| callback      |Callable[[HistorySweetsEntry], None]|
| poll_interval |  float          |
| initial_offset|  Optional[int]  |
#### callback обязательно должен быть указан
#### poll_interval и initial_offset необязательны к указанию

### **Не забудьте изменить все входные данные!**
