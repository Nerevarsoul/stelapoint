from datetime import date, timedelta
from urllib.parse import urljoin
import helpers
from bs4 import BeautifulSoup


_base_url = "http://www.fca.org.uk/your-fca/list?ttypes=Final+Notice&yyear=&ssearch=&ppage="
_site_url = "http://www.fca.org.uk"
companies = ("ltd", "limited", "company", "services", "bank", "trading", "financial")


def get_date(mydate):
    if mydate == "Today":
        return date.today().strftime("%y-%m-%d")
    elif mydate == "Yesterday":
        return (date.today() - timedelta(days=1)).strftime("%y-%m-%d")
    else:
        mydate = mydate.split('/')
        return "{}-{}-{}".format(mydate[2], mydate[1], mydate[0])


def _generate_entities():
    """for each scrapable page, yield an entity"""
    run = True
    page = 0
    while run:
        url = _base_url + str(page)
        page += 1
        doc = BeautifulSoup(helpers.fetch_string(url), "html.parser")
        div = doc.find('div', id="resultsSearchBox")
        all_h3 = div.find_all("h3", id='')

        if not all_h3:
            run = False
            return

        for h3 in all_h3:
            a = h3.find('a')
            href = urljoin(_site_url, a['href'])
            name = a.get_text().split(':')[1].strip()
            sub = h3.find_next_sibling('sub')
            spans = sub.find_all('span')
            if spans:
                published = get_date(spans[0].get_text().strip())
                modified = get_date(spans[0].get_text().strip())
            else:
                sub = sub.get_text().strip()
                published = get_date(sub[-10:])
                modified = get_date(sub[11:21])

            if any(company in name.lower() for company in companies):
                entity_type = "company"
            else:
                entity_type = "person"

            fields = [
                {"tag": "url", "value": href},
                {"tag": "Published", "value": published},
                {"tag": "Last Modified", "value": modified}
            ]

            yield {
                "_meta": {
                    "id": helpers.make_id(name),
                    "entity_type": entity_type
                },
                "fields": fields,
                "name": name
            }


def main():
    for entity in _generate_entities():
        helpers.emit(entity)


if __name__ == "__main__":
    main()
