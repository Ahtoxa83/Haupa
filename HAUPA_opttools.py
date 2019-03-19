import os
import csv
import re
import requests
from bs4 import BeautifulSoup
from random import choice, uniform
from time import sleep
from multiprocessing import Pool
from datetime import datetime


def get_html(url, useragent=None, proxy=None):
    r = requests.get(url, headers=useragent, proxies=proxy)
    return r.text

def get_file_path(page):
    user_agents = open('useragents.txt').read().split('\n')
    proxies = open('proxies.txt').read().split('\n')
    proxy = {'http': 'http://' + choice(proxies)}
    useragent = {'User-Agent': choice(user_agents)}

    count = 1
    base_url = 'https://opttools.ru'
    page_with_name = get_html(page, useragent, proxy)

    soup = BeautifulSoup(page_with_name, 'lxml')

    # take folder name
    folder_row = []
    folder_names = soup.find('div', class_='breadcrumb-new').find_all('span', class_='breadcrumb__title_new')
    for folder_name in folder_names:
        breadcrumb__title_new = folder_name.text
        name_translit = (translite(breadcrumb__title_new))
        # folder = append (name_translit)
        name_translit = name_translit[:50]
        folder_row.extend([name_translit])
    folder = '\\'.join(folder_row[1:])
            
    # 
    
    try:
        file_path = soup.find('img', id='zoom').get('data-zoom-image')
    except:
        file_path = soup.find('div', class_='detail_picture').find('meta').get('content')
        # file_path = soup.find('div', class_='detail_picture').find('div', class_ = 'catalog-detail-images').get('src')

    file_name = soup.find('div', class_='catalog-detail-properties').find_all('div', class_='val')[2].text.strip()
    
    try:

        more_photos = soup.find('div', class_='more_photo').find_all('a', 'catalog-detail-images fancybox')

        for more_photo in more_photos:
            link_photo = base_url + more_photo.get('href')
            exten_photo = link_photo.split('.')[-1]
            name_photo = link_photo.split('/')[-1].split('.')[-2]
            next_photo = file_name + '-' + str(count) + '.' + exten_photo
            save_image(get_name(next_photo, folder), get_file(link_photo))
            count += 1
    except:
        more_photo = ""
        next_name = ""

    file_name += '.jpg'
    full_path = base_url + file_path
    save_image(get_name(file_name, folder), get_file(full_path))
    # print (get_name(file_name, folder))

def get_name(file_name, folder):
    name = re.sub(r"/", "'", file_name)
    write_csv(name)

    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder + '\\' + name

def translite(name):
    #Заменяем пробелы и преобразуем строку к нижнему регистру
    name = name.replace(' ','-').lower()
    name_translit = re.sub(r"/", "'", name)
    #
    transtable = (
        ## Большие буквы
        (u"Щ", u"Sch"),
        (u"Щ", u"SCH"),
        # two-symbol
        (u"Ё", u"Yo"),
        (u"Ё", u"YO"),
        (u"Ж", u"Zh"),
        (u"Ж", u"ZH"),
        (u"Ц", u"Ts"),
        (u"Ц", u"TS"),
        (u"Ч", u"Ch"),
        (u"Ч", u"CH"),
        (u"Ш", u"Sh"),
        (u"Ш", u"SH"),
        (u"Ы", u"Yi"),
        (u"Ы", u"YI"),
        (u"Ю", u"Yu"),
        (u"Ю", u"YU"),
        (u"Я", u"Ya"),
        (u"Я", u"YA"),
        # one-symbol
        (u"А", u"A"),
        (u"Б", u"B"),
        (u"В", u"V"),
        (u"Г", u"G"),
        (u"Д", u"D"),
        (u"Е", u"E"),
        (u"З", u"Z"),
        (u"И", u"I"),
        (u"Й", u"J"),
        (u"К", u"K"),
        (u"Л", u"L"),
        (u"М", u"M"),
        (u"Н", u"N"),
        (u"О", u"O"),
        (u"П", u"P"),
        (u"Р", u"R"),
        (u"С", u"S"),
        (u"Т", u"T"),
        (u"У", u"U"),
        (u"Ф", u"F"),
        (u"Х", u"H"),
        (u"Э", u"E"),
        (u"Ъ", u""),
        (u"Ь", u""),
        ## Маленькие буквы
        # three-symbols
        (u"щ", u"sch"),
        # two-symbols
        (u"ё", u"yo"),
        (u"ж", u"zh"),
        (u"ц", u"ts"),
        (u"ч", u"ch"),
        (u"ш", u"sh"),
        (u"ы", u"yi"),
        (u"ю", u"yu"),
        (u"я", u"ya"),
        # one-symbol
        (u"а", u"a"),
        (u"б", u"b"),
        (u"в", u"v"),
        (u"г", u"g"),
        (u"д", u"d"),
        (u"е", u"e"),
        (u"з", u"z"),
        (u"и", u"i"),
        (u"й", u"j"),
        (u"к", u"k"),
        (u"л", u"l"),
        (u"м", u"m"),
        (u"н", u"n"),
        (u"о", u"o"),
        (u"п", u"p"),
        (u"р", u"r"),
        (u"с", u"s"),
        (u"т", u"t"),
        (u"у", u"u"),
        (u"ф", u"f"),
        (u"х", u"h"),
        (u"э", u"e"),
        (u":", u""),
        (u",", u""),
        (u"ъ", u""),
        (u"ь", u""),
        (u".", u""),
        (u",", u""),
    )
    #перебираем символы в таблице и заменяем
    for symb_in, symb_out in transtable:
        name_translit = name_translit.replace(symb_in, symb_out)
    #возвращаем переменную
    return name_translit

def get_file(full_path):
    r = requests.get(full_path, stream=True)
    return r

def save_image(name, file_object):
    with open(name, 'bw') as f:
        for chunk in file_object.iter_content(4096):
            f.write(chunk)

def write_csv(name):
    with open('opttools.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([name])

def make_all (url):
    get_file_path (url)

def main():
    start = datetime.now()

    time_to_sleep = (uniform(3, 6))
    sleep(time_to_sleep)
    
    links = []
    with open('opttools_list.csv', 'r+') as f:
        reader = csv.reader(f)
        for row in reader:
            row = ''.join(row)
            links.append(row)

    with Pool(5) as p:
        p.map (make_all, links)

    end = datetime.now()

    total = end - start
    print(str(total))

if __name__ == '__main__':
    main()