"""Sensor entity"""

from pydantic import BaseModel, Field


class SensorMask(BaseModel):
  """Sensor entity"""

  icon: str | None = Field(description='Defines the icon of the sensor')
  text: str | None = Field(description='Defines the text of the sensor')
  color: str | None = Field(
    description='Defines the color of the sensor, used for visual representation',
  )
  value: str | float | int | None = Field(
    default=None,
    description='Defines the value of the sensor, can be of various types',
  )
