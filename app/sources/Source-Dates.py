'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd
from bs4 import BeautifulSoup
import requests


# ---------------------------------------------------------------------------- #
#                                 Data Sources                                 #
# ---------------------------------------------------------------------------- #

# ------------------------------- Telegeography ------------------------------ #

# 'url_tel' = Telegeography GitHub repo.
url_tel = 'https://github.com/telegeography/www.submarinecablemap.com'
# 'html_tel' = Read HTML of 'url_tel' to 'html_tel'.
html_tel = requests.get(url_tel).text
# Add HTML to 'soup' with an XML parser.
soup = BeautifulSoup(html_tel, 'lxml')
# 'updt_tel' = date submarine cables were last updated.
updt_tel = soup.find('relative-time').text
print(updt_tel)


# ------------------------------ ITU Indicators ------------------------------ #

# 'url_src' = Indicator's source.
url_src = 'https://www.itu.int/en/ITU-D/Statistics/Pages/stat/default.aspx'
# 'html_src' = Read HTML of 'url_src' to 'html_src'.
html_src = requests.get(url_src).text
# Add HTML to 'soup' with an XML parser.
soup = BeautifulSoup(html_src, 'lxml')
# 'updt_ind' = date indicators were last updated.
updt_ind = soup.find('strong', class_="ms-rteThemeForeColor-9-0").text
updt_ind = updt_ind.replace(u'\u00A0' + ' Released on ', '')
print(updt_ind)


# -------------------------------- ITU Baskets ------------------------------- #

# 'url_ipb' = Basket's source.
url_ipb = "https://www.itu.int/en/ITU-D/Statistics/Documents/publications/prices2020/ITU_ICTPriceBaskets_2008-2020.xlsx"
# 'df_s4' = Read sheet 4 of the 'url_ipb' into 'df_s1' dataframe.
df_s4 = pd.read_excel(url_ipb, sheet_name=3)
# 'updt_ipb' date baskets were last updated.
updt_ipb = str(df_s4.iloc[-1]['Unnamed: 2'])
updt_ipb = updt_ipb.split()[0]
print(updt_ipb)

