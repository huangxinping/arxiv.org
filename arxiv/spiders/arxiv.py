from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as sle
from scrapy.selector import Selector
from arxiv.items import ArxivItem
from scrapy.exceptions import CloseSpider
from scrapy.http import Request, Response
import re
import datetime


def utc_str_to_local_str(utc_str: str, utc_format: str, local_format: str):
    utc_str = utc_str.strip()
    temp1 = datetime.datetime.strptime(utc_str, utc_format)
    temp2 = temp1.replace(tzinfo=datetime.timezone.utc)
    local_time = temp2.astimezone()
    return local_time.strftime(local_format)


class ArxivSpider(CrawlSpider):
    name = 'arxiv'
    allowed_domains = ['arxiv.org']

    start_urls = [
        'https://arxiv.org/list/cs/pastweek?skip=0&show=3000',  # Computer Science
        'https://arxiv.org/list/econ/pastweek?skip=0&show=3000',  # Economics
        'https://arxiv.org/list/eess/pastweek?skip=0&show=3000',  # Electrical Engineering and Systems Science
        'https://arxiv.org/list/stat/pastweek?skip=0&show=3000',  # Statistics
        'https://arxiv.org/list/q-fin/pastweek?skip=0&show=3000',  # Quantitative Finance
        'https://arxiv.org/list/q-bio/pastweek?skip=0&show=3000',  # Quantitative Biology
        'https://arxiv.org/list/math/pastweek?skip=0&show=3000',  # Mathematics
        'https://arxiv.org/list/astro-ph/pastweek?skip=0&show=3000',  # Physics - Astrophysics
        'https://arxiv.org/list/cond-mat/pastweek?skip=0&show=3000',  # Physics - Condensed Matter
        'https://arxiv.org/list/gr-qc/pastweek?skip=0&show=3000',  # Physics - General Relativity and Quantum Cosmology
        'https://arxiv.org/list/hep-ex/pastweek?skip=0&show=3000',  # Physics - High Energy Physics - Experiment
        'https://arxiv.org/list/hep-lat/pastweek?skip=0&show=3000',  # Physics - High Energy Physics - Lattice
        'https://arxiv.org/list/hep-ph/pastweek?skip=0&show=3000',  # Physics - High Energy Physics - Phenomenology
        'https://arxiv.org/list/hep-th/pastweek?skip=0&show=3000',  # Physics - High Energy Physics - Theory
        'https://arxiv.org/list/math-ph/pastweek?skip=0&show=3000',  # Physics - Mathematical Physics
        'https://arxiv.org/list/nlin/pastweek?skip=0&show=3000',  # Physics - Nonlinear Sciences
        'https://arxiv.org/list/nucl-ex/pastweek?skip=0&show=3000',  # Physics - Nuclear Experiment
        'https://arxiv.org/list/nucl-th/pastweek?skip=0&show=3000',  # Physics - Nuclear Theory
        'https://arxiv.org/list/physics/pastweek?skip=0&show=3000',  # Physics - Condensed Matter
        'https://arxiv.org/list/quant-ph/pastweek?skip=0&show=3000',  # Physics
    ]

    rules = [
        Rule(sle(allow=('abs/\d{1,4}\.\d{1,5}'
                        )), follow=True, callback='parse_item')
    ]

    def parse_item(self, response):
        item = ArxivItem()
        item['url'] = response.url.split('?')[0]
        item['attachment'] = response.url.split('?')[0].replace('abs', 'pdf') + '.pdf'

        title_xpath = "//h1[@class='title mathjax']/text()"
        title_selector = response.xpath(title_xpath).extract()
        if len(title_selector):
            title = title_selector[0]
            item['title'] = title

        authors_xpath = "//div[@class='authors']/a/text()"
        authors_selector = response.xpath(authors_xpath).extract()
        if len(authors_selector):
            authors = [author for author in authors_selector]
            item['authors'] = authors

        abstract_xpath = "//blockquote[@class='abstract mathjax']"
        abstract_selector = response.xpath(abstract_xpath).extract()
        if len(abstract_selector):
            abstract = abstract_selector[0]
            abstract = abstract.replace(
                '<blockquote class="abstract mathjax">\n      <span class="descriptor">Abstract:</span>  ', '')
            abstract = abstract.replace('\n\n    </blockquote>', '')
            abstract = abstract.replace('\n', '')
            item['abstract'] = abstract

        subjects_xpath = "//td[@class='tablecell subjects']"
        subjects_selector = response.xpath(subjects_xpath).extract()
        if len(subjects_selector):
            subjects = subjects_selector[0]
            subjects = subjects.replace('<td class="tablecell subjects">\n            ', '')
            subjects = subjects.replace(f'<span class="primary-subject">', '')
            subjects = subjects.replace(f'</span>', '')
            subjects = subjects.replace('</td>', '')
            subjects = subjects.split(';')
            subjects = list(map(lambda x: x.strip(), subjects))
            subject_fullnames = list(map(lambda x: re.search('.*\(', x).group(0).replace(' (', ''), subjects))
            subject_shortnames = list(map(lambda x: re.search('\(.*\)', x).group(0).replace('(', '').replace(')', ''), subjects))
            item['subjects'] = [{'name': fullname, 'short': shortname} for fullname, shortname in zip(subject_fullnames, subject_shortnames)]

        submission_history_xpath = "//div[@class='submission-history']"
        submission_history_selector = response.xpath(submission_history_xpath).extract()
        if len(submission_history_selector):
            submissions = []
            for submission_history in submission_history_selector:
                # submission author
                submission_author = (submission_history.split('[')[0]).split(':')[1].strip()

                # the page's submission time
                submission_time = ((submission_history.split('</strong>')[1]).split('(')[0]).replace('\n','').strip()

                # the page's submisstion attachment size
                submission_attachment_size = (submission_history.split('(')[1]).split(' KB')[0]

                # convert to true submission date
                utc_fmt = '%a, %d %b %Y %H:%M:%S UTC'
                # local_fmt = '%Y-%m-%d %H:%M:%S+08:00'
                local_fmt = '%Y-%m-%d'
                submission_local_date = utc_str_to_local_str(submission_time, utc_fmt, local_fmt)

                submissions.append({
                    'author': submission_author,
                    'date': submission_local_date,
                    'attachment_size': submission_attachment_size,
                })

            item['submissions'] = submissions
        # item['submissions'] = [] # fix the value because it is a bug.

        yield item
