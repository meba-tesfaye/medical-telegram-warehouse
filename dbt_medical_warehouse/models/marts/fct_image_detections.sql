{{ config(
    materialized='table'
) }}

with raw_detections as (
    select
        message_id,
        channel_name,
        image_path,
        detected_objects,
        confidence_score,
        image_category
    from {{ source('raw', 'image_detections') }}
),

stg_messages as (
    select
        alert_key,          -- This is your message_id renamed!
        channel_name,
        md5(channel_name) as channel_key
    from {{ ref('stg_telegram_messages') }}
)

select
    md5(cast(rd.message_id as varchar) || '-' || rd.channel_name) as image_detection_key,
    rd.message_id,
    sm.channel_key,
    rd.image_path,
    rd.detected_objects,
    rd.confidence_score,
    rd.image_category
from raw_detections rd
left join stg_messages sm 
    on rd.message_id = sm.alert_key -- Clean join on the true keys!
    and rd.channel_name = sm.channel_name