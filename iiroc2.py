from datetime import datetime
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

import helpers

_base_url = "http://www.iiroc.ca/industry/enforcement/Pages/Search-Disciplinary-Cases.aspx"


def _get_scrape_urls():
    """find all scrapable links on main page"""

    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
    driver.get(_base_url)
    list_data = []

    while True:
        time.sleep(3)
        data = driver.find_elements_by_xpath("//td[@class='ms-vb']")
        _generate_entities(data)
        try:
            next_a = driver.find_element_by_xpath("//img[@src='/_layouts/images/next.gif']/parent::a")
            next_a.click()
        except NoSuchElementException:
            break
    driver.close()
    return list_data


def _generate_entities(data):
    """for each scrapable page, yield an entity"""

    i = 0
    while i < len(data):
        release_date = datetime.strptime(data[i].text, '%m/%d/%Y')
        release_date = release_date.strftime('%Y-%m-%d')
        name = data[i+1].text
        url = data[i+1].find_element_by_tag_name('a').get_attribute("/href")

        href = data[i+2].find_element_by_tag_name('a').get_attribute("/href")
        related = []
        if href:
            doc = BeautifulSoup(helpers.fetch_string(href), "html.parser")
            tds = doc.find_all("td", class_='ms-vb')
            for td in tds:
                try:
                    related.append(td.find('a')['href'])
                except AttributeError:
                    pass
         
        related_documents = ' '.join(related) 
        fields = [{"name": "Release date", "value": release_date},
                  {"tag": "url", "value": url},
                  {"name": "Related documents", "value": related_documents}]
        i += 3

        my_id = helpers.make_id(name)
        if len(my_id) > 99:
            my_id = my_id[:99]

        entity = {
            "_meta": {
                "id": my_id,
                "entity_type": "company"
            },
            "fields": fields,
            "name": name,
        }

        helpers.emit(entity)


def main():
    _get_scrape_urls()


if __name__ == "__main__":
    main()
