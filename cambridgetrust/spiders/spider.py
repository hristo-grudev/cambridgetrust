import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import CambridgetrustItem
from itemloaders.processors import TakeFirst


class CambridgetrustSpider(scrapy.Spider):
	name = 'cambridgetrust'
	start_urls = ['https://ir.cambridgetrust.com/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246&LanguageId=1&bodyType=3&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1']

	def parse(self, response):
		data = json.loads(response.text)
		for post in data['GetPressReleaseListResult']:
			url = post['LinkToDetailPage']
			yield response.follow(url, self.parse_post)

		next_page = response.xpath('/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h2//text()[normalize-space()]').get()
		description = response.xpath('//div[@class="module_body"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//span[@class="module_date-text"]/text()').get()

		item = ItemLoader(item=CambridgetrustItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
