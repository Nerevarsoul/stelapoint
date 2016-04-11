import helpers
from bs4 import BeautifulSoup
from urllib.parse import urljoin


_base_url = "https://www.pmddtc.state.gov/compliance/consent_agreements.html"
_site_url = "https://www.pmddtc.state.gov/compliance/"


def _get_scrape_urls():
    """find all scrapable links on main page"""

    url = _base_url

    doc = BeautifulSoup(helpers.fetch_string(url, cache_hours=6), "html.parser")
    div = doc.find("div", id="print_content")
    uls = div.find_all('ul')

    for ul in uls:
        href = ul.find_all("a")
        for link in href:
            link = link['href']
            link = urljoin(_site_url, link)
            yield link


def _generate_entities():
    """for each scrapable page, yield an entity"""

    for url in _get_scrape_urls():

        doc = BeautifulSoup(helpers.fetch_string(url, cache_hours=6), "html.parser")
        div = doc.find('div', id="print_content")
        u = div.find("u").get_text().strip()
        name = u.split(':')[-1]
        year = u.split(':')[0][-4:]

        p = div.find_all("p")[1]

        text = p.get_text().strip()

        fields = [
            {"tag": "url", "value": url},
            {"tag": "text", "value": text},
            {"tag": "year", "value": year}
        ]

        yield {
            "_meta": {
                "id": helpers.make_id(name),
                "entity_type": "company"
            },
            "fields": fields,
            "name": name
        }


def main():
    for entity in _generate_entities():
        helpers.emit(entity)


if __name__ == "__main__":
    main()

