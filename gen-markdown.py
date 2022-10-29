import json
import os

markdown = {
    "server": None,
    "server_events": None,
    "client": None,
    "client_events": None
}

last_category = None
def convert(data: dict) -> str:
    global last_category
    markdown_str = ""

    for key, value in data.items():
        if key in markdown:
            continue

        if isinstance(value, str):
            value = value.replace("'''", "`")

        category = value["category"]
        if category != last_category:
            markdown_str += f"# Category: {category}\n"
            last_category = category

        name = key
        description = value["description"]

        markdown_str += f"## {name}\n"

        if "syntax" in value:
            markdown_str += f"### Syntax\n```\n{value['syntax']}\n```\n"

        if "params" in value and len(value["params"]) > 0:
            markdown_str += f"| Name | Description |\n| ---- | ----------- |\n"
            for param in value["params"]:
                markdown_str += f"| {param['name']} | {param['description']} |\n"

        if "return" in value:
            return_str = value["return"].replace("'''", "`")
            markdown_str += f"### \n{return_str}\n"

        if "description" in value:
            description = description.replace("'''", "`")
            markdown_str += f"{description}\n"

        markdown_str += "\n"

    return markdown_str

if __name__ == '__main__':
    with open("api.json", "r") as f:
        data = json.load(f)
        markdown["server"] = convert(data["server"])
        markdown["server_events"] = convert(data["server_events"])
        markdown["client"] = convert(data["client"])
        markdown["client_events"] = convert(data["client_events"])

    if not os.path.exists("API_MD"):
        os.mkdir("API_MD")

    for key, value in markdown.items():
        name = key.title().replace("_", "")
        with open(f"API_MD/{name}.md", "w", encoding="utf-8") as f:
            f.write(value)

    api_file_str = """# API Documentation
## [Server](./Server.md)
## [Server Events](./ServerEvents.md)
## [Client](./Client.md)
## [Client Events](./ClientEvents.md)
"""

    with open("API_MD/API.md", "w", encoding="utf-8") as f:
        f.write(api_file_str)