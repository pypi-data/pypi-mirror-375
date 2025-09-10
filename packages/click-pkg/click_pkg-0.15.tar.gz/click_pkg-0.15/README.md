<h1 align="center">Click Software Development Kit for Django and FastAPI</h1>
<p align="center">
  <a href="https://t.me/+lO97J78xBj45MzBi">
    <img src="https://img.shields.io/badge/Support%20Group-blue?logo=telegram&logoColor=white" alt="Support Group on Telegram"/>
  </a>
</p>

<p align="center">
  <a href="https://docs.pay-tech.uz"><img src="https://img.shields.io/static/v1?message=Documentation&logo=gitbook&logoColor=ffffff&label=%20&labelColor=5c5c5c&color=3F89A1"></a>
  <a href="https://github.com/PayTechUz/click-pkg"><img src="https://img.shields.io/badge/Open_Source-❤️-FDA599?"/></a>
  <a href="https://github.com/PayTechUz/click-pkg/issues">
    <img src="https://img.shields.io/github/issues/PayTechUz/click-pkg" />
  </a>
  <a href="https://pepy.tech/project/click-pkg">
    <img src="https://static.pepy.tech/badge/click-pkg" alt="PyPI - Downloads" />
  </a>
</p>
<p align="center">Welcome to payme-pkg, the open source payme SDK for Python.</p>

<p align="center">You can use it for test and production mode. Join our community and ask everything you need.</p>

<a href="https://docs.pay-tech.uz">
  <p align="center">Visit the full documentation for Click Shop API</p>
</a>

<p align="center">
  <a href="https://youtu.be/beIJGe2ftcw?si=VjQETGnzdyiOafgx" target="_blank">
    <img src="https://img.shields.io/badge/Watch%20Demo-red?logo=youtube&logoColor=white&style=for-the-badge" 
         alt="Watch the YouTube Demo" 
         style="width: 150px; height: 30px; border-radius: 7px;" />
  </a>
</p>


## Installation

```shell
pip install click-pkg
```

## Installation to Django

Add `'click_up'` in to your settings.py

```python
INSTALLED_APPS = [
    ...
    'click_up',
    ...
]
```

Add `'click_up'` credentials inside to settings.py

Click configuration settings.py
```python
CLICK_SERVICE_ID = "your-service-id"
CLICK_MERCHANT_ID = "your-merchant-id"
CLICK_SECRET_KEY = "your-secret-key"
CLICK_ACCOUNT_MODEL = "order.models.Order" # your order model path.
CLICK_AMOUNT_FIELD = "amount" # your amount field that's belongs to your order model

CLICK_COMMISSION_PERCENT = "(optional int field) your companies comission percent if applicable"
CLICK_DISABLE_ADMIN = False # (optionally configuration if you want to disable change to True)
```

Create a new View that about handling call backs
```python
from click_up.views import ClickWebhook


class ClickWebhookAPIView(ClickWebhook):
    def successfully_payment(self, params):
        """
        successfully payment method process you can ovveride it
        """
        print(f"payment successful params: {params}")

    def cancelled_payment(self, params):
        """
        cancelled payment method process you can ovveride it
        """
        print(f"payment cancelled params: {params}")
```

Add a `click webhook` path to core of urlpatterns:

```python
from django.urls import path
from django.urls import include

from your_app.views import ClickWebhookAPIView


urlpatterns = [
    ...
    path("payment/click/update/", ClickWebhookAPIView.as_view()),
    ...
]
```

Run migrations
```shell
python3 manage.py makemigrations && python manage.py migrate
```

🎉 Congratulations you have been integrated click with django, keep reading docs. After successfull migrations check your admin panel and see results what happened.


## Generate Pay Link
Example to generate link:

- Input

```python
from click_up import ClickUp


click_up = ClickUp(service_id="your-service-id", merchant_id="your-merchant-id") # alternatively you can use settings variables as well here.


# Generate Paylik payment link
paylink = click_up.initializer.generate_pay_link(
  id=1, # id maybe order_id or acount_id (user_id, chat_id and etc..)
  amount=100,
  return_url="https://example.com"
)
```

- Output
```
https://my.click.uz/services/pay?service_id=service_id&merchant_id=merchant_id&amount=1000&transaction_param=1&return_url=https://example.com
```


## Installation and example usage for FastAPI
```python
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import declarative_base

from fastapi import FastAPI, Depends, Request, Body

from clickup_fastapi.core.client import ClickUp
from clickup_fastapi.utils.const import Action
from clickup_fastapi.api.webhook import process_webhook, Account
from clickup_fastapi.dependencies import click_database_manager, ClickSettings

app = FastAPI()
Base = declarative_base()

settings = ClickSettings(
    service_id="your-service-id",
    merchant_id="your-merchant-id",
    secret_key="your-secret-key",
)

DB_SESSION_LOCAL = click_database_manager(
    db_url="sqlite:///database.db" # you can use another database engines
)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)


# creating tables
Base.metadata.create_all(bind=DB_SESSION_LOCAL().get_bind())


def get_db():
    db = DB_SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()


def fetch_account(merchant_trans_id: str, db: Session) -> Account:
    order = db.query(Order).filter_by(id=merchant_trans_id).first()
    account = Account(
        id=order.id,
        amount=order.amount
    )

    return account


@app.post("/v1/webhook/click")
async def webhook_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    settings: ClickSettings = Depends(lambda: settings)
):
    params = await request.form()
    merchant_trans_id = params.get("merchant_trans_id")
    account = fetch_account(merchant_trans_id, db)

    response = await process_webhook(params, db, settings, account)

    if "merchant_prepare_id" in response:
        order = db.query(Order).filter_by(id=merchant_trans_id).first()

        # checking for successfull transaction and change our order account
        if response["error"] >= 0 and params.get("action") == Action.COMPLETE:
            order.status = "success"

        elif response["error"] != 0:  # Transaction cancelled
            order.status = "cancelled"

        db.commit()

    return response


@app.post("/v1/order/create")
async def create_order(
    amount: float = Body(embed=True),
    db: Session = Depends(get_db),
):
    order = Order(amount=amount, status="pending")

    db.add(order)
    db.commit()
    db.refresh(order)

    click_up = ClickUp(
        service_id=settings.service_id,
        merchant_id=settings.merchant_id,
        secret_key=settings.secret_key,
    )

    # generate payment link
    payment_link = await click_up.initializer.generate_pay_link(
        id=order.id,
        amount=order.amount,
        return_url="https://example.uz"
    )

    return {
        "order_id": order.id,
        "payment_link": payment_link
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
