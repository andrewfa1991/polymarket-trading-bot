# 🤖 Polymarket Trading Bot - Полное Руководство

## 📋 Содержание
1. [Быстрый старт](#быстрый-старт)
2. [Режимы работы](#режимы-работы)
3. [Торговые стратегии](#торговые-стратегии)
4. [Инструменты анализа](#инструменты-анализа)
5. [Параметры и настройки](#параметры-и-настройки)

---

## 🚀 Быстрый старт

### Установка зависимостей:
```bash
pip install -r requirements.txt
```

### Настройка .env файла:
Файл `.env` уже создан с вашими credentials. Проверьте что все ключи на месте:
```bash
cat .env
```

### Проверка работоспособности:
```bash
# Запуск тестов (98 тестов)
python3 -m pytest tests/ -v

# Быстрое демо
python3 scripts/run_bot.py
```

---

## 🎮 Режимы работы

### 1️⃣ Quick Demo (быстрая проверка)
```bash
python3 scripts/run_bot.py
```
**Что делает:**
- Показывает статус бота
- Выводит количество открытых ордеров
- Проверяет подключение к API

---

### 2️⃣ Interactive Mode (ручная торговля)
```bash
python3 scripts/run_bot.py --interactive
```

**Доступные команды:**

| Команда | Описание | Пример |
|---------|----------|--------|
| `help` | Показать справку | `help` |
| `status` | Статус бота и открытые ордера | `status` |
| `place` | Разместить ордер | `place 0x123... 0.65 10 BUY` |
| `cancel` | Отменить ордер | `cancel order_123` |
| `cancel-all` | Отменить все ордера | `cancel-all` |
| `trades` | Показать последние сделки | `trades` |
| `price` | Получить цену рынка | `price 0x123...` |
| `exit` | Выход из бота | `exit` |

**Примеры использования:**
```bash
# Купить 10 токенов по цене 0.65
place 0x1234567890abcdef 0.65 10 BUY

# Продать 5 токенов по цене 0.70
place 0x1234567890abcdef 0.70 5 SELL

# Узнать текущую цену
price 0x1234567890abcdef

# Отменить конкретный ордер
cancel order_abc123
```

---

## 📈 Торговые стратегии

### 🔥 1. Flash Crash Strategy (Волатильность)

**Описание:** Ловит резкие падения цены и покупает на просадке

**Запуск:**
```bash
python3 apps/run_flash_crash.py --coin ETH
```

**Все параметры:**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `--coin` | str | ETH | Монета (BTC, ETH, SOL, XRP) |
| `--size` | float | 5.0 | Размер позиции в USDC |
| `--drop` | float | 0.30 | Порог падения (изменение цены 0-1) |
| `--lookback` | int | 10 | Окно анализа в секундах |
| `--take-profit` | float | 0.10 | Тейк-профит (изменение цены) |
| `--stop-loss` | float | 0.05 | Стоп-лосс (изменение цены) |
| `--paper` | flag | false | Виртуальная торговля |
| `--balance` | float | - | % от баланса для размера позиции |
| `--debug` | flag | false | Debug логирование |

**⚠️ ВАЖНО про Take-Profit и Stop-Loss:**

Параметры указываются в **изменении цены** (price delta), НЕ в долларах!

**Пример расчёта:**
- Вход по цене: **0.35** (35% вероятность)
- `--take-profit 0.10` → продажа при цене **0.45** (0.35 + 0.10)
- `--stop-loss 0.05` → продажа при цене **0.30** (0.35 - 0.05)

**Реальный PnL в долларах:**
```
PnL = (exit_price - entry_price) × size
```

При размере 10 USDC:
- Take profit: (0.45 - 0.35) × 10 = **+$1.00**
- Stop loss: (0.30 - 0.35) × 10 = **-$0.50**

**Примеры команд:**
```bash
# BTC с размером 10 USDC
python3 apps/run_flash_crash.py --coin BTC --size 10

# ETH с порогом падения 25%
python3 apps/run_flash_crash.py --coin ETH --drop 0.25

# SOL с кастомными TP/SL
python3 apps/run_flash_crash.py --coin SOL --take-profit 0.15 --stop-loss 0.08

# Paper trading (виртуальная торговля)
python3 apps/run_flash_crash.py --coin BTC --paper --size 20

# Использовать 10% от баланса
python3 apps/run_flash_crash.py --coin ETH --balance 0.10

# Полная конфигурация
python3 apps/run_flash_crash.py --coin BTC --size 20 --drop 0.35 --lookback 15 --take-profit 0.20 --stop-loss 0.10 --debug
```

**Логика стратегии:**
1. Автоматически находит текущий 15-минутный рынок
2. Мониторит цены через WebSocket в реальном времени
3. Когда цена падает на 0.30+ за 10 секунд → покупает упавшую сторону
4. Выходит при достижении take-profit или stop-loss
5. **Автоматически переключается на новый рынок через 5 секунд после закрытия**

---

### 💎 2. Fair Value Strategy (Справедливая цена)

**Описание:** Использует Black-Scholes модель для расчёта справедливой цены бинарных опционов на основе цены BTC с Binance

**Запуск:**
```bash
python3 apps/run_fair_value.py --coin BTC --duration 5
```

**Параметры:**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `--coin` | str | BTC | Монета (пока только BTC) |
| `--duration` | int | 5 | Длительность рынка (5 или 15 минут) |
| `--size` | float | 0.0 | Размер в USDC (0 = авто от баланса) |
| `--edge` | float | 0.05 | Минимальное преимущество для входа |
| `--vol-window` | int | 300 | Окно для расчёта волатильности (сек) |
| `--kelly` | float | 0.25 | Kelly fraction для sizing |
| `--take-profit` | float | 0.10 | Тейк-профит (изменение цены) |
| `--stop-loss` | float | 0.05 | Стоп-лосс (изменение цены) |
| `--min-time` | float | 30.0 | Мин. время до конца для входа (сек) |
| `--paper` | float | - | Paper trading с начальным балансом |
| `--debug` | flag | false | Debug логирование |

**Примеры:**
```bash
# Стандартный запуск на 5-минутных рынках
python3 apps/run_fair_value.py --coin BTC --duration 5

# Paper trading с балансом $20
python3 apps/run_fair_value.py --coin BTC --paper 20

# Кастомные параметры
python3 apps/run_fair_value.py --coin BTC --edge 0.03 --vol-window 120 --kelly 0.15

# 15-минутные рынки
python3 apps/run_fair_value.py --coin BTC --duration 15 --size 10
```

**Логика стратегии:**
1. Получает spot цену BTC с Binance WebSocket
2. Рассчитывает справедливую цену (fair value) по формуле Black-Scholes
3. Сравнивает с ценой на Polymarket
4. Покупает если есть edge (преимущество) больше порога
5. Использует Kelly criterion для sizing

**Формула Fair Value:**
```
fv_up = N(d2) где d2 = [ln(S/K) + (-σ²/2)×T] / (σ × √T)
```
- S = текущая цена BTC
- K = strike (цена на момент открытия рынка)
- T = время до экспирации
- σ = realized volatility

---

### 📚 3. Дополнительные стратегии (папка `strategy/`)

Это **backtest-only** стратегии для анализа исторических данных:

#### **Book Imbalance** (дисбаланс ордербука)
```bash
python3 strategy/book_imbalance.py data/btc-5m-2026-02-14.jsonl
```
Покупает сторону с более узким спредом (уверенные маркет-мейкеры)

#### **Convergence** (конвергенция)
```bash
python3 strategy/convergence.py data/btc-5m-2026-02-14.jsonl
```
Торгует на схождении цен UP и DOWN к 0.50

#### **Early Momentum** (ранний импульс)
```bash
python3 strategy/early_momentum.py data/btc-5m-2026-02-14.jsonl
```
Входит в начале рынка при сильном движении цены

#### **Lead-Lag** (опережение/запаздывание)
```bash
python3 strategy/lead_lag.py data/btc-5m-2026-02-14.jsonl
```
Использует корреляцию между UP и DOWN сторонами

#### **Sum Arbitrage** (арбитраж суммы)
```bash
python3 strategy/sum_arb.py data/btc-5m-2026-02-14.jsonl
```
Торгует когда сумма UP + DOWN отклоняется от 1.0

---

## 🔬 Инструменты анализа

### 📊 1. Data Recorder (запись данных)

**Описание:** Записывает orderbook данные в JSONL файл для последующего бэктестинга

**Запуск:**
```bash
python3 apps/record_data.py --coin BTC --duration 5
```

**Параметры:**

| Параметр | Описание | Пример |
|----------|----------|--------|
| `--coin` | Монета для записи | `--coin ETH` |
| `--duration` | Длительность рынка (5 или 15 мин) | `--duration 15` |
| `--output` | Путь к файлу | `--output data/btc-5m.jsonl` |
| `--sample-interval` | Интервал записи (сек) | `--sample-interval 1.0` |

**Примеры:**
```bash
# Записать BTC 5-минутные рынки
python3 apps/record_data.py --coin BTC --duration 5 --output data/btc-5m.jsonl

# Записать ETH 15-минутные рынки с интервалом 0.5 сек
python3 apps/record_data.py --coin ETH --duration 15 --sample-interval 0.5
```

**Формат данных:**
```json
{"t": 1771063800.5, "slug": "btc-updown-5m-...", "end": "2026-...",
 "up": {"mid": 0.55, "bid": 0.54, "ask": 0.56, "spread": 0.02},
 "down": {"mid": 0.45, "bid": 0.44, "ask": 0.46, "spread": 0.02}}
```

---

### 📉 2. Backtester (бэктестинг)

**Описание:** Проигрывает записанные данные через стратегию для оценки производительности

**Запуск:**
```bash
python3 apps/backtest.py data/btc-5m-2026-02-14.jsonl
```

**Параметры:**

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `--balance` | Начальный баланс | 10.0 USDC |
| `--bet-fraction` | % от баланса на сделку | 0.10 (10%) |
| `--drop` | Порог падения | 0.30 |
| `--lookback` | Окно анализа (сек) | 10 |
| `--tp` | Take profit | 0.10 |
| `--sl` | Stop loss | 0.05 |
| `--no-trade-seconds` | Cooldown между сделками | 30 |
| `--sweep` | Перебор параметров | flag |

**Примеры:**
```bash
# Одиночный прогон
python3 apps/backtest.py data/btc-5m.jsonl --drop 0.25 --tp 0.08 --sl 0.04

# Sweep - перебор параметров для оптимизации
python3 apps/backtest.py data/btc-5m.jsonl --sweep

# С кастомным балансом
python3 apps/backtest.py data/btc-5m.jsonl --balance 100 --bet-fraction 0.05
```

**Вывод:**
```
════════════════════════════════════════════════════════════════════
                        BACKTEST RESULTS
════════════════════════════════════════════════════════════════════
Markets:        15
Trades:         8
Win Rate:       62.5%
Total PnL:      +$2.45
Final Balance:  $12.45 (24.5% return)
════════════════════════════════════════════════════════════════════
```

---

### 📺 3. Orderbook TUI (визуализация)

**Описание:** Отображает live orderbook в терминале

**Запуск:**
```bash
python3 apps/orderbook_tui.py --coin BTC --levels 5
```

**Параметры:**
- `--coin` - монета (BTC, ETH, SOL, XRP)
- `--levels` - количество уровней цен (default: 5)
- `--duration` - длительность рынка в минутах (5 или 15)

---

## 🎯 Торговые стратегии - Подробное описание

### Strategy 1: Flash Crash (Основная стратегия)

**Когда использовать:** Высокая волатильность, резкие движения цены

**Оптимальные параметры для разных монет:**

#### BTC (низкая волатильность):
```bash
python3 apps/run_flash_crash.py --coin BTC --drop 0.25 --size 10 --take-profit 0.08 --stop-loss 0.04
```

#### ETH (средняя волатильность):
```bash
python3 apps/run_flash_crash.py --coin ETH --drop 0.30 --size 8 --take-profit 0.10 --stop-loss 0.05
```

#### SOL/XRP (высокая волатильность):
```bash
python3 apps/run_flash_crash.py --coin SOL --drop 0.35 --size 5 --take-profit 0.15 --stop-loss 0.08
```

**Риск-менеджмент:**
- Консервативный: `--size 5 --take-profit 0.08 --stop-loss 0.03`
- Средний: `--size 10 --take-profit 0.10 --stop-loss 0.05`
- Агрессивный: `--size 20 --take-profit 0.15 --stop-loss 0.08`

---

### Strategy 2: Fair Value (Black-Scholes)

**Когда использовать:** Спокойный рынок, цены отклоняются от справедливых

**Запуск:**
```bash
python3 apps/run_fair_value.py --coin BTC --duration 5
```

**Оптимальные параметры:**

#### Консервативный подход:
```bash
python3 apps/run_fair_value.py --coin BTC --edge 0.07 --kelly 0.15 --vol-window 300
```
- Высокий edge (0.07) = меньше сделок, но более уверенных
- Низкий Kelly (0.15) = меньший риск

#### Агрессивный подход:
```bash
python3 apps/run_fair_value.py --coin BTC --edge 0.03 --kelly 0.35 --vol-window 120
```
- Низкий edge (0.03) = больше сделок
- Высокий Kelly (0.35) = больший размер позиций

#### Paper trading для тестирования:
```bash
python3 apps/run_fair_value.py --coin BTC --paper 50 --edge 0.05
```

**Как работает:**
1. Подключается к Binance WebSocket для получения spot цены BTC
2. Рассчитывает realized volatility за последние N секунд
3. Вычисляет fair value по формуле Black-Scholes
4. Сравнивает с ценой на Polymarket
5. Если edge > порог → входит в позицию
6. Sizing по Kelly criterion

---

## 🛠️ Инструменты разработки

### 1. Запись данных для бэктеста
```bash
# Записать 1 час данных BTC
python3 apps/record_data.py --coin BTC --duration 5 --output data/btc-5m-$(date +%Y%m%d).jsonl

# Оставить на ночь (запись будет идти пока не остановите Ctrl+C)
nohup python3 apps/record_data.py --coin ETH --duration 15 --output data/eth-15m.jsonl &
```

### 2. Бэктестинг записанных данных
```bash
# Прогнать Flash Crash стратегию
python3 apps/backtest.py data/btc-5m-20260315.jsonl --drop 0.30

# Оптимизация параметров
python3 apps/backtest.py data/btc-5m-20260315.jsonl --sweep
```

### 3. Анализ стратегий на исторических данных
```bash
# Fair Value backtest
python3 strategy/fair_value.py data/btc-5m-20260315.jsonl --edge 0.05

# Book Imbalance backtest
python3 strategy/book_imbalance.py data/btc-5m-20260315.jsonl

# Sweep для нахождения лучших параметров
python3 strategy/convergence.py data/btc-5m-20260315.jsonl --sweep
```

---

## ⚙️ Параметры и настройки

### Переменные окружения (.env файл)

```bash
# Обязательные
POLY_PRIVATE_KEY=...              # Приватный ключ MetaMask
POLY_SAFE_ADDRESS=...             # Адрес Polymarket Safe

# Для gasless транзакций (Builder Program)
POLY_BUILDER_API_KEY=...
POLY_BUILDER_API_SECRET=...
POLY_BUILDER_API_PASSPHRASE=...

# Опциональные
POLY_RPC_URL=https://polygon-rpc.com
POLY_CHAIN_ID=137
POLY_CLOB_HOST=https://clob.polymarket.com
POLY_DEFAULT_SIZE=1.0
POLY_DEFAULT_PRICE=0.5
POLY_DATA_DIR=credentials
POLY_LOG_LEVEL=INFO
```

### Конфигурация через config.yaml

Альтернатива .env файлу:
```yaml
safe_address: "0xYourSafeAddress"

builder:
  api_key: "your_api_key"
  api_secret: "your_api_secret"
  api_passphrase: "your_passphrase"

clob:
  host: "https://clob.polymarket.com"
  chain_id: 137

default_size: 5.0
default_price: 0.5
```

---

## 🎓 Рекомендации по использованию

### Для начинающих:

1. **Начните с paper trading:**
```bash
python3 apps/run_flash_crash.py --coin ETH --paper --size 10
```

2. **Запишите данные для анализа:**
```bash
python3 apps/record_data.py --coin BTC --duration 5 --output data/test.jsonl
# Подождите 1-2 часа, затем Ctrl+C
```

3. **Протестируйте на записанных данных:**
```bash
python3 apps/backtest.py data/test.jsonl --sweep
```

4. **Запустите с минимальным размером:**
```bash
python3 apps/run_flash_crash.py --coin ETH --size 1
```

### Для опытных трейдеров:

1. **Оптимизируйте параметры через sweep:**
```bash
python3 apps/backtest.py data/btc-5m-week.jsonl --sweep
```

2. **Комбинируйте стратегии:**
```bash
# Terminal 1: Flash Crash на BTC
python3 apps/run_flash_crash.py --coin BTC --size 10

# Terminal 2: Fair Value на ETH
python3 apps/run_fair_value.py --coin ETH --size 8
```

3. **Используйте balance-based sizing:**
```bash
python3 apps/run_flash_crash.py --coin BTC --balance 0.05  # 5% от баланса
```

---

## 📊 Мониторинг и логи

### Просмотр логов:
```bash
# В реальном времени
tail -f logs/bot.log

# Фильтр по ошибкам
grep ERROR logs/bot.log
```

### Debug режим:
```bash
python3 apps/run_flash_crash.py --coin BTC --debug
```

### Проверка статуса через API:
```bash
python3 -c "
from src.utils import create_bot_from_env
import asyncio

async def check():
    bot = create_bot_from_env()
    orders = await bot.get_open_orders()
    trades = await bot.get_trades(limit=10)
    print(f'Open orders: {len(orders)}')
    print(f'Recent trades: {len(trades)}')

asyncio.run(check())
"
```

---

## 🔐 Безопасность

1. **Никогда не коммитьте .env файл** (уже в .gitignore)
2. **Используйте отдельный кошелёк** для торговли
3. **Начинайте с малых сумм** ($1-5)
4. **Тестируйте в paper mode** перед реальной торговлёй
5. **Регулярно проверяйте баланс** и открытые позиции

---

## 🆘 Troubleshooting

| Проблема | Решение |
|----------|---------|
| `401 Unauthorized` | Проверьте POLY_BUILDER_* credentials |
| `ModuleNotFoundError` | Запустите `pip install -r requirements.txt` |
| WebSocket не подключается | Проверьте интернет/firewall |
| Бот не переключает рынки | Убедитесь что `auto_switch_market=True` |
| Нет сделок | Попробуйте снизить `--drop` порог |

---

## 📈 Статистика и метрики

Бот отслеживает:
- **Открытые позиции** (open_positions)
- **Закрытые сделки** (trades_closed)
- **Выигрышные/проигрышные** (winning_trades / losing_trades)
- **Win Rate** (процент прибыльных сделок)
- **Total PnL** (общая прибыль/убыток)
- **Unrealized PnL** (нереализованная прибыль открытых позиций)

Просмотр статистики:
```bash
python3 scripts/run_bot.py --interactive
# В консоли введите: status
```

---

## 🎯 Ключевые особенности обновлённого бота

### ✅ Что исправлено:
1. **L2 Authentication** - корректный `signer_address` в заголовках
2. **Position Type** - правильная типизация в стратегиях
3. **WebSocket Parsing** - обработка массивов сообщений
4. **Market Switching** - переключение на новый рынок через **5 секунд**

### 🆕 Что добавлено:
1. **6 новых стратегий** для бэктестинга
2. **Binance интеграция** для Fair Value расчётов
3. **Paper trading** режим
4. **Backtest framework** с sweep оптимизацией
5. **Data recorder** для сбора исторических данных
6. **Balance-based sizing** - авто размер от баланса
7. **5-minute markets** поддержка

### 🚀 Производительность:
- **98/98 тестов** проходят
- **Gasless транзакции** через Builder Program
- **Real-time WebSocket** для мгновенных данных
- **Автоматическое переключение** рынков
- **Zero blind spot** при переходе между рынками

---

## 📞 Быстрая справка

```bash
# Запуск основной стратегии
python3 apps/run_flash_crash.py --coin ETH --size 10

# Paper trading для тестирования
python3 apps/run_flash_crash.py --coin BTC --paper --size 20

# Fair Value с Binance
python3 apps/run_fair_value.py --coin BTC --duration 5

# Запись данных
python3 apps/record_data.py --coin BTC --duration 5

# Бэктестинг
python3 apps/backtest.py data/btc-5m.jsonl --sweep

# Интерактивный режим
python3 scripts/run_bot.py --interactive

# Проверка статуса
python3 scripts/run_bot.py

# Запуск тестов
python3 -m pytest tests/ -v
```

---

## 🎓 Рекомендуемый workflow

### День 1: Подготовка
```bash
# 1. Проверка работоспособности
python3 scripts/run_bot.py

# 2. Paper trading тест
python3 apps/run_flash_crash.py --coin ETH --paper --size 10
```

### День 2: Сбор данных
```bash
# Запустить запись на весь день
nohup python3 apps/record_data.py --coin BTC --duration 5 --output data/btc-5m-day1.jsonl &
nohup python3 apps/record_data.py --coin ETH --duration 5 --output data/eth-5m-day1.jsonl &
```

### День 3: Оптимизация
```bash
# Бэктест с оптимизацией
python3 apps/backtest.py data/btc-5m-day1.jsonl --sweep
python3 apps/backtest.py data/eth-5m-day1.jsonl --sweep

# Тестирование разных стратегий
python3 strategy/fair_value.py data/btc-5m-day1.jsonl --sweep
python3 strategy/book_imbalance.py data/btc-5m-day1.jsonl --sweep
```

### День 4: Реальная торговля
```bash
# Запуск с оптимизированными параметрами
python3 apps/run_flash_crash.py --coin BTC --size 5 --drop 0.28 --take-profit 0.09 --stop-loss 0.04
```

---

## 🏆 Best Practices

1. **Всегда начинайте с paper trading**
2. **Записывайте данные** для анализа
3. **Используйте sweep** для оптимизации параметров
4. **Начинайте с малых размеров** ($1-5)
5. **Мониторьте win rate** - должен быть >50%
6. **Используйте stop-loss** всегда
7. **Не торгуйте последние 30 секунд** рынка
8. **Диверсифицируйте** - разные монеты и стратегии

---

## 📦 Структура проекта (обновлённая)

```
polymarket-trading-bot/
├── apps/                          # Приложения для запуска
│   ├── run_flash_crash.py        # Flash Crash стратегия (live)
│   ├── run_fair_value.py         # Fair Value стратегия (live)
│   ├── backtest.py               # Бэктестер
│   ├── record_data.py            # Запись данных
│   └── orderbook_tui.py          # Визуализация orderbook
│
├── strategy/                      # Стратегии для бэктеста
│   ├── fair_value.py             # Black-Scholes pricing
│   ├── book_imbalance.py         # Дисбаланс ордербука
│   ├── convergence.py            # Конвергенция цен
│   ├── early_momentum.py         # Ранний импульс
│   ├── lead_lag.py               # Lead-Lag корреляция
│   ├── sum_arb.py                # Арбитраж суммы
│   └── common.py                 # Общие утилиты
│
├── strategies/                    # Live стратегии
│   ├── base.py                   # Базовый класс
│   ├── flash_crash.py            # Flash Crash (live)
│   └── fair_value_live.py        # Fair Value (live)
│
├── lib/                           # Библиотеки
│   ├── market_manager.py         # Управление рынками + WebSocket
│   ├── position_manager.py       # Управление позициями
│   ├── price_tracker.py          # Отслеживание цен
│   ├── binance_feed.py           # Binance WebSocket/REST
│   └── console.py                # Цвета для терминала
│
├── src/                           # Ядро бота
│   ├── bot.py                    # TradingBot (главный класс)
│   ├── client.py                 # CLOB + Relayer API
│   ├── signer.py                 # EIP-712 подписи
│   ├── config.py                 # Конфигурация
│   ├── crypto.py                 # Шифрование ключей
│   ├── gamma_client.py           # Gamma API (market discovery)
│   ├── websocket_client.py       # WebSocket клиент
│   └── utils.py                  # Утилиты
│
├── scripts/                       # Вспомогательные скрипты
│   ├── run_bot.py                # Запуск бота
│   ├── setup.py                  # Интерактивная настройка
│   └── full_test.py              # Интеграционные тесты
│
├── examples/                      # Примеры кода
│   ├── quickstart.py             # Начните отсюда!
│   ├── basic_trading.py          # Базовые операции
│   └── strategy_example.py       # Кастомные стратегии
│
├── tests/                         # Юнит-тесты (98 тестов)
├── data/                          # Записанные данные
├── .env                           # Ваши credentials (НЕ коммитить!)
└── requirements.txt               # Зависимости Python
```

---

## 🎯 Быстрые команды (шпаргалка)

```bash
# ═══════════════════════════════════════════════════════════════
# ЗАПУСК СТРАТЕГИЙ
# ═══════════════════════════════════════════════════════════════

# Flash Crash (основная)
python3 apps/run_flash_crash.py --coin ETH --size 10

# Fair Value (Black-Scholes)
python3 apps/run_fair_value.py --coin BTC --duration 5

# Paper trading
python3 apps/run_flash_crash.py --coin BTC --paper --size 20

# ═══════════════════════════════════════════════════════════════
# АНАЛИЗ И БЭКТЕСТИНГ
# ═══════════════════════════════════════════════════════════════

# Запись данных
python3 apps/record_data.py --coin BTC --duration 5 --output data/btc.jsonl

# Бэктест
python3 apps/backtest.py data/btc.jsonl --drop 0.30

# Оптимизация параметров
python3 apps/backtest.py data/btc.jsonl --sweep

# ═══════════════════════════════════════════════════════════════
# РУЧНОЕ УПРАВЛЕНИЕ
# ═══════════════════════════════════════════════════════════════

# Интерактивный режим
python3 scripts/run_bot.py --interactive

# Быстрая проверка
python3 scripts/run_bot.py

# ═══════════════════════════════════════════════════════════════
# ТЕСТИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════

# Все тесты
python3 -m pytest tests/ -v

# Конкретный модуль
python3 -m pytest tests/test_bot.py -v

# С покрытием
python3 -m pytest tests/ -v --cov=src
```

---

## 🌟 Новые возможности версии 2.0

### 1. Binance Integration
- Real-time BTC spot цены
- Исторические данные для бэктеста
- Автоматический кэш для ускорения

### 2. Advanced Strategies
- 6 новых стратегий для разных рыночных условий
- Backtest framework с оптимизацией
- Paper trading для безопасного тестирования

### 3. Improved Market Management
- Упрощённая логика переключения
- Настраиваемая задержка (5 секунд)
- Поддержка 5-минутных рынков

### 4. Better Position Sizing
- Balance-based sizing (% от баланса)
- Kelly criterion для Fair Value
- Автоматический расчёт оптимального размера

---

## 🎉 Итого

**Ветка:** `Polymarket-Bot-Working`

**Статус:**
- ✅ 98/98 тестов проходят
- ✅ Все критические баги исправлены
- ✅ Добавлены новые стратегии и инструменты
- ✅ Время переключения рынков = 5 секунд
- ✅ Готов к production использованию

**Готов к push в:** `https://github.com/andrewfa1991/polymarket-trading-bot.git`

---

*Последнее обновление: 15 марта 2026*
