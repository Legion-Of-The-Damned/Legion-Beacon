import requests

def send_webhook_payload(url, username, avatar_url, content, role_ids, embeds):
    data = {
        "username": username,
        "avatar_url": avatar_url,
        "content": content,
        "embeds": []
    }

    for e in embeds:
        embed_dict = {}
        if e.get("title"):
            embed_dict["title"] = e["title"]
        if e.get("description"):
            embed_dict["description"] = e["description"]
        if e.get("color"):
            try:
                embed_dict["color"] = int(e["color"].replace("#", ""), 16)
            except:
                pass
        if e.get("image"):
            embed_dict["image"] = {"url": e["image"]}
        if embed_dict:
            data["embeds"].append(embed_dict)

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
    except Exception as ex:
        print(f"Ошибка при отправке вебхука: {ex}")
