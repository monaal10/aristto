import stripe

from main.user.models import User
from main.utils.model_token_cost import model_tokens_to_dollars


def convert_model_tokens_to_dollars(input_tokens, output_tokens, model="gpt-4o-mini"):
    model_price = model_tokens_to_dollars.get(model)
    model_input_price = round((model_price.get(input_tokens)*input_tokens)/1000000, 2)
    model_output_price = round((model_price.get(output_tokens)*output_tokens)/1000000, 2)
    total_price = model_input_price + model_output_price
    return total_price

def convert_dollars_to_aristto_credits(price):
    return round((price*3)/100, 3)

def meter_usage(credits_used):
    user = User().get()
    stripe.billing.MeterEvent.create(
      event_name="aristto_credits",
      payload={"value": credits_used, "stripe_customer_id": user["stripe_customer_id"]},
    )

def price_api_call(cost):
    credits_used = convert_dollars_to_aristto_credits(cost)
    meter_usage(credits_used)