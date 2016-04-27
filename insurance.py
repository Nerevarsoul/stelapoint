from datetime import datetime

from bs4 import BeautifulSoup

import helpers


_base_url = "https://insurance.az.gov/administrative-orders?page="


def _get_scrape_urls():
    """find all scrapable links on main page"""

    i = 0
    while i < 74:
        yield _base_url + str(i)
        i += 1


def _generate_entities():
    """for each scrapable page, yield an entity"""

    for url in _get_scrape_urls():

        doc = BeautifulSoup(helpers.fetch_string(url), "html.parser")
        table = doc.find('table', class_='views-table').find('tbody')
        trs = table.find_all('tr')
        for tr in trs:
            td = tr.find_all('td')
            href = td[0].find_all('a')[1]['href']
            name = td[1].get_text().strip()
            matter_type = td[2].get_text().strip()
            date_failed = td[3].get_text().strip()

            fields = [{"name": "Matter Type", "value": matter_type},
                      {"name": "Docket Number", "value": href},
                      {"name": "Date Failed", "value": date_failed}]

            my_id = helpers.make_id(name)
            if len(my_id) > 99:
                my_id = my_id[:99]

            yield {
                "_meta": {
                    "id": my_id,
                    "entity_type": "company"
                },
                "fields": fields,
                "name": name,
            }


def main():
    for entity in _generate_entities():
        helpers.check(entity)


if __name__ == "__main__":
    main()
