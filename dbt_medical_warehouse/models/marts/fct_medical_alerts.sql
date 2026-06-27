with alerts as (
    select * from {{ ref('stg_telegram_messages') }}  -- <-- Updated here
)

select
    alert_key,
    md5(channel_name) as channel_key, 
    alert_timestamp,
    cleaned_text as alert_message_payload,
    extracted_price_etb as item_price_etb,
    length(cleaned_text) as message_character_length,
    case 
        when extracted_price_etb is null then false 
        else true 
    end as is_commercial_ad
from alerts