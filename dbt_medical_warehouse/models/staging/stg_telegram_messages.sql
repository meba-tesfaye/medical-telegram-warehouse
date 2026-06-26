{{ config(materialized='view') }}

with raw_source as (
    select * from main.telegram_messages
)

select
    cast(message_id as integer) as message_id,
    trim(channel) as channel_name,
    cast(date as date) as message_date,
    cleaned_text,
    cast(extracted_price_etb as real) as price_etb,
    cast(has_media as boolean) as has_media,
    image_path,
    cast(views as integer) as view_count,
    cast(forwards as integer) as forward_count
from raw_source