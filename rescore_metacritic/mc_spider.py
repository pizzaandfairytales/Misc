import scrapy
class McSpider(scrapy.Spider):
	name = "metacritic"
	start_urls = [
			"http://www.metacritic.com/browse/games/score/metascore/all/pc/filtered?view=condensed&sort=desc&page=0",
        ]
	def parse(self, response):
		for title in response.css('div.product_title'):
			yield {
					'name': title.css('a::text').extract()
				}
		next_page = response.css('span.next a::attr(href)').extract_first()
		if next_page is not None:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(next_page, callback = self.parse)
