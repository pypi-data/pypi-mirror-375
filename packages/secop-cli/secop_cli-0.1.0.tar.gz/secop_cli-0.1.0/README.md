# secop-cli

[![PyPI](https://img.shields.io/pypi/v/secop-cli?color=blue&label=PyPI)](https://pypi.org/project/secop-cli/)
[![TestPyPI](https://img.shields.io/badge/TestPyPI-latest-orange)](https://test.pypi.org/project/secop-cli/)
![Python](https://img.shields.io/badge/python-3.11%2B-brightgreen)

CLI для работы с хранилищем Docker-образов компонентов **Secop**.  
Позволяет просматривать образы, фильтровать их по компонентам и добавлять новые из YAML/JSON-манифестов.

---

## Установка

Из [PyPI](https://pypi.org/project/secop-cli/):

```bash
pip install secop-cli
```

## Использование

```shell
secop-cli --help
```

### Список образов

Получить все образы
```shell
secop-cli images list
```

Отфильтровать по компоненту

```shell
secop-cli images list --component <component-name>
```

### Добавить образ
```shell
secop-cli images insert --file image.yaml
```

где `image.yaml` имеет следующую структуру:
```yaml
id: some_id_str
component: some_component_str
template: some_template_str
cloud:
  big_indexer:
    name: image_name
    version: image_name
    registry: registry
    login: token
```
