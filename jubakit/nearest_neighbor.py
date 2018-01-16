# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import jubatus
import jubatus.embedded
import uuid

from .base import BaseDataset, BaseService, GenericConfig, GenericSchema
from .compat import unicode_t
from .loader.array import ArrayLoader, ZipArrayLoader
from .loader.chain import MergeChainLoader
from .loader.sparse import SparseMatrixLoader


class Schema(GenericSchema):
    """Schema for Nearest Neighbor service."""

    ID = 'i'

    def __init__(self, mapping, fallback=None):
        self._id_key = self._get_unique_mapping(mapping, fallback, self.ID,
                                                'ID', True)
        super(Schema, self).__init__(mapping, fallback)

    def transform(self, row):
        """Nearest Neighbor schema transforms the row into Datum,
        its associated ID.

        If row_id does not be set, assign uuid as row_id.
        """

        row_id = row.get(self._id_key, None)
        if row_id is not None:
            row_id = unicode_t(row_id)
        else:
            row_id = unicode_t(uuid.uuid4())
        d = self._transform_as_datum(row, None, [self._id_key])
        return row_id, d


class Dataset(BaseDataset):
    """Dataset for Nearest Neighbor service."""

    @classmethod
    def _predict(cls, row):
        return Schema.predict(row, False)

    @classmethod
    def _from_loader(cls, data_loader, ids, static):
        if ids is None:
            loader = data_loader
            schema = Schema({}, Schema.NUMBER)
        else:
            id_loader = ZipArrayLoader(_id=ids)
            loader = MergeChainLoader(data_loader, id_loader)
            schema = Schema({'_id': Schema.ID}, Schema.NUMBER)
        return Dataset(loader, schema, static)

    @classmethod
    def from_data(cls, data, ids=None, feature_names=None, static=True):
        """Converts two arrays or a sparse matrix data and its associated
        id array to Dataset.

        Parameters
        ----------
        data : array or scipy 2-D sparse matrix of shape
               [n_samples, n_features]
        ids : array of shape [n_samples], optional
        feature_names : array of shape [n_features], optional
        """

        if hasattr(data, 'todense'):
            return cls.from_matrix(data, ids, feature_names, static)
        else:
            return cls.from_array(data, ids, feature_names, static)

    @classmethod
    def from_array(cls, data, ids=None, feature_names=None, static=True):
        """Converts two arrays (data and its associated targets) to Dataset.

        Parameters
        ----------
        data : array of shape [n_samples, n_features]
        ids : array of shape [n_samples], optional
        feature_names : array of shape [n_features], optional
        """

        data_loader = ArrayLoader(data, feature_names)
        return cls._from_loader(data_loader, ids, static)

    @classmethod
    def from_matrix(cls, data, ids=None, feature_names=None, static=True):
        """Converts a sparse matrix data and its associated target array
        to Dataset.

        Parameters
        ----------

        data : scipy 2-D sparse matrix of shape [n_samples, n_features]
        ids : array of shape [n_samples], optional
        feature_names : array of shape [n_features], optional
        """

        data_loader = SparseMatrixLoader(data, feature_names)
        return cls._from_loader(data_loader, ids, static)

    def get_ids(self):
        """
        Returns labels of each record in the dataset.
        """

        if not self._static:
            raise RuntimeError('non-static datasets cannot fetch list of ids')
        for (idx, (row_id, d)) in self:
            yield row_id


class NearestNeighbor(BaseService):
    """Nearest Neighbor service."""

    @classmethod
    def name(cls):
        return 'nearest_neighbor'

    @classmethod
    def _client_class(cls):
        return jubatus.nearest_neighbor.client.NearestNeighbor

    @classmethod
    def _embedded_class(cls):
        return jubatus.embedded.NearestNeighbor

    def set_row(self, dataset):
        """Updates the row whose id is id with given row.
        If the row with the same id already exists, the row is overwritten with
        row (note that this behavior is different from that of recommender).
        Otherwise, new row entry will be created.
        If the server that manages the row and the server that received
        this RPC request are same, this operation is reflected instantly.
        If not, update operation is reflected after mix."""
        cli = self._client()
        for (idx, (row_id, d)) in dataset:
            if row_id is None:
                raise RuntimeError('dataset must have id.')
            result = cli.set_row(row_id, d)
            yield (idx, row_id, result)

    def neighbor_row_from_id(self, dataset, size=10):
        """Returns size rows (at maximum) that have most similar datum
        to id and their distance values."""
        cli = self._client()
        for (idx, (row_id, _)) in dataset:
            if row_id is None:
                raise RuntimeError('each data point must have its id.')
            result = cli.neighbor_row_from_id(row_id, size)
            yield (idx, row_id, result)

    def neighbor_row_from_datum(self, dataset, size=10):
        """Returns size rows (at maximum) of which datum are most similar to
        query and their distance values."""
        cli = self._client()
        for (idx, (row_id, d)) in dataset:
            if row_id is None:
                raise RuntimeError('each data point must have its id.')
            result = cli.neighbor_row_from_datum(d, size)
            yield (idx, row_id, result)

    def similar_row_from_id(self, dataset, size=10):
        """Returns ret_num rows (at maximum) that have most similar datum to id
        and their similarity values.
        """
        cli = self._client()
        for (idx, (row_id, _)) in dataset:
            if row_id is None:
                raise RuntimeError(
                    'Non ID-based datasets must use `similar_row_from_datum`')
            result = cli.similar_row_from_id(row_id, size)
            yield (idx, row_id, result)

    def similar_row_from_datum(self, dataset, size=10):
        """Returns ret_num rows (at maximum) of which datum are most similar
        to query and their similarity values.
        """
        cli = self._client()
        for (idx, (row_id, d)) in dataset:
            result = cli.similar_row_from_datum(d, size)
            yield (idx, row_id, result)

    def get_all_rows(self):
        """Returns the list of all row IDs."""
        cli = self._client()
        return cli.get_all_rows()


class Config(GenericConfig):
    """Configuration to run Nearest Neighbor service."""

    @classmethod
    def methods(cls):
        return ['lsh', 'minhash', 'euclid_lsh']

    @classmethod
    def _default_method(cls):
        return 'lsh'

    @classmethod
    def _default_parameter(cls, method):
        if method not in Config.methods():
            raise RuntimeError('unknown method: {0}'.format(method))
        return {
            'threads': 1,
            'hash_num': 128
        }
