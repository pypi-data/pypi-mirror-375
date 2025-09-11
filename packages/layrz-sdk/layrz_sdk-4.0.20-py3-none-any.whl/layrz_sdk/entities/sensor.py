"""Sensor entity"""

from pydantic import BaseModel, Field

from .sensor_mask import SensorMask


class Sensor(BaseModel):
  """Sensor entity"""

  pk: int = Field(description='Defines the primary key of the sensor', alias='id')
  name: str = Field(description='Defines the name of the sensor')
  slug: str = Field(description='Defines the slug of the sensor')
  formula: str = Field(
    default='',
    description='Defines the formula of the sensor, used for calculations',
  )
  mask: list[SensorMask] | None = Field(
    default=None,
    description='Defines the mask of the sensor, used for filtering data',
  )

  measuring_unit: str | None = Field(
    default=None,
    description='Defines the measuring unit of the sensor, e.g., km/h, °C',
  )
