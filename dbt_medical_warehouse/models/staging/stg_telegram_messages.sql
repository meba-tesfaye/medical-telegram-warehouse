with source as (
    select * from {{ source('main', 'staging_telegram_alerts') }}
)

select
    message_id as alert_key,
    channel_name,
    message_text,
    cleaned_text,
    extracted_price_etb,
    scraped_at as alert_timestamp
from source