import pandas
import requests
from bs4 import BeautifulSoup

# url = 'http://www.railwaycodes.org.uk/pride/elrmapping.shtm'

# pd = pandas.read_html(url)[0]

# for index, row in pd.iterrows():
#     with open('./reference_data/elr_mapping.csv', 'a', encoding='utf-8') as file:
#         file.write(f"{row['ELR']}\t{row['Miles from']}\t{row['Miles to']}\t{row['LOR code']}\n")

# for letter in range(65, 91):
#     url = f"http://www.railwaycodes.org.uk/elrs/elr{str(chr(letter)).lower()}.shtm"
#     pd = pandas.read_html(url)[0]
#     for index, row in pd.iterrows():
#         with open('./reference_data/elr_references.csv', 'a', encoding='utf-8') as file:
#             file.write(f"{row['ELR']}\t{row['Line name']}\t{row['Mileages']}\t{row['Datum']}\t{row['Notes']}\n")

# prefix_list = ['CY', 'EA', 'GW', 'LN', 'MD', 'NW', 'SC', 'SO', 'SW', 'XR']

# for prefix in prefix_list:
#     url = f"http://www.railwaycodes.org.uk/pride/pride{str(prefix).lower()}.shtm"
#     pd = pandas.read_html(url)[0]
#     for index, row in pd.iterrows():
#         with open('./reference_data/pride_lor_codes.csv', 'a+', encoding='utf-8') as file:
#             file.write(f"{row['Code']}\t{row['Line Name']}\t{row['Route Availability (RA)']}\n")

# url = 'http://www.railwaycodes.org.uk/pride/elrmapping.shtm'
# pd = pandas.read_html(url)[0]

# for _, row in pd.iterrows():
#     elr = row['ELR']
#     l_case = elr.lower()
#     prefix = l_case[0]


#     url = f'http://www.railwaycodes.org.uk/elrs/_mileages/{prefix}/{l_case}.shtm'
#     r = requests.get(url)
#     if not r.status_code == 200:
#         continue
#     soup = BeautifulSoup(r.text, 'html5lib')
#     try:
#         data = soup.find_all('pre')[0].get_text()
#         with open(f'./reference_data/mileage_files/{elr}.txt', 'w', encoding='utf-8') as file:
#             file.write(data)
#     except IndexError:
#         continue

url = 'http://www.railwaycodes.org.uk/stations/stationa.shtm'
pd = pandas.read_html(url)[0]
print(pd)
