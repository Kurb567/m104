import yookassa
import config as x
yookassa.Configuration.configure(x.SHOP_ID, x.SECRET_KEY)
while True:
    payment_id = input()
    payment = yookassa.Payment.find_one(payment_id)
    print(payment.status)
