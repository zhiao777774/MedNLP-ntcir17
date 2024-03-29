from pathlib import Path
import pandas as pd
import scrapy
import ast

DATA_FILE = "../data/preproc/preproc_en_train.csv"


class MedlinePlusSpider(scrapy.Spider):
    name = "MedlinePlus"

    def start_requests(self):

        df = pd.read_csv(DATA_FILE)
        drug_id = df['medline_plus_id'].tolist()

        drug_id_list = []
        urls = []

        for item in drug_id:

            l = ast.literal_eval(item)
            l = [item.strip() for item in l]

            for i in l:
                # print(i)
                if i == 'None':
                    continue
                drug_id_list.append(i)
            drug_id_list = list(set(drug_id_list))
            drug_id_list.sort()

        for i in drug_id_list:
            urls.append(f"https://medlineplus.gov/druginfo/meds/{i}.html")

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # get name only from xpath
        drug_name = response.xpath(
            '//*[@id="mplus-content"]/article/div[1]/div[1]/h1/text()').get()

        # get description only from xpath
        normal_description = response.xpath(
            '//*[@id="section-side-effects"]/ul[1]/li/text()').getall()
        serious_description = response.xpath(
            '//*[@id="section-side-effects"]/ul[2]/li/text()').getall()

        item = {
            drug_name: {
                'normal': normal_description,
                'serious': serious_description
            }
        }

        yield item

        # print(item)
        # drug_id = response.url.split("/")[-1][:-5]
        # filename = f"../data/crawler/MedlinePlus/MedlinePlus-{drug_id}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")