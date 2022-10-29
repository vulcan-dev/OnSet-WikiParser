import json
import os
import re

categories = {
    "server": {},
    "server_events": {},
    "client": {},
    "client_events": {}
}

if __name__ == '__main__':
    if not os.path.exists("OnsetAPI"):
        os.system("mdbook init OnsetAPI --ignore none --title \"Onset API\"")

    if not os.path.exists("OnsetAPI"):
        print("Failed to create the book, please make sure mdbook is installed")
        exit(1)

    with open("api.json", "r") as f:
        data = json.load(f)
        
        # Setup categories & functions
        for key, value in categories.items():
            if key != "server_events" or key != "client_events":
                for k, v in data[key].items():
                    name = categories[key].get(v["category"], []) + [k]
                    categories[key][v["category"]] = name
            else:
                categories[key] = data[key]

        for key, value in categories.items():
            for k, v in value.items():
                k = k.replace(" ", "")

                if not os.path.exists(f"OnsetAPI/src/{key}/{k}"):
                    os.makedirs(f"OnsetAPI/src/{key}/{k}")
                    
                # Create the file in the category
                with open(f"OnsetAPI/src/{key}/{k}/index.md", "w", encoding="utf-8") as f:
                    for name in v:
                        value = data[key][name]

                        f.write(f"## {name}\n")
                        if value["description"]:
                            desc = value["description"]
                            desc = desc.replace("[", "").replace("]", "")
                            f.write(f"### Description<br><p><small>{desc}</small></p>\n")
                        
                        if value["params"]:
                            f.write("### Parameters\n")
                            f.write("| Name | Description |\n")
                            f.write("|------|-------------|\n")
                            for param in value["params"]:
                                desc = param["description"]
                                desc = re.sub(r"\[\[([a-zA-Z0-9]+)\]\]", r"[\1](#\1)", desc)

                                f.write(f"| {param['name']} | {desc} |\n")

                        try:
                            if value["syntax"]:
                                f.write("### Syntax\n")
                                f.write(f"```lua\n{value['syntax']}\n```\n")

                            ret_value = value["return"]
                            if ret_value:
                                ret_value = ret_value.replace("'", "")
                                f.write(f"### Return\n```\n{ret_value}\n```\n")
                        except:
                            pass

                        f.write("---\n")

        # Generate SUMMARY.md
        with open("OnsetAPI/src/SUMMARY.md", "w", encoding="utf-8") as f:
            f.write("# Summary\n\n")
            for key, value in categories.items():
                title = key.replace("_", " ").title()
                key = key.replace(" ", "")

                if key == "server_events" or key == "client_events":
                    f.write(f"* [{title}]({key}/Unknown/index.md)\n")
                else:
                    with open(f"OnsetAPI/src/{key}/index.md", "w", encoding="utf-8") as f2:
                        f2.write(f"# {title}\n\n")
                        for k, v in value.items():
                            k = k.replace(" ", "")
                            f2.write(f"* [{k}]({k}/index.md)\n")

                    f.write(f"* [{title}]({key}/index.md)\n")
                    for k, v in value.items():
                        k = k.replace(" ", "")
                        f.write(f"  * [{k}]({key}/{k}/index.md)\n")