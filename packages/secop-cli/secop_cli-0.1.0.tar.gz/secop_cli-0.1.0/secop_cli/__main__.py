import json
from typing import Optional

import typer
import yaml

from secop_cli.api import SecopApiClient
from secop_cli.models.mongo_models import ImageDocument
from secop_cli.transform import flatten_docs

app = typer.Typer(
    help=(
        "secop-cli – CLI для работы с хранилищем Docker-образов компонентов Secop.\n\n"
        "Основные команды:\n"
        "  images  – операции с Docker-образами (просмотр, добавление и др.)\n\n"
        "Флаг --api-url:\n"
        "  Можно передать URL сервисного API (по умолчанию https://secop.g.vmailru.net/api/v0).\n\n"
        "Примеры:\n"
        "  secop-cli images list\n"
        "  secop-cli images list --component big_indexer\n"
        "  secop-cli images insert --file manifest.yaml\n"
    ),
    rich_markup_mode=None,
)

images_app = typer.Typer(
    help=(
        "Операции с образами:\n"
        "  list    – показать все образы (или только для выбранного компонента)\n"
        "  insert  – добавить новый образ из yaml/json манифеста\n"
    ),
    rich_markup_mode=None,
)
app.add_typer(images_app, name="images")


@images_app.command("list")
def images(
    component: Optional[str] = typer.Option(
        None, "--component", "-c", help='Фильтр по компоненту (например, "big_indexer")'
    ),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="Базовый URL внешнего API (по умолчанию $SECOP_API_URL)."
    ),
):
    """
    secop-cli images --api-url <api-url>
    secop-cli images --component <component-name> --api-url <api-url>
    """
    client = SecopApiClient(base_url=api_url)
    docs = client.get_images_by_component(component) if component else client.get_all_images()
    rows = flatten_docs(docs)
    payload = [r.model_dump() for r in rows]
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@images_app.command("insert")
def images_insert(
    file: Optional[str] = typer.Option(None, "--file", "-f", help="JSON/YAML-манифест образа"),
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="Базовый URL внешнего API (по умолчанию $SECOP_API_URL)."
    ),
):
    """
    secop-cli images insert --file <file>

    где <file> – это .yaml файл, в котором лежит ImageDocument (mongo_models.ImageDocument)
    """
    if file is None:
        raise ValueError("--file option is required to insert images!")
    with open(file, "r", encoding="utf-8") as fh:
        text = fh.read()
        data = (
            yaml.safe_load(text)
            if (file.endswith(".yml") or file.endswith(".yaml"))
            else json.loads(text)
        )

    model = ImageDocument.model_validate(data)
    payload = model.model_dump(by_alias=True)

    client = SecopApiClient(base_url=api_url)
    res = client.insert_image(payload)

    typer.echo(json.dumps({"request": payload, "response": res}, ensure_ascii=False, indent=2))


def cli():
    app()
