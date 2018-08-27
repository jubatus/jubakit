# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Using Burst and CSV file
========================================

This is a simple example that illustrates:

* How to load CSV files and convert it into Jubakit dataset.
* Register keywords to the burst client using the keyword dataset.
* Add documents to the burst client using the document dataset.
* Getting burst result.
"""

from jubakit.burst import KeywordSchema, KeywordDataset
from jubakit.burst import DocumentSchema, DocumentDataset
from jubakit.burst import Burst, Config
from jubakit.loader.csv import CSVLoader

keyword_loader = CSVLoader('burst_keywords.csv')
keyword_schema = KeywordSchema({
    'keyword': KeywordSchema.KEYWORD,
    'scaling': KeywordSchema.SCALING,
    'gamma': KeywordSchema.GAMMA
})
keyword_dataset = KeywordDataset(keyword_loader, keyword_schema)

document_loader = CSVLoader('burst_documents.csv')
document_schema = DocumentSchema({
    'position': DocumentSchema.POSITION,
    'text': DocumentSchema.TEXT
})
document_dataset = DocumentDataset(document_loader, document_schema)

burst = Burst.run(Config())

for _ in burst.add_keyword(keyword_dataset): pass
for _ in burst.add_documents(document_dataset): pass

for result in burst.get_result('burst').batches:
    print(result)

burst.stop()
