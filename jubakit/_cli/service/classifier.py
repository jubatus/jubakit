# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from jubatus.classifier.types import *

from .generic import GenericCLI
from ..args import Arguments, TDatum
from ..util import *

class ClassifierCLI(GenericCLI):
  @classmethod
  def _name(cls):
    return 'classifier'

  def _clear_cache(self):
    self._labels = set()

  @Arguments(str, TDatum)
  def do_train(self, label, d):
    """Syntax: train label datum_key datum_value [datum_key datum_value ...]
    Trains the model with given label and datum.
    Bulk training is not supported on the command line.
    """
    self._verbose("datum = {0}".format(d))
    result = self.client.train([LabeledDatum(label, d)])
    if result != 1:
      print("Failed")
    self._labels.add(label)

  def complete_train(self, text, line, begidx, endidx):
    pos = comp_position(text, line, begidx, endidx)
    if pos == 0:
      return filter_candidates(text, self._labels)

  @Arguments(TDatum)
  def do_classify(self, d):
    """Syntax: classify datum_key datum_value [datum_key datum_value ...]
    Classify the given datum.
    Bulk classification is not supported on the command line.
    """
    self._verbose("datum = {0}".format(d))
    results = self.client.classify([d])[0]
    results.sort(key=lambda e: e.score, reverse=True)
    for result in results:
      print("{0}: {1}".format(result.label, str(result.score)))
      self._labels.add(result.label)

  @Arguments()
  def do_get_labels(self):
    """Syntax: get_labels
    Prints the list of currently registered labels and number of instances trained for each label.
    """
    labels = self.client.get_labels()
    for (label, count) in labels.items():
      print('{0}: {1}'.format(label, count))
    self._labels = set(labels.keys())

  @Arguments(str)
  def do_set_label(self, label):
    """Syntax: set_label label
    Registers the new label without training.
    """
    result = self.client.set_label(label)
    if not result:
      print("Failed")
    self._labels.add(label)

  @Arguments(str)
  def do_delete_label(self, label):
    """Syntax: delete_label label
    Deletes the label.
    """
    result = self.client.delete_label(label)
    if not result:
      print("Failed")
    self._labels.discard(label)
