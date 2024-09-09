from ast import Tuple
import requests
from dotenv import dotenv_values
import os
from bs4 import BeautifulSoup
import bs4
from requests.auth import HTTPBasicAuth

from time import sleep

config: dict = {
    **dotenv_values("backend/.env"),  # load shared development variables
    # **dotenv_values(".env.secret"),  # load sensitive variables
    # **os.environ,  # override loaded values with environment variables
}

def make_session():
    sess = requests.Session()
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
    sess.get("https://uus.eys.ee/?q=node&destination=node", headers=ua)

    # selleks et sisse logida
    sess.post(
        "https://uus.eys.ee/?q=node&destination=node",
        headers=headers,
        data=f"name={config['EYS_NIMI']}&pass={config['EYS_PAROOL']}&form_id=user_login_block&op=Logi+sisse",
    )

    return sess

def get_liikmete_nimekiri(sess:requests.Session)->list[Tuple]:
    """Parsib siseveebi leheküljelt kõik siseveebis olevate liikmete pildid.
    Isiku url on kujul"/?q=nimekiri/isik/1".
    Isiku nimi on Perenimi, Eesnimi

    :param requests.Session sess: sisselogitud sessioon
    :return list[Tuple]: list, kus on [(isiku url, isiku nimi), ...]
    """    
    nimekiri = sess.get("https://uus.eys.ee/?q=nimekiri")
    soup_nimekiri = BeautifulSoup(nimekiri.content, "lxml")
    

    liikmed = []
    tabel: bs4.element.Tag | bs4.NavigableString | None = soup_nimekiri.find("tbody")

    for trow in tabel.find_all("a", href=True):  # type: ignore
        # print(asi["href"])
        # print(asi.contents[0])
        liikmed.append((trow["href"], trow.contents[0]))

    # print(len(liikmed))

    return liikmed

def get_liikme_pildid(sess:requests.Session, url:str)->list:
    
    profiil_id = url.split("/")[-1]

    profiil = sess.get(f"https://uus.eys.ee/?q=pildid/lisa/{profiil_id}/nimekiri")

    soup_profiil = BeautifulSoup(profiil.content, "lxml")
 

    persons_images = []
    for image_source in soup_profiil.find_all("img"):
        # print(image_source["src"])
        persons_images.append(image_source["src"])
    return persons_images

def download_liikme_pildid(sess:requests.Session, urlid, nimi)->None:
    os.mkdir(f"./backend/data/siseveeb/{nimi}")


    for idx, img_url in enumerate(urlid):
        img_data = sess.get(img_url, allow_redirects=True).content
            
        with open(f"backend/data/siseveeb/{nimi}/{idx}.jpg", "wb") as handler:
            handler.write(img_data)
        sleep(1)


if __name__ == "__main__":
    if not os.path.exists("backend/data/siseveeb"):
        os.makedirs("backend/data/siseveeb")

    sess = make_session()

    liikmete_nimekiri = get_liikmete_nimekiri(sess)

    for liige in liikmete_nimekiri:
        (liikme_url, liikme_nimi) = liige # type:ignore
        print(liikme_nimi)
        print("\t", liikme_url)

        pildi_urlid = get_liikme_pildid(sess, liikme_url)
        print("\t", pildi_urlid)
        
        if len(pildi_urlid) == 0:
            continue

        download_liikme_pildid(sess, pildi_urlid, liikme_nimi)

        sleep(3)