from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import urllib.request as req
import json
from datetime import datetime


bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(ID):
    from webapp.models import Reader, Librarian, Admin
    if Reader.query.filter_by(ID = ID).first():

        return Reader.query.filter_by(ID = ID).first()
    if Librarian.query.filter_by(ID = ID).first():

        return Librarian.query.filter_by(ID = ID).first()
    if Admin.query.filter_by(ID=ID).first():

        return Admin.query.filter_by(ID=ID).first()

class GetBook:
    url_header = "https://api.douban.com/v2/book/isbn/:"
    header = ("User-Agent","Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")
    def __init__(self,isbn="9780553212419"):
        self.isbn = isbn
        self.url = self.url_header+isbn
        r = req.Request(self.url)
        r.add_header(*self.header)
        r.add_header('GET',self.url)
        try:
            data = req.urlopen(r).read().decode('UTF-8')
        except Exception as err:
            print(err)
            data = None
            raise ValueError
        self.book_info = json.loads(data) if data  else None 
        self.book = None
        self.to_book()

    def to_book(self):
        if self.book_info is None:
            return None
        title = self.book_info['title']
        subtitle = self.book_info['subtitle']
        author = ' '.join(self.book_info['author'])
        publish_date = self.book_info['pubdate']
        image_path = self.book_info['image']
        summary = self.book_info['summary']
        price = self.book_info['price']
        press = self.book_info['publisher']
        ISBN = self.book_info['isbn13']

        self.book = dict(title=title,subtitle=subtitle,author=author,publish_date=publish_date,image_path=image_path \
            ,summary=summary,price=price,press=press,ISBN=ISBN)

    def change_urlheader(self,new_urlheader):
        self.url_header = new_urlheader
    
    def __getitem__(self,key):
        if self.book is None or key not in self.book:
            return None
        return self.book[key]
def get_week(date):
    return int(datetime.isocalendar(date)[1])
def get_month(date):
    return int(date.month)
def get_year(date):
    return int(date.year)
def download_picture(url,path):
    if len(url) == 0:
        return False
    try:
        data = req.urlopen(url).read()
        if not data:
            return False
        tail = url.split('.')[-1]
    except Exception:
        print('exp')
        with open(path+'default.png','rb') as file:
            data = file.read()
            tail='png'
    path += str(datetime.now().time()).split('.')[-1]+ '.'+tail
    
    with open(path,'wb') as file:
        file.write(data)

    return path
if __name__ == '__main__':
    pic = GetBook()['image_path']
    download_picture(pic,r'E:\\Program\\Library_Manage_System\\webapp\\static\\picture\\2')

