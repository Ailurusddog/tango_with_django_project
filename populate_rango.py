import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tango_with_django_project.settings')

import django
django.setup()

from rango.models import Category, Page


def add_cat(name, views=0, likes=0):
    c, created = Category.objects.get_or_create(name=name)
    c.views = views
    c.likes = likes
    c.save()
    return c


def add_page(category, title, url, views=0):
    p, created = Page.objects.get_or_create(category=category, title=title)
    p.url = url
    p.views = views
    p.save()
    return p


def populate():
    python_pages = [
        {'title': 'Official Python Tutorial',
         'url': 'https://docs.python.org/3/tutorial/',
         'views': 128},
        {'title': 'How to Think like a Computer Scientist',
         'url': 'http://www.greenteapress.com/thinkpython/',
         'views': 64},
        {'title': 'Learn Python in 10 Minutes',
         'url': 'https://www.korokithakis.net/tutorials/python/',
         'views': 32},
    ]

    django_pages = [
        {'title': 'Official Django Tutorial',
         'url': 'https://docs.djangoproject.com/en/2.2/intro/tutorial01/',
         'views': 64},
        {'title': 'Django Rocks',
         'url': 'http://www.djangorocks.com/',
         'views': 32},
        {'title': 'How to Tango with Django',
         'url': 'http://www.tangowithdjango.com/',
         'views': 16},
    ]

    other_pages = [
        {'title': 'Bottle',
         'url': 'https://bottlepy.org/docs/dev/',
         'views': 16},
        {'title': 'Flask',
         'url': 'https://flask.palletsprojects.com/',
         'views': 32},
    ]

    # 这些值是 tests_chapter5.py 里硬编码检查的
    cats = {
        'Python': {'pages': python_pages, 'views': 128, 'likes': 64},
        'Django': {'pages': django_pages, 'views': 64, 'likes': 32},
        'Other Frameworks': {'pages': other_pages, 'views': 32, 'likes': 16},
    }

    for cat_name, cat_data in cats.items():
        c = add_cat(cat_name, cat_data['views'], cat_data['likes'])
        for p in cat_data['pages']:
            add_page(c, p['title'], p['url'], p['views'])

    # 打印确认
    for c in Category.objects.all():
        print(f'{c.name}: views={c.views}, likes={c.likes}')
        for p in Page.objects.filter(category=c):
            print(f'  - {p.title} ({p.views} views)')


if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()
