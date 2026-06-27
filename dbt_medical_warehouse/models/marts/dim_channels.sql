with unique_channels as (
    select distinct
        channel_name
    from {{ ref('stg_telegram_messages') }}  -- <-- Updated here
)

select
    md5(channel_name) as channel_key,
    channel_name,
    case 
        when channel_name = 'CheMed123' then 'Medical Products & Pharma'
        when channel_name = 'lobelia4cosmetics' then 'Cosmetics & Clinical Skincare'
        when channel_name = 'TikvahPharma' then 'Clinical Pharmacy & Inquiries'
        else 'General Medical Channel'
    end as channel_category
from unique_channels