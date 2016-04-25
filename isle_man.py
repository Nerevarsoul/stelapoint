import helpers
from bs4 import BeautifulSoup
from urllib.parse import urljoin


_base_url = "http://www.tynwald.org.im/memoff/member/Pages/default.aspx"
_site_url = "http://www.tynwald.org.im"
_base_url2 = "http://www.tynwald.org.im/memoff/former/Pages/HoKNewOld.aspx"
month = {'January': '01', 'February': '02', 'March': '03', 'April': '04',
         'May': '05', 'June': '06', 'July': '07', 'August': '08',
         'September': '09', 'October': '10', 'November': '11', 'December': '12'}
name_words = ('Hon ', ' MHK', 'Mrs ', 'The ', 'Mlc ', 'Bsc ')


def _get_name(name):
    name = name.split('Esq')[0]
    name = name.split('Bsc')[0]
    for word in name_words:
        name = name.replace(word, '')
    name = " ".join([name.capitalize() for name in name.split()])
    if ',' in name:
        name = name.split(',')[1] + ' ' + name.split(',')[0]
    return name.strip()


def get_date(date):
    if 'th' in date:
        date = '{}-{}-{}'.format(date.split()[2][:4],
                                 month[date.split()[1]],
                                 date.split()[0].replace('th', ''))
    return date


def _get_scrape_urls():
    """find all scrapable links on main page"""

    doc = BeautifulSoup(helpers.fetch_string(_base_url), "html.parser")
    council = doc.find('div', id='div_938d72bb-8154-4b6a-bd71-8144ca6bf1a0')
    house = doc.find('div', id='div_47793ec9-3449-46a3-9095-f2eb8c475846')

    council_lis = council.find_all("div", class_="link-item")
    house_lis = house.find_all("li", class_="dfwp-item")

    for li in council_lis:
        person = li.find("a")
        link = person["href"]
        name = _get_name(person.get_text())
        office = "Legislative Council"
        entity = _generate_entities(link, name, office)
        yield entity

    for li in house_lis:
        try:             
            parish = li.find("div", class_="groupheader").get_text().strip()
        except AttributeError:
            continue
        all_div = li.find_all("div", class_="link-item")
        for div in all_div: 
            person = div.find("a")
            link = person["href"]
            name = _get_name(person.get_text())
            office = "House of Keys"
            entity = _generate_entities(link, name, office, parish)
            yield entity

    doc = BeautifulSoup(helpers.fetch_string(_base_url2), "html.parser")
    div = doc.find('div', id='div_a1526572-2de9-494b-a410-6fdc17d3b84e')
    trs = div.find_all('tr', class_='ms-itmhover')
    for tr in trs:
        try:
            td = tr.find_all('td')
            name = _get_name(td[1].get_text())
            office = "House of Keys"
            link = urljoin(_site_url, td[3].find('a')['href'])
            years_active = td[2].get_text().strip()
            try:
                date = int(years_active.split()[-1])
                if date < 1990:
                    continue
            except ValueError:
                pass
            if '.pdf' in link:
                fields = [
                    {"tag": "url", "value": link},
                    {"tag": "Years Active", "value": years_active},
                    {"tag": "Office", "value": office}
                ]
                yield {
                    "_meta": {
                        "id": helpers.make_id(name),
                        "entity_type": "person"
                    },
                    "fields": fields,
                    "name": name
                }
                continue
            entity = _generate_entities(link, name, office, years_active)
            yield entity
        except TypeError:
            pass


def _generate_entities(url, name, office, years_active=None, parish=None):
    """for each scrapable page, yield an entity"""

    doc = BeautifulSoup(helpers.fetch_string(url), "html.parser")
    img = urljoin(_site_url, doc.find("img", class_="ms-rteImage-2")['src'])
    h3 = doc.find_all('h3', class_="ms-rteElement-H3")

    div = h3[0].find_next_sibling()
    current = 'Current Posts ' + div.get_text().strip()
    while div.name != 'h3':
        div = div.find_next_sibling()
        if div:
            current += ' ' + div.get_text().strip()
        else:
            break
    
    current = current.replace('dateMember', 'date Member')

    fields = [
        {"tag": "url", "value": url},
        {"tag": "Current Posts", "value": current},
        {"tag": "picture_url", "value": img},
        {"tag": "Office", "value": office},
    ]

    if years_active:
        fields.append({"tag": "Years Active", "value": years_active})

    if parish:
        fields.append({"tag": "Parish", "value": parish})

    try:
        p = h3[1].find_next_sibling()
        career = p.get_text().strip()
        while p.name == 'p':
            p = p.find_next_sibling()
            career += ' ' + p.get_text().strip()
        fields.append({"tag": "Parliamentary Career", "value": career})
    except IndexError:
        pass

    ps = doc.find_all("p", class_="ms-rteElement-P")
    for p in ps:
        p = p.get_text().strip()
        if 'Born' in p:
            fields.append({"tag": "date_of_birth", "value": get_date(p.split(':')[-1].strip())})
        elif 'Parents' in p:
            fields.append({"tag": "Parents", "value": p.split(':')[-1].strip()})
    
    return {
        "_meta": {
            "id": helpers.make_id(name),
            "entity_type": "person"
        },
        "fields": fields,
        "name": name
    }


def main():
    for entity in _get_scrape_urls():
        helpers.check(entity)


if __name__ == "__main__":
    main()
