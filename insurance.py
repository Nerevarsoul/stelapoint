import re

from bs4 import BeautifulSoup

import helpers


_base_url = "https://insurance.az.gov/administrative-orders?page="
dividers = (",LLC", ",INC.", ",L.P.", ",LTD.")
company = ("Lls", ",Inc", ",L.P.", ",Ltd", "Limited")


def _get_name(name):
    new_name_list = []
    new_name = re.sub(r'\([^)]*\)', '', name)
    new_name = new_name.replace("LIMITED,", "LIMITED")
    for divider in dividers:
        new_name = new_name.replace(divider, divider[1:])
    new_name = new_name.replace("INC.", "INC")
    new_name = new_name.replace("LTD.", "LTD")
    name_list = new_name.split('AND')
    stash = []
    for word in name_list:
        word_list = word.split(',')
        for new_word in word_list:
            new_word = new_word.split()
            if stash:
                new_word.append(stash.pop())
            if len(new_word) != 1:
                new_word = ' '.join([word.capitalize() for word in new_word if '(' not in word])
                if new_word.startswith('Inc '):
                    new_word = new_word.replace("Inc ", '') + " Inc"
                if new_word.startswith('By ') and len(new_word.split()) > 3:
                    new_word = new_word.replace("By ", '')
                new_name_list.append(new_word)
            else:
                stash.append(new_word[0])

    return new_name_list


def _get_scrape_urls():
    """find all scrapable links on main page"""

    i = 0
    while i < 30:
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
            matter_type = " ".join([word.capitalize() for word in matter_type.split()])
            date_failed = td[3].get_text().strip()
            date_failed = "{}-{}-{}".format(date_failed[:4], date_failed[4:6], date_failed[6:])

            fields = [{"name": "Matter Type", "value": matter_type},
                      {"name": "Docket Number", "value": href},
                      {"name": "Date Failed", "value": date_failed}]

            names = _get_name(name):
                if len(names) > 1:
                    name = names[0]
                    aka = []
                    for aka_name in names:
                        aka.append({'name': aka_name})
                else:
                    name = names[0]

                my_id = helpers.make_id(new_name)
                if len(my_id) > 99:
                    my_id = my_id[:99]

                if any(word in name for word in company):
                    entity_type = "company"
                else:
                    entity_type = "person"

                if aka:
                    yield {
                        "_meta": {
                            "id": my_id,
                            "entity_type": entity_type
                        },
                        "fields": fields,
                        "aka": aka,
                        "name": name,
                    }
                else:    
                    yield {
                        "_meta": {
                            "id": my_id,
                            "entity_type": entity_type
                        },
                        "fields": fields,
                        "name": name,
                    }


def main():
    for entity in _generate_entities():
        helpers.emit(entity)


if __name__ == "__main__":
    main()
