import requests
import bs4
from bs4 import BeautifulSoup, Tag
from typing import Any
import csv
import os

csv_path = 'data/csv/FReD_data.csv'

def scrap():

    url = 'http://www.reflectance.co.uk//advanceresults.php?bcolourc=&hcolourc=Human%20Colour&maincolourc=Main%20Colour&flowersectc=&altitudec=&heightc=&tubec=&corollac=&pollinatorc=&familyc=Family&genusc=Genus&speciesc=Species&countryc=&townc=&eastc=&southc=&collectorc=&publicationc=&accessionc=&family=*Any%20Family*&genus=*Any%20Genus*&species=*Any%20Species*&country=*Any%20Country*&town=*Any%20Town*&bcolour=*Any%20Colour*&hcolour=*Any%20Colour*&flowersect=*Any%20Section*&pollinator=*Any%20Pollinator*&collector=*Any%20Collector*&maincolour=*Do%20not%20mind*&altitudegreat=-1&altitudeless=2801&heightgreat=-1&heightless=1001&tubegreat=-1&tubeless=61&corollagreat=-1&corollaless=161'

    response = requests.get(url)

    if response.status_code == 200:
        
        soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        
        header_row = soup.find('tr', {"bgcolor": "#8DCE5E"})
        
        if not header_row:
            return
        
        column_names: list[str] = []
        
        for td in header_row.find_all('td'):
            a_tag = td.find('a')
            
            if a_tag:
                column_names.append(a_tag.get_text(strip=True))
            else:
                column_names.append(td.get_text(strip=True))
        
        rows = soup.find_all('tr', {'style': 'cursor: pointer'})
        
        print(rows)
        
        rows_values: list[tuple[Any, ...]] = []
        
        for row in rows:
            
            td_tags = row.find_all_next('td', limit=len(column_names))
            
            if not td_tags:
                continue
            
            values: list[Any] = [td.get_text(strip=True) for td in td_tags]
            
            rows_values.append(tuple(values))
        
        print(column_names, rows_values)
        
        with open(csv_path, 'w') as file:
            writer = csv.writer(file, 'excel')
            writer.writerow(column_names)
            writer.writerows(rows_values)

if not os.path.exists(csv_path):
    scrap()