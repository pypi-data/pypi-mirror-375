<p align="center">
  <img src="https://raw.githubusercontent.com/LaFTonTechnology/mytonwallet_pay/main/assets/mtwpayLogo.png" width="300"/>
  <h1 align="center">mtwpay</h1>
  <p align="center">Асинхронный Python клиент для <a href="https://anywaylabs.notion.site/MyTonWallet-Pay-Docs-for-partners-18aba64b301480f98053e88b5c829e4a">MyTonWallet Pay API</a></p>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/LaFTonTechnology/mytonwallet_pay/main/assets/python-version.json" alt="Python"></a>
  <a href="https://pydantic.dev"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json" alt="Pydantic v2"></a>
  <a href="https://docs.aiohttp.org/en/stable/"><img src="https://img.shields.io/badge/aiohttp-v3-2c5bb4?logo=aiohttp" alt="Aiohttp"></a>
</p>

---

## 📌 О проекте

**mtwpay** — асинхронный Python клиент для работы с [MyTonWallet Pay API](https://anywaylabs.notion.site/MyTonWallet-Pay-Docs-for-partners-18aba64b301480f98053e88b5c829e4a).  
Позволяет создавать счета, получать ссылки на оплату и обрабатывать платежи полностью асинхронно.

---

### 📖 Документация
[![Docs](https://img.shields.io/badge/docs-online-brightgreen)](https://laftontechnology.github.io/mytonwallet_pay/)

---

## 💬 Сообщество

Присоединяйтесь к нашему чату в Telegram: [@mtwpay](https://t.me/mtwpay)

---

## Quick start

```python
import asyncio
from mytonwallet_pay import MTWPay
from datetime import datetime, timedelta


async def main():
    mtw_pay = MTWPay(token="YOUR_TOKEN", project_id=0)

    inv = await mtw_pay.create_invoice(amount=300000000, coin="TON", validUntil=datetime.now()+timedelta(minutes=5), description="My internal order info (id in your system, etc)")
    return inv.invoiceLink  # Ссылка для оплаты счёта


if __name__ == "__main__":
    print(asyncio.run(main()))
```


## 📦 Основные возможности

- ✅ Асинхронный клиент на `aiohttp`  
- ✅ Полная поддержка [MyTonWallet Pay API](https://anywaylabs.notion.site/MyTonWallet-Pay-Docs-for-partners-18aba64b301480f98053e88b5c829e4a)
- ✅ Быстрое создание счетов и получение ссылок для оплаты  
- ✅ Совместимость с Python 3.10+  

---

## 💖 Поддержка проекта

Вы можете поддержать разработчиков донатом:

| Сеть     | Адрес                                                                 |
|----------|-----------------------------------------------------------------------|
| **TON**  | `UQCekZTSqysK4OUQFovzI31CILQj0GGjnYxBV77HlK2Zv1BM`                    |

---

## 📝 Лицензия

Проект распространяется под лицензией MIT.

---

## 📌 Контакты и обратная связь

- Telegram: [@mtwpay](https://t.me/mtwpay)  
- GitHub Issues: открывайте любые баги или предложения прямо в репозитории.
