ChangeLog
====================================================

Release 0.2.2 (2016-07-25)
---------------------------------------

* Improvements
    * Add hyper-parameter tuning example using hyperopt library (#28)
    * Fix warnings when using ``numpy`` record (#29)

* Bug Fixes
    * Fix log output from server not captured correctly (#30, #31)

Release 0.2.1 (2016-06-27)
---------------------------------------

* Improvements
    * Add support for `cosine` and `euclidean` method of Classifier (#27)
    * Improve default configuration of `NN` method of Classifier to use multiple CPU cores (#26)
    * Improve Anomaly service to validate invalid method name (#25)
    * Fix deprecated test warning in Python 3.5 (#24)

Release 0.2.0 (2016-05-30)
---------------------------------------

* New Features
    * Add support for Anomaly engine (#20)
    * Add support for Weight engine (#19)

* Improvements
    * Add logging system (#12, #17)
    * Add `get_status` API to Service (#15)
    * Add seed option to `shuffle` API to Dataset (#14)
    * Revise `Loader` API (#13)
    * `Config.add_mecab` API now accepts feature filters as list (#16)
    * Improve documentation (#11)
    * Add tests (#21)

* Bug Fixes
    * Fix missing records not ignored as expected (#22)
    * Fix `get_label` of Classifier service raise unexpected error when the dataset is not static (#21)
    * Fix `LineBasedStreamLoader` not closing file when iteration is terminated (#10)
    * Fix `classifer_bulk.py` example not using config object (#18)

Release 0.1.0 (2016-04-25)
---------------------------------------

Initial release.
