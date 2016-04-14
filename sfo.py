import helpers
from bs4 import BeautifulSoup


_base_url = "https://www.sfo.gov.uk/our-cases/"
_base_url2 = "https://www.sfo.gov.uk/our-cases/case-archive/"


def divide_name(names, divide):

    names = names.split(divide)
    if len(names) == 1:
        return names

    new_names = []
    i = 0
    while i < len(names):
        if ' ' in names[i]:
            new_names.append(names[i])
            i += 1
        else:
            if i % 2 == 0:
                name = names[i] + divide + names[i+1]
                i += 2
                new_names.append(name)
            else:
                new_names[-1] = new_names[-1] + divide + names[i]
                i += 1
    return new_names


def _get_scrape_urls():
    """find all scrapable links on main page"""

    for url in _base_url, _base_url2:

        doc = BeautifulSoup(helpers.fetch_string(url, cache_hours=6), "html.parser")
        uls = doc.find_all("ul", class_="contentListing")

        for ul in uls:
            href = ul.find_all("a")
            for link in href:
                if link:
                    yield link['href']


def _generate_entities():
    """for each scrapable page, yield an entity"""

    for url in _get_scrape_urls():

        doc = BeautifulSoup(helpers.fetch_string(url, cache_hours=6), "html.parser")
        section = doc.find('section', id="pageContent")
        h1 = section.find("h1").get_text().strip()

        if '(' in h1:
            h1_without_bracket = h1.split('(')[0] + h1.split(')')[-1]
            h1_without_bracket = h1_without_bracket.strip()
        else:
            h1_without_bracket = h1

        names1 = h1_without_bracket.split(',')
        names2 = []
        for name in names1:
            for new_name in divide_name(name, ' & '):
                names2.append(new_name)
        new_names = []

        for name in names2:
            for new_name in divide_name(name, ' and '):
                new_names.append(new_name)

        text = section.find("p").get_text().strip()
        fields = [
            {"tag": "url", "value": url},
            {"name": "text", "value": text}
            ]

        custom_fields = section.find_all("h2")
        for custom_field in custom_fields:
            field_name = custom_field.get_text().strip()
            if field_name == 'Defendants':
                values1 = section.find_all('div', class_="chargeDefendant")
                values2 = section.find_all('div', class_="chargeCharge")
                value = zip(values1, values2)
                field_value = ' '.join([value[0].get_text().strip() + ' ' + value[1].get_text().strip() for value in values])
            else:
                field_value = custom_field.find_next_sibling('p').get_text().strip()
            fields.append({"tag": field_name, "value": field_value})

        for name in new_names:

            name = name.strip()

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
