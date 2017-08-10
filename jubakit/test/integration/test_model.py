# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase
import os
import json

from jubakit.model import JubaModel

from jubakit.anomaly import Anomaly, Config as AnomalyConfig
from jubakit.classifier import Classifier, Config as ClassifierConfig
from jubakit.recommender import Recommender, Config as RecommenderConfig
from jubakit.weight import Weight, Config as WeightConfig
from jubakit.dumb import Clustering, NearestNeighbor, Regression


class JubaModelTransformationTest(TestCase):
  def _get_model(self, service, config):
    # Create empty model for the given service.
    s = service.run(config)
    path = None
    try:
      s.save('test')
      path = s.get_status().popitem()[1]['last_saved_path']
      with open(path, 'rb') as f:
        return JubaModel.load_binary(f)
    finally:
      s.stop()
      if path and os.path.exists(path):
        os.remove(path)

  def _assertModelLoadable(self, service, model):
    config = json.loads(model.system.config)
    s = service.run(config)
    path = None
    try:
      s.save('test')
      path = s.get_status().popitem()[1]['last_saved_path']
      with open(path, 'wb') as f:
        model.dump_binary(f)
      s.load('test')
    finally:
      s.stop()
      if path and os.path.exists(path):
        os.remove(path)

  def test_from_classifier(self):
    model = self._get_model(Classifier, ClassifierConfig(method="NN"))

    self._assertModelLoadable(Classifier, model)
    self._assertModelLoadable(Weight, model.transform('weight'))
    self._assertModelLoadable(NearestNeighbor, model.transform('nearest_neighbor'))

  def test_from_regression(self):
    RegressionConfig = {
      "method": "NN",
      "parameter": {
        "method": "euclid_lsh",
        "parameter": {"hash_num": 64},
        "nearest_neighbor_num": 128
      },
      "converter": {
        "string_rules": [{"key":"*","type":"str","sample_weight":"bin","global_weight":"bin"}],
        "num_rules": [{"key":"*","type":"num"}]
      }
    }

    model = self._get_model(Regression, RegressionConfig)

    self._assertModelLoadable(Regression, model)
    self._assertModelLoadable(Weight, model.transform('weight'))
    self._assertModelLoadable(NearestNeighbor, model.transform('nearest_neighbor'))

  def test_from_recommender(self):
    model = self._get_model(Recommender, RecommenderConfig(method="nearest_neighbor_recommender"))

    self._assertModelLoadable(Recommender, model)
    self._assertModelLoadable(Weight, model.transform('weight'))
    self._assertModelLoadable(NearestNeighbor, model.transform('nearest_neighbor'))

  def test_from_anomaly_nn(self):
    model = self._get_model(Anomaly, AnomalyConfig(method="light_lof"))

    self._assertModelLoadable(Anomaly, model)
    self._assertModelLoadable(Weight, model.transform('weight'))
    self._assertModelLoadable(NearestNeighbor, model.transform('nearest_neighbor'))

  def test_from_anomaly_recommender(self):
    model = self._get_model(Anomaly, AnomalyConfig(method="lof"))

    self._assertModelLoadable(Anomaly, model)
    self._assertModelLoadable(Weight, model.transform('weight'))
    self._assertModelLoadable(Recommender, model.transform('recommender'))

  def test_from_clustering(self):
    model = self._get_model(Clustering, Clustering.CONFIG)

    self._assertModelLoadable(Clustering, model)
    self._assertModelLoadable(Weight, model.transform('weight'))
