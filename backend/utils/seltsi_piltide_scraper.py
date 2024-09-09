import requests
from dotenv import dotenv_values
import os

from requests.auth import HTTPBasicAuth

config: dict = {
    **dotenv_values("backend/.env"),  # load shared development variables
    # **dotenv_values(".env.secret"),  # load sensitive variables
    # **os.environ,  # override loaded values with environment variables
}

live_scrape = True
sess = requests.Session()

if live_scrape:

    ua = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "Referer": "https://uus.eys.ee/?q=node&destination=node",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    # ns et cookied läheksid õigeks äkki?
    res = sess.get("https://uus.eys.ee/?q=node&destination=node", headers=ua)

    # selleks et sisse logida
    res = sess.post(
        "https://uus.eys.ee/?q=node&destination=node",
        headers=headers,
        data=f"name={config['EYS_NIMI']}&pass={config['EYS_PAROOL']}&form_id=user_login_block&op=Logi+sisse",
    )

    # edasi saab sessiooni alt kätte saada
    nimekiri = sess.get("https://uus.eys.ee/?q=nimekiri")
    # print(nimekiri.content)


from bs4 import BeautifulSoup
import bs4

if live_scrape:
    soup = BeautifulSoup(nimekiri.content, "lxml")
    with open("backend/temp/nimekiri.html", "wb+") as f:
        f.write(nimekiri.content)
else:
    with open("backend/temp/nimekiri.html", "r") as f:
        soup = BeautifulSoup(f, "lxml")

parsimise_todo = []
tabel: bs4.element.Tag | bs4.NavigableString | None = soup.find("tbody")

for asi in tabel.find_all("a", href=True):  # type: ignore
    # print(asi)
    # print(asi["href"])
    # print(asi.contents[0])
    parsimise_todo.append((asi["href"], asi.contents[0]))
    # print("----")

print(len(parsimise_todo))


temp = "1149"
if live_scrape:
    profiil = sess.get(f"https://uus.eys.ee/?q=pildid/lisa/{temp}/nimekiri")

    soup = BeautifulSoup(profiil.content, "lxml")
    with open("backend/temp/profiil.html", "wb+") as f:
        f.write(profiil.content)

else:
    with open("backend/temp/profiil.html", "r") as f:
        soup = BeautifulSoup(f, "lxml")

persons_images = []
for image_source in soup.find_all("img"):
    print(image_source["src"])
    persons_images.append(image_source["src"])

# BUG piltide salvestamine
for idx, img_url in enumerate(persons_images):
    img_data = sess.get(img_url, allow_redirects=True).content

    with open(f"backend/temp/{idx}.jpg", "wb") as handler:
        handler.write(img_data)
