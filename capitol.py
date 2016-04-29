from datetime import datetime

from bs4 import BeautifulSoup

import helpers


_base_url = ("http://capital.sec.or.th/webapp/enforce/recent_enforce_query_eng.php",
             "http://capital.sec.or.th/webapp/adm_sanc/seequery_eng_p21.php?cmbcsd_desc=all&cmbstat_desc=all&miss_stat_code=&query_type=true&txtEfftDate=&txtExpDate=&txtPerson_name=&ref_id=213&txtother=",
             "http://capital.sec.or.th/webapp/enforce/admsanc_dvact_queryeng_p2.php?cmbbuss_type=all&cmbcsd_code=all&query_type=M&txtStartDate=&txtEndDate=&txtsanction_name=&content_id=5")


def _get_name(name):
    name = name.replace('Mrs. ', '')
    name = name.replace('Mr. ', '')
    name = " ".join([name.capitalize() for name in name.split()])
    return name


def _get_date(old_date):
    old_date = datetime.strptime(old_date, '%d/%m/%Y')
    return old_date.strftime('%Y-%m-%d')


def _generate_entities():
    """for each scrapable page, yield an entity"""

    doc = BeautifulSoup(helpers.fetch_string(_base_url[0]), "html.parser")
    form = doc.find('form', {'name': 'criminalqueryeng_p2'})
    tables = form.find_all('table', {'bgcolor': '#84BD00'})

    tr = tables[0].find_all('tr')
    i = 1
    while i < len(tr):
        td = tr[i].find_all('td')
        name = _get_name(td[2].get_text().strip())
        date_filing = _get_date(td[1].get_text().strip())
        try:
            url = td[6].find('a')['href']
        except TypeError:
            url = ''
        summarized_facts = td[5].get_text().strip()

        fields = [{"name": "Summarized Facts", "value": summarized_facts},
                  {"name": "Press Release", "value": url},
                  {"name": "Date of Complaint Filing", "value": date_filing}]

        yield {
            "_meta": {
                "id": helpers.make_id(name),
                "entity_type": "company"
            },
            "fields": fields,
            "name": name,
        }
        i += 2

    tr = tables[1].find_all('tr')
    i = 1
    while i < len(tr):
        td = tr[i].find_all('td')
        name = _get_name(td[4].get_text().strip())
        date_filing = _get_date(td[1].get_text().strip())
        try:
            url = td[8].find('a')['href']
        except TypeError:
            url = ''
        summarized_facts = td[7].get_text().strip()
        baht = td[9].get_text().strip()
        section = td[5].get_text().strip()
        law = td[6].get_text().strip()
        nomer = td[3].get_text().strip()

        fields = [{"name": "Summarized Facts", "value": summarized_facts},
                  {"name": "Press Release", "value": url},
                  {"name": "Date of Complaint Filing", "value": date_filing},
                  {"name": "Amount of Fines (Baht)", "value": baht},
                  {"name": "Section", "value": section},
                  {"name": "Relevant Law", "value": law},
                  {"name": "Order Number", "value": nomer},
        ]

        yield {
            "_meta": {
                "id": helpers.make_id(name),
                "entity_type": "company"
            },
            "fields": fields,
            "name": name,
        }
        i += 2

    doc = BeautifulSoup(helpers.fetch_string(_base_url[1]), "html.parser")
    tr = doc.find_all('tr')
    i = 0
    while i < len(tr):
        try:
            td=tr[i].find_all('td')
            name = _get_name(td[1].get_text().strip())
            type_personal = td[2].get_text().strip()
            try:
                url = td[3].find('a')['href']
            except TypeError:
                url = ''
            summarized_facts = td[4].get_text().strip()
            administrative_orders = td[5].get_text().strip()
            effective_date = td[6].get_text().strip()
      
            fields = [{"name": "Type of Personal", "value": type_personal},
                      {"name": "Press Release", "value": url},
                      {"name": "Date of Complaint Filing", "value": date_filing},
                      {"name": "Administrative Orders", "value": administrative_orders},
                      {"name": "Summarized Facts", "value": summarized_facts},
                      {"name": "Effective Date", "value": effective_date},
            ]
      
            yield {
                "_meta": {
                    "id": helpers.make_id(name),
                    "entity_type": "company"
                },
                "fields": fields,
                "name": name,
            }
            i += 2
        except:
            i += 1

    doc = BeautifulSoup(helpers.fetch_string(_base_url[2]), "html.parser")
    tr = doc.find_all('tr')
    i = 0
    while i < len(tr):
        try:
            td=tr[i].find_all('td')
            name = _get_name(td[3].get_text().strip())
            sanction = _get_date(td[1].get_text().strip())
            summarized_facts = td[7].get_text().strip()
            nomer = td[2].get_text().strip()
            types_business = td[4].get_text().strip()
            relevant_law = td[5].get_text().strip()
            section = td[6].get_text().strip()
            baht = td[10].get_text().strip()
    
            fields = [{"name": "Date of Imposing the Administrative Sanction", "value": sanction},
                      {"name": "Types of Business", "value": types_business},
                      {"name": "Summarized Facts", "value": summarized_facts},
                      {"name": "Order Number", "value": nomer},
                      {"name": "Relevant Law", "value": relevant_law},
                      {"name": "Section", "value": section},
                      {"name": "Amount of Fines (Baht)", "value": baht},
            ]
    
            yield {
                "_meta": {
                    "id": helpers.make_id(name),
                    "entity_type": "company"
                },
                "fields": fields,
                "name": name,
            }
            i += 2
        except:
            i += 1


def main():
    for entity in _generate_entities():
        helpers.check(entity)


if __name__ == "__main__":
    main()
