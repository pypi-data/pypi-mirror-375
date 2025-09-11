from pydantic import BaseModel, Field


class ImageCLI(BaseModel):
    component: str = Field(description="Имя компоненты")
    cloud_component_name: str = Field(description="Имя клауд-компоненты")
    image_name: str = Field(description="Имя образа компонента")
    image_version: str = Field(description="Версия образа компонента")
    registry: str = Field(description="Используемый реджистри")

    class Config:
        populate_by_name = True
