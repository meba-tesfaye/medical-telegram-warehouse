with alerts as (
    select * from {{ ref('stg_telegram_messages') }}
)

select
    channel_name,
    count(alert_key) as total_messages_posted,      -- <-- Fixed column name here
    count(extracted_price_etb) as total_ads_with_prices,
    avg(extracted_price_etb) as average_product_price_etb
from alerts
group by channel_name