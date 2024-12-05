from bs4 import BeautifulSoup
import requests
import json
import time

joan_miro_url = "https://www.fmirobcn.org/en/colection/catalog-works/joan-miro/paintings/page/"
data = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}

def change_data_structure(data):
    formated_data = []
    for d in data:
        picture_data = {}
        picture_data["name_of_artist"] = d.get("author", None)
        picture_data["title"] = d.get("title", None)
        picture_data["date or period of creation"] = d.get("date", None)
        picture_data["dimensions"] = d.get("sizes", None)
        picture_data["technique"] = d.get("medium", None)
        picture_data["signature"] = d.get("signature", None)
        picture_data["provenance"] = d.get("provenance", None)
        picture_data["bibliography"] = d.get("bibliography", None)
        picture_data["exhibition"] = d.get("exhibitions", None)
        picture_data["literature"] = d.get("inscriptions", None)
        picture_data["image_url"] = d.get("image_url", None)
        formated_data.append(picture_data)
    return formated_data


for page in range(1, 17):
    time.sleep(1)
    response = requests.get(f"{joan_miro_url}{page}", headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")


    paintings_ul = soup.find(name="ul", class_="llistat-obres small-block-grid-2 medium-block-grid-3 large-block-grid-4")
    all_paintings = paintings_ul.find_all(name="a", href=True)
    hrefs = [a["href"] for a in all_paintings]

    for href in hrefs:

        curr_picture_data = {}
        time.sleep(0.5)
        response = requests.get(f"https://www.fmirobcn.org{href}", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        description_list = soup.find(name="dl", class_="obra-dades-list")
        try:
            for dt, dd in zip(description_list.find_all(name="dt"), description_list.find_all(name="dd")):
                key = dt.text.strip().lower()
                p = dd.find(name="p")
                ul = dd.find(name="ul")
                if p:
                    value = p.get_text()
                elif ul:
                    value = [li.get_text().strip("\t") for li in ul.find_all(name="li")]
                else:
                    value = dd.get_text()
                curr_picture_data[key] = value
        except AttributeError:
            pass

        img_div = soup.find(name="div", class_="obra-pict")
        if img_div:
            img_src = img_div.find(name="img")["src"]
            curr_picture_data["image_url"] = f"https://www.fmirobcn.org{img_src}"
        else:
            curr_picture_data["image_url"] = "None"
        data.append(curr_picture_data)

for d in data:
    print(d)

data = change_data_structure(data)

with open('miro.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


