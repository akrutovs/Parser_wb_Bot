# -*- coding: utf-8 -*-
import apiai
import telebot
import config
import json
import requests
import bs4 
import requests 
import collections
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#logging.basicConfig( level=  logging.ERROR) 
#logger = logging.getLogger('wb') 


ParseResult = collections.namedtuple(
    'ParseResult', 
    (
        'image',
        'article',
        'brand_name',
        'goods_name',
        'url',
        'price',
        'old_price',
        'sale',
        'revenu',
        'sales',
        'stars',
        'comments',
        'orders',
        'stocks',
        
    ),
    
)
count = 0
HEADERS = ('Фото','Артикул','Бренд','Товар','Ссылка','Цена','Старая цена','Скидка', 'Выручка за 30 дней','Продажи','Звезды','Комментарии', 'Среднее кол-во заказов','Среднее количество остатков')

html = ''
temp = 'sfdf'
vlozh = 100
gl_url = ''
vl = []

for i in range(1000):
    vl.append(str(i))

bot = telebot.TeleBot(config.API_TOKEN)
print(bot.get_me())


def log(message, answer):
    print("\n ==============")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1} (id = {2}) \nТекст - {3}".format(
        message.from_user.first_name, message.from_user.last_name,
        str(message.from_user.id), message.text))
    print("Ответ - {0}".format(answer))

@bot.message_handler(commands=['help'])
def handle_text(message):
    ans = "Этот бот создан для того, чтобы парсить страницы wb"
    bot.send_message(message.from_user.id, ans)
    log(message, ans)


@bot.message_handler(commands=['start'])
def handle_start(message):
    ans = "Привет, я бот, и пока что со мной \
    можно парсить запросы для WB для этого введи цифру от 1 до 100 - сколько товаров нужно спарсить и вставь ссылку на запрос (не на отдельный товар!))))"
    bot.send_message(message.from_user.id, ans)
    log(message, ans)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    global vlozh
    global vl

    if message.text in vl:
        vlozh = int(message.text)
        string =f'Вложенность {vlozh} товаров'
        bot.send_message(message.from_user.id, string)
        log(message,'Вложенность - '+message.text)

    else:
        log(message,message.text)
        if str(message.text)[:5] =='https':
            bot.send_message(message.from_user.id, 'Я принял ссылку - подожди пару минут')
            log(message,'скинута ссылка - '+str( message.text))
            go_parse(message)
        else:

            bot.send_message(message.from_user.id, 'Бот умеет принимать только ссылку - ссылка должна начинаться на https, так же боту можно скинуть код html страницы')

