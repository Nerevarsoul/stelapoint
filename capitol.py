from datetime import datetime

from bs4 import BeautifulSoup

import helpers


_base_url = ("http://capital.sec.or.th/webapp/enforce/recent_enforce_query_eng.php",
             "http://capital.sec.or.th/webapp/adm_sanc/seequery_eng_p21.php?cmbcsd_desc=all&cmbstat_desc=all&miss_stat_code=&query_type=true&txtEfftDate=&txtExpDate=&txtPerson_name=&ref_id=213&txtother=",
             "http://capital.sec.or.th/webapp/enforce/admsanc_dvact_queryeng_p2.php?cmbbuss_type=all&cmbcsd_code=all&query_type=M&txtStartDate=&txtEndDate=&txtsanction_name=&content_id=5")


def _generate_entities():
    """for each scrapable page, yield an entity"""

    doc = BeautifulSoup(helpers.fetch_string(_base_url[0]), "html.parser")
    form = doc.find('form', {'name': 'criminalqueryeng_p2'})
    tables = form.find_all('table', {'bgcolor': '#84BD00'})

    tr = tables[0].find_all('tr')
    i = 1
    while i < len(tr):
        td = tr[i].find_all('td')
        name = td[2].get_text().strip()
        date_filing = td[1].get_text().strip()
        url = td[6].find('a')['href']
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
        name = td[4].get_text().strip()
        date_filing = td[1].get_text().strip()
        url = td[8].find('a')['href']
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
    table = form.find('table', {'bgcolor': '#84BD00'})
    




def main():
    for entity in _generate_entities():
        helpers.check(entity)


if __name__ == "__main__":
    main()
