from typing import NewType, Optional

from pydantic import BaseModel, Field

CloudComponentName = NewType("CloudComponentName", str)
SearchComponentName = NewType("SearchComponentName", str)


class DockerImage(BaseModel):
    name: str
    version: str
    registry: str
    login: Optional[str] = Field(default=None)


class ImageDocument(BaseModel):
    id: str = Field(alias="id", description="Имя образа")
    component: SearchComponentName = Field(description="Имя компонента, про которого образ")
    template: str = Field(description="Имя шаблона, про который образ")
    cloud: dict[CloudComponentName, DockerImage] = Field(
        default_factory=dict,
        description=(
            "Маппинг из имён клауд-компонентов клауд-сервиса этого КП в образа из докер-реджестри"
        ),
    )

    class Config:
        populate_by_name = True
