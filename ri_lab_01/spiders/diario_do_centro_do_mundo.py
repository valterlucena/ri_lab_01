# -*- coding: utf-8 -*-
import scrapy
import json

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class DiarioDoCentroDoMundoSpider(scrapy.Spider):
    name = 'diario_do_centro_do_mundo'
    allowed_domains = ['diariodocentrodomundo.com.br']
    start_urls = []
    sections = []
    id = 0

    def __init__(self, *a, **kw):
        super(DiarioDoCentroDoMundoSpider, self).__init__(*a, **kw)
        with open('seeds/diario_do_centro_do_mundo.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())
        self.sections = [url.split('/')[-2] for url in list(data.values())]

    '''
        Function that finds and follows the url for the news at each section page
    '''
    def parse(self, response):
        for href in response.css('h3.entry-title > a::attr(href)').getall():
            yield response.follow(href, self.parse_news, meta={'url': response.url})
    
    '''
        Function that extracts and formats the scraped data
    '''
    def parse_news(self, response):

        '''
            Auxiliary function that returns the data from a single occurrence of the query args
        '''
        def extract_with_css(query):
            return response.css(query).get()
        
        '''
            Auxiliary function that returns the data from all occurrences of the query args
        '''
        def extract_with_css_all(query):
            return response.css(query).getall()

        '''
            Auxiliary function that returns an article's datetime
        '''
        def extract_date(query):
            extracted = extract_with_css(query).split('T')
            date = '/'.join(extracted[0].split('-')[::-1])
            time = extracted[-1].split('+')[0]
            return date + ' ' + time

        '''
            Auxiliary function that returns the article's section
        '''
        def extract_section():
            section = response.meta['url'].split('/')[-2]
            return section if section in self.sections else ''

        '''
            Auxiliary function that extracts and formats an article's text
        '''
        def extract_text(query):
            extracted = extract_with_css_all(query)
            return ' '.join(extracted)

        self.id += 1

        yield {
            'title': extract_with_css('h1.entry-title::text'),
            'subtitle': '',
            'author': extract_with_css('div.td-post-author-name > a::text'),
            'date': extract_date('time::attr(datetime)'),
            'section': extract_section(),
            'text': extract_text('.p1::text, .s1::text, div._2cuy::text, p:not(.donation_paragraph)::text'),
            'url': response.url
        }
        
        if self.id < 120:
            next_article = extract_with_css('.td-post-next-prev-content > a::attr(href)')
            yield response.follow(next_article, self.parse_news, meta={'url': response.url})
    