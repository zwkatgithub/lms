from webapp.models import Book

def search_by_title(content):
    return Book.query.filter(Book.title.like('%'+content+'%'))

def search_by_author(content):
    return Book.query.filter(Book.author.like('%'+content+'%'))


def search_by_ISBN(content):
    return Book.query.filter_by(ISBN=content).first()

def search_by(method,content):
    if method ==1:
        #title
        return search_by_title(content)
    elif method==2:
        #author
        return search_by_author(content)
    elif method==3:
        #ISBN
        return search_by_ISBN(content)
    else:
        return None


def book_info(book):
    res = dict()
    res['title'] = book.title
    res['author'] = book.author
    res['press'] = book.press
    res['publish_date'] = str(book.publish_date)
    res['ISBN'] = book.ISBN
    res['location'] = book.location
    res['summary'] = str(book.summary)
    res['picture'] = book.picture

    return res

