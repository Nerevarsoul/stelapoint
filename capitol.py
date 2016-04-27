from datetime import datetime

from bs4 import BeautifulSoup

import helpers


_base_url = "http://capital.sec.or.th/webapp/enforce/recent_enforce_query_eng.php"


def _generate_entities():
    """for each scrapable page, yield an entity"""

    doc = BeautifulSoup(helpers.fetch_string(_base_url), "html.parser")
    form = doc.find('form', {'name': 'criminalqueryeng_p2'})
    tables = form.find('table', {'bgcolor': '#84BD00'})

    for table in tables:
        tr = table.find_all('tr')
        i = 1
        while i < len(tr):
            td = tr[i].find_all('td')
            name = td[2].get_text().strip()
            date = td[1].get_text().strip()
            url = td[6].find('a')['href']
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
