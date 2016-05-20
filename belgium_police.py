from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import helpers

_base_url = "http://www.politie.be/fed/nl/opsporingen/gezocht/gekende-verdachten?offset="
_site_url = "http://www.politie.be/"
_entity_base_url = "http://www.politie.be/fed/nl/opsporingen/gezocht/"


def get_name(name):
    if ":" in name:
        name = name.split(":")[1]
    return ' '.join([n.capitalize() for n in name.split()]) 

def get_date(mydate):
    mydate = mydate.split()[0].strip()
    mydate = datetime.strptime(mydate, '%d.%m.%Y')
    return mydate.strftime("%Y-%m-%d")


def _get_scrape_urls():
    """find all scrapable links on main page"""
    for i in (0, 10, 20):
        url = _base_url + str(i)
        yield url


def _generate_entities():
    """for each scrapable page, yield an entity"""
    for url in _get_scrape_urls():
        doc = BeautifulSoup(helpers.fetch_string(url), "html.parser")
        lis = doc.find_all("li", class_="card card--horizontal")
        for li in lis:
             name = get_name(li.find("span", class_="card__name").get_text())
             
             try: 
                 mydate = get_date(li.find("span", class_="card__date").get_text())
             except AttributeError:
                 mydate = '' 
             
             try:  
                 place = li.find("span", class_="card__place").get_text()
             except AttributeError:
                 place = ""

             picture_url = urljoin(_site_url, li.find("img")["src"])

             fields = [
                  {"name": "Date", "value": mydate},
                  {"name": "Place", "value": place},
                  {"tag": "picture_url", "value": picture_url},
             ]

             try:
                 entity_url = urljoin(_entity_base_url, li.find("a", class_="card__box")["href"])
                 doc2 = BeautifulSoup(helpers.fetch_string(entity_url), "html.parser")
                 div = doc2.find("div", class_="article__text")
                 ps = div.find_all("p")       
                 header = ps[0].get_text().strip()
                 text = ' '.join([p.get_text().strip() for p in ps[1:]])
                 fields.append({"name": header, "value": text}) 
             except TypeError:
                 entity_url = ''

             fields.append({"tag": "url", "value": entity_url}) 

             yield {
                 "_meta": {
                     "id": helpers.make_id(name),
                     "entity_type": "person"
                 },
                 "fields": fields,
                 "name": name
             } 


def main():
    for entity in _generate_entities():
        helpers.check(entity)


if __name__ == "__main__":
    main()


