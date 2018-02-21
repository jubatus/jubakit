# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import sys
import warnings
from unittest import TestCase

from jubakit.nearest_neighbor import Schema, Dataset, NearestNeighbor, Config
from . import requireEmbedded
from .stub import StubLoader


def filter_warning():
    if sys.version_info > (3, 0):
        warnings.simplefilter("ignore", ResourceWarning)


class SchemaTest(TestCase):
    def test_simple(self):
        schema = Schema({
            'id': Schema.ID,
            'k1': Schema.STRING,
            'k2': Schema.NUMBER,
        })
        (row_id, d) = schema.transform(
            {'id': 'user001', 'k1': 'abc', 'k2': '123'})

        self.assertEqual(row_id, 'user001')
        self.assertEqual({'k1': 'abc'}, dict(d.string_values))
        self.assertEqual({'k2': 123}, dict(d.num_values))

    def test_illegal_id(self):
        # schema with multiple IDs
        self.assertRaises(RuntimeError, Schema, {
            'k1': Schema.ID,
            'k2': Schema.ID,
        })


class DatasetTest(TestCase):
    def test_predict(self):
        loader = StubLoader()
        dataset = Dataset(loader, None)  # predict
        self.assertEqual(['v', 1.0], dataset[0][1].num_values[0])


class NearestNeighborTest(TestCase):
    def test_simple(self):
        nearest_neighbor = NearestNeighbor()
        self.assertIsNotNone(nearest_neighbor)

    @requireEmbedded
    def test_embedded(self):
        nearest_neighbor = NearestNeighbor.run(Config(), embedded=True)
        self.assertIsNotNone(nearest_neighbor)

    def test_set_row(self):
        nearest_neighbor = NearestNeighbor.run(Config())
        loader = StubLoader()

        schema = Schema({'v': Schema.ID})
        dataset = Dataset(loader, schema)
        for (idx, row_id, result) in nearest_neighbor.set_row(dataset):
            self.assertEqual(result, True)
        nearest_neighbor.stop()

    def test_neighbor_row_from_id(self):
        filter_warning()
        nearest_neighbor = NearestNeighbor.run(Config())
        loader = StubLoader()

        schema = Schema({'v': Schema.ID})
        dataset = Dataset(loader, schema)
        for (_, _, d) in nearest_neighbor.neighbor_row_from_id(dataset):
            if len(d) != 0:
                self.assertEqual(0, len(d.string_values))
                self.assertEqual(0, len(d.num_values))
                self.assertEqual(0, len(d.binary_values))

        nearest_neighbor.stop()

    def test_neighbor_row_from_datum(self):
        filter_warning()
        nearest_neighbor = NearestNeighbor.run(Config())
        loader = StubLoader()

        schema = Schema({'v': Schema.ID})
        dataset = Dataset(loader, schema)
        for (_, _, d) in nearest_neighbor.neighbor_row_from_datum(dataset):
            if len(d) != 0:
                self.assertEqual(0, len(d.string_values))
                self.assertEqual(0, len(d.num_values))
                self.assertEqual(0, len(d.binary_values))

        schema = Schema({'v': Schema.NUMBER})
        dataset = Dataset(loader, schema)
        for (_, row_id, d) in \
                nearest_neighbor.neighbor_row_from_datum(dataset):
            if len(d) != 0:
                self.assertEqual(0, len(d.string_values))
                self.assertEqual(0, len(d.num_values))
                self.assertEqual(0, len(d.binary_values))

        nearest_neighbor.stop()

    def test_similar_row_from_id(self):
        filter_warning()
        nearest_neighbor = NearestNeighbor.run(Config())
        loader = StubLoader()

        schema = Schema({'v': Schema.ID})
        dataset = Dataset(loader, schema)
        for (idx, row_id, d) in nearest_neighbor.similar_row_from_id(dataset):
            if len(d) != 0:
                self.assertEqual(0, len(d.string_values))
                self.assertEqual(0, len(d.num_values))
                self.assertEqual(0, len(d.binary_values))

        nearest_neighbor.stop()

    def test_similar_row_from_datum(self):
        filter_warning()
        nearest_neighbor = NearestNeighbor.run(Config())
        loader = StubLoader()
        schema = Schema({'v': Schema.ID})
        dataset = Dataset(loader, schema)
        for (idx, row_id, result) in nearest_neighbor.similar_row_from_datum(
                dataset):
            self.assertEqual(0, len(result))

        schema = Schema({'v': Schema.NUMBER})
        dataset = Dataset(loader, schema)
        for (idx, row_id, result) in nearest_neighbor.similar_row_from_datum(
                dataset):
            # there is no similar row in column_table
            self.assertEqual(0, len(result))

        nearest_neighbor.stop()

    def test_get_all_rows(self):
        filter_warning()
        nearest_neighbor = NearestNeighbor.run(Config())
        loader = StubLoader()

        schema = Schema({'v': Schema.ID})
        dataset = Dataset(loader, schema)
        for _ in nearest_neighbor.set_row(dataset):
            pass
        ret = nearest_neighbor.get_all_rows()
        self.assertEqual(len(ret), len(dataset))

        nearest_neighbor.stop()


class ConfigTest(TestCase):
    def test_simple(self):
        config = Config()
        self.assertEqual('lsh', config['method'])

    def test_methods(self):
        config = Config()
        self.assertTrue(isinstance(config.methods(), list))

    def test_default(self):
        config = Config.default()
        self.assertEqual('lsh', config['method'])

    def test_method_param(self):
        self.assertTrue('hash_num' in Config(method='lsh')['parameter'])
        self.assertTrue('threads' in Config(method='lsh')['parameter'])

    def test_invalid_method(self):
        self.assertRaises(RuntimeError, Config._default_parameter,
                          'invalid_method')
