from bs4 import BeautifulSoup
import requests
import json
from requests import RequestException

joan_miro_url = "https://www.fmirobcn.org/en/colection/catalog-works/joan-miro/paintings/page/"
data = []
id = 1

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}

def change_data_structure(data):
    formated_data = []
    for d in data:
        picture_data = {
            "id": d.get("id", None),
            "name_of_artist": d.get("author", None),
            "title": d.get("title", None),
            "date": d.get("date", None),
            "dimensions": d.get("sizes", None),
            "technique": d.get("medium", None),
            "signature": d.get("signature", None),
            "provenance": d.get("provenance", None),
            "bibliography": d.get("bibliography", None),
            "exhibition": d.get("exhibitions", None),
            "literature": d.get("inscriptions", None),
            "image_url": d.get("image_url", None)
        }
        formated_data.append(picture_data)
    return formated_data


def fetch_html(url, headers):
    error = True
    while error:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
        except RequestException:
            pass
        else:
            error = False
    return soup

for page in range(1, 17):
    print(f"I'm on page {page}", flush=True)
    soup = fetch_html(f"{joan_miro_url}{page}", headers)


    paintings_ul = soup.find(name="ul", class_="llistat-obres small-block-grid-2 medium-block-grid-3 large-block-grid-4")
    all_paintings = paintings_ul.find_all(name="a", href=True)
    hrefs = [a["href"] for a in all_paintings]

    for href in hrefs:

        curr_picture_data = {}

        soup = fetch_html(f"https://www.fmirobcn.org{href}", headers=headers)

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

            image_response = requests.get(curr_picture_data['image_url'])
            if image_response.status_code == 200:
                with open(f"images/{id}.jpg", 'wb') as img_file:
                    img_file.write(image_response.content)
        else:
            curr_picture_data["image_url"] = "None"
        data.append(curr_picture_data)

        curr_picture_data["id"] = id
        data = change_data_structure(data)
        id += 1
        with open('miro.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


