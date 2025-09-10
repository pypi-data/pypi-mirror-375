from dataclasses import dataclass
from typing import Optional
from starburst_data_products_client.shared.models import JsonDataClass


@dataclass
class MaterializedViewProperties(JsonDataClass):
    refresh_interval: Optional[str]
    refresh_schedule: Optional[str]
    refresh_schedule_timezone: Optional[str]
    storage_schema: Optional[str]
    incremental_column: Optional[str]
