{{ config(materialized='table') }}

with staging_data as (
    select * from {{ ref('stg_telegram_messages') }}
)

select
    channel_name,
    count(message_id) as total_messages_posted,
    sum(view_count) as total_accumulated_views,
    sum(forward_count) as total_accumulated_forwards,
    avg(price_etb) as average_product_price_etb,
    sum(forward_count) * 100.0 / nullif(sum(view_count), 0) as engagement_rate_percentage
from staging_data
group by channel_name