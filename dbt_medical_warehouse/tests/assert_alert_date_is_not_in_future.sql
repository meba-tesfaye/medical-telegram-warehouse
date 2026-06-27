-- Custom test: Ensure that extracted product prices are never negative values
select
    alert_key,
    item_price_etb
from {{ ref('fct_medical_alerts') }}
where item_price_etb < 0