def go_parse(message):
    #load full html page
    global temp
    global gl_url
    global html
    #options = webdriver.ChromeOptions()
    #options.add_argument('headless')
    #options.add_argument('window-size=1920x935')
    gl_url = str(message.text)
    #driver = webdriver.Chrome(chrome_options=options)
    driver = webdriver.Chrome()
    driver.get(gl_url) #This is a dummy website URL
    try:
        elem = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-card-list")) #This is a dummy element
        )

        html = driver.page_source
        print(html)
    except TimeoutError:
        html = driver.page_source

    driver.quit()
    temp = 'wbb1'
    class Client: 
        def __init__(self):
            global html
            self.session = requests.Session() 
            self.session.headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
                'Accept-Languages' :'ru',}
            self.result = []
            
        def check_pages(self):
            pass
        def load_page(self): 
            global html

            local_html = html
            return local_html
            
        def parse_page(self, text: str): 
            global count
            global vlozh
            soup = bs4.BeautifulSoup(text, "lxml") 
            container = soup.select('div.dtList.i-dtList.j-card-item')
            for block in container:
                count+=1
                self.parse_block(block = block)
                if count == vlozh:
                    break

        def parse_block( self, block): 
            #logger.debug(block)
            #logger.debug('='*100)
            #cсылка на товар
            #_________________________________________________________
            url_block = block.select_one('a.ref_goods_n_p')
            if not url_block:
                #logger.error('no url_block')
                return
            url = url_block.get('href')
            #_________________________________________________________
            #aртикул
            article = str(url).split('/')
            article = article[2]
            #_________________________________________________________
            if not url:
                #logger.error('no href')
                return
            #_________________________________________________________
            #имя бренда
            name_block = block.select_one('div.dtlist-inner-brand-name')
            if not name_block:
                #logger.error(f'no name_block on https://www.wildberries.ru{url}')
                return
            brand_name = name_block.select_one('strong.brand-name')
            if not brand_name:
                #logger.error(f'no brand_name on https://www.wildberries.ru{url}')
                return
            
            brand_name = brand_name.text
            brand_name = brand_name.replace('/', '').strip()
            #_________________________________________________________

            #_________________________________________________________
            #имя товара
            goods_name = name_block.select_one('span.goods-name')
            if not goods_name:
                #logger.error(f'no goods_name on https://www.wildberries.ru{url}')
                return
            goods_name =  goods_name.text.strip()

            #_________________________________________________________
            #комментарии цена старая цена скидка и количество звезд
            block_for_price = block.select_one('div.dtlist-inner-brand')
            comments = block.select_one('span.dtList-comments-count')
            price = block_for_price.select_one('ins.lower-price')
            old_price = block_for_price.select_one('span.price')
            old_price =old_price.select_one('del')
            sale = block_for_price.select_one('span.price-sale')
            stars = block.select_one('span.c-stars-line-lg')
            
            if not stars:
                #logger.error(f'no stars on https://www.wildberries.ru{url}')
                #return
                stars = '?'
            else:
                #print(stars)
                stars = str(stars)
                stars = stars[-10]
                
            if not price:
                #logger.error(f'no price on https://www.wildberries.ru{url}')
                price = '?'
            else:
                price =  price.text.strip()

            if not comments:
                #logger.error(f'no comments on https://www.wildberries.ru{url}')
                comments = '?'
            else:
                comments = comments.text.strip()
            
            if not old_price:
                #logger.error(f'no old_price on https://www.wildberries.ru{url}')
                old_price = ''
            else:
                old_price = old_price.text.strip()
            
            if not sale:
                #logger.error(f'no sale on https://www.wildberries.ru{url}')
                sale = ''
            else:
                sale = sale.text.strip()

            #________________________________________________________
            #ссылка на картинку
            block_for_image = block.select_one('div.l_class')
            img = block_for_image.select_one('img')
            if not img:
                #logger.error(f'no img on https://www.wildberries.ru{url}')
                return
            
            url_image = img.get('data-original')
            if not url_image:
                #logger.error(f'no url_img on https://www.wildberries.ru{url}')
                url_image = ''
            #_______________________________________________________
            global ParseResult
            self.result.append(ParseResult( image = url_image ,article = article, url = 'https://www.wildberries.ru'+url, brand_name = brand_name, goods_name = goods_name,price = price, old_price = old_price, sale =sale,revenu = revenu, sales = sales ,stars = stars, comments = comments,orders = avg_orders, stocks = avg_stocks))
            
            
        def save_results(self):
            global temp
            path = f'/Users/a_krut/Desktop/{temp}.csv'
            with open(path, 'w') as f:
                writer = csv.writer(f, quoting = csv.QUOTE_MINIMAL)
                writer.writerow(HEADERS)
                for item in self.result:
                    writer.writerow(item)
            
        def run(self):
            text = self.load_page()
            self.parse_page(text = text)

            #logger.info(f'получили {len(self.result)}')
            self.save_results()

    parser = Client()
    parser.run()

    bot.send_message(message.from_user.id, 'Ответ получен - держи')
    path = f'/Users/a_krut/Desktop/{temp}.csv'
    document = open(path, 'rb')
    bot.send_document(message.from_user.id, document)
        


bot.polling(none_stop=True, interval=0)
