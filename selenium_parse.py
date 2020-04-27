import re
from selenium import webdriver

main_url = 'https://www.wellton-towers.ru/filter/?limit=1&mode=cards&offset=100'

base_url = 'https://www.wellton-towers.ru/flats/?limit=238&mode=cards&offset=0'

driver = webdriver.Chrome()
driver.get(base_url)
print(driver.page_source)
exit()

begin_url = "https://www.wellton-towers.ru"
src = begin_url + re.search(r'src=\\"(.*.svg)', driver.page_source).group(1)
print(src)

full_href = re.search(r'href=\\\"(.*?)\".*href=\\\"(.*?)\"', driver.page_source)
href1 = full_href.group(1)
href2 = full_href.group(2)
print(href1)
print(href2)