import requests
import random
from bs4 import BeautifulSoup
import re
import xlsxwriter


def get_page(url):
    url_list = (
        {'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1"},
        {'user-agent': "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1"},
        {'user-agent': "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11"},
        {'user-agent': "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11"},
        {'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"}
    )
    user_agent = random.choice(url_list)
    response = requests.get(url, headers=user_agent)
    if response.status_code == 200:
        return response.text


def get_onepage_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    data_one_page,data = [],[]
    for item in soup.select('ol li'):
        item = str(item)
        sub_soup = BeautifulSoup(item,'html.parser')
        link = sub_soup.select('div div.pic a')[0]['href']
        names = sub_soup.findAll('span',attrs={'class','title'})
        cname = names[0].text
        if len(names)==2:
            ename = names[1].string.replace('/', '').lstrip()
        else:
            ename = ''
        info = sub_soup.find('div',attrs={'class','bd'}).find('p').text
        director = re.findall('导演:\s\S*',info)[0][4:]
        year = re.search('\d{4}',info).group()
        country = re.search('\d{4}\s[/]\s.*?\s',info).group()[7:-1]
        rating = sub_soup.find('span',attrs={'class','rating_num'}).string
        star_info = sub_soup.find('div',attrs={'class','star'}).text
        rating_people = re.search('\d*人',star_info).group()[:-1]
        data = [link,cname,ename,director,year,country,rating,rating_people]
        data_one_page.append(data)
    return data_one_page

def save_data(all_data):
    with xlsxwriter.Workbook('movie_db_top250.xlsx') as workbook:
        row, col = 0, 0
        col_name = ['链接','中文名','原名','导演','年份','国家','评分','评分人数']
        worksheet = workbook.add_worksheet('movie')
        worksheet.write_row('A1',col_name)
        for data in all_data:
            row = row + 1
            worksheet.write_row(row, col, data)

def get_all_data(url):
    all_data,one_page_data = [],[]
    temp_url = url
    while True:
        try:
            soup = BeautifulSoup(get_page(temp_url),'html.parser')
            all_data.extend(get_onepage_data(get_page(url)))
            sub_url = soup.select('span.next link')[0]['href']
            temp_url = url+sub_url
            print(temp_url)
        except IndexError:
            return all_data
def main():
    url = "https://movie.douban.com/top250"
    all_data = get_all_data(url)
    save_data(all_data)
    print(all_data)

if __name__ == "__main__":
    main()
