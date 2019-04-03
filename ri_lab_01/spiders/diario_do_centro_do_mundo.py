# -*- coding: utf-8 -*-
import scrapy
import json

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class DiarioDoCentroDoMundoSpider(scrapy.Spider):
    name = 'diario_do_centro_do_mundo'
    allowed_domains = ['diariodocentrodomundo.com.br']
    start_urls = []

    def __init__(self, *a, **kw):
        super(DiarioDoCentroDoMundoSpider, self).__init__(*a, **kw)
        with open('seeds/diario_do_centro_do_mundo.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        for href in response.css('h3.entry-title > a::attr(href)').getall():
            yield response.follow(href, self.parse_news)
    
    def parse_news(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        title = extract_with_css('h1.entry-title::text')
        author = extract_with_css('div.td-post-author-name > a::text')
        date =  extract_with_css('time::attr(datetime)')
        text = response.css('.p1::text, p:not(.donation_paragraph)::text').getall()

        print('%s, %s, %s, \ntext:%s' % (title, author, date, text))
    