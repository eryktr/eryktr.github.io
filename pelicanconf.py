AUTHOR = 'Eryk Trzeciakiewicz'

PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = [
  'sitemap',
  'neighbors',
  'assets',
  'latex',
]

SITENAME = "Let's Research Stuff"
SITESUBTITLE = "Witness the stream of my thoughts being compiled into a text format."
SITEURL = ''
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}

PATH = 'content'

TIMEZONE = 'Europe/Warsaw'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

AUTHORS_BIO = {
  "eryktr": {
    "name": "Eryk Trzeciakiewicz",
    "image": "assets/images/avatar.webp",
    "linkedin": "https://www.linkedin.com/in/eryk-trzeciakiewicz-2a86a1182/",
    "github": "eryktr",
    "location": "Poland",
    "bio": "An engineer pushing code code at work and his limits thereafter. " 
           "Currently chasing latest technologies, learning European languages "
           "and practicing calisthenics."
  }
}

# Social widget
SOCIAL =  (
  ('github', 'https://github.com/eryktr'),
)

COLOR_SCHEME_CSS = 'tomorrow.css'

DEFAULT_PAGINATION = 10

THEME = 'attila-1.3'

### Theme settings
HEADER_COVER = 'assets/images/main_cover.webp'
#HEADER_COLOR = 'black'

JINJA_ENVIRONMENT = {
  'extensions' :[
    'jinja2.ext.loopcontrols',
    'jinja2.ext.i18n',
    'jinja2.ext.do'
  ]
}
#DEFAULT_DATE = 'fs'

#DEFAULT_DATE_FORMAT = '%d %b %Y'

ARTICLE_URL = '{date:%Y}/{date:%m}/{slug}.html'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{slug}.html'
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'
YEAR_ARCHIVE_SAVE_AS = '{date:%Y}/index.html'
MONTH_ARCHIVE_SAVE_AS = '{date:%Y}/{date:%m}/index.html'

# Tags and Category path
CATEGORY_URL = 'category/{slug}'
CATEGORY_SAVE_AS = 'category/{slug}/index.html'
CATEGORIES_SAVE_AS = 'catgegories.html'
TAG_URL = 'tag/{slug}'
TAG_SAVE_AS = 'tag/{slug}/index.html'
TAGS_SAVE_AS = 'tags.html'

AUTHOR_URL = 'author/{slug}'
AUTHOR_SAVE_AS = 'author/{slug}/index.html'
AUTHORS_SAVE_AS = 'authors.html'

STATIC_PATHS = ['assets']

JINJA_FILTERS = {'max': max}


# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True