ChangeLog
====================================================

Release 0.6.2 - 2019/01/28
--------------------------

* New Features
    * Add Bandit service (#129, #131)
    * Add support for clear_row method of Recommender (#136, #137)

* Improvements
    * Add visualize example using TensorBoard (#131)

* Bug Fixes
    * Fix schema not working with service specialized column definition (#134, #135)
    * Fix Twitter Loader not working with latest tweepy (#138)

Release 0.6.1 - 2018/10/29
--------------------------

* New Features
    * Add postgresql loader (#125)
    * Add support for filtering API of Recommender (#126, #127)
* Bug Fixes
    * Fix ``classifier_kfold.py`` example not working with sklearn 0.20 or later (#128)

Release 0.6.0 (2018-08-27)
--------------------------

* New Features
    * Add Burst service (#94, #124)

Release 0.5.5 (2018-04-23)
---------------------------------------

* New Features
    * Add support for distance option of Clustering (#123)

* Documentation
    * Translate documents into Japanese (#104, #105, #108, #110, #111, #113-122)

Release 0.5.4 (2018-02-26)
---------------------------------------

* New Features
    * Add Nearest Neighbor service (#92, #103)
    * Add support for add_bulk of Anomaly (#106)

Release 0.5.3 (2017-12-18)
---------------------------------------

* New Features
    * Add Clustering service (#93, #98)

Release 0.5.2 (2017-10-30)
---------------------------------------

* Changes to Supported Systems
    * Deprecate  Python 2.6 support (#99, #100)


Release 0.5.1 (2017-08-28)
---------------------------------------

* New Features
    * Add ``--transform`` option to ``jubamodel`` command (#75, #83)

* Improvements
    * Fix library version for Python 2.6 (#88, #91)

Release 0.5.0 (2017-04-24)
---------------------------------------

* New Features
    * Add Regression service (#82, #87)
    * Add ``--replace-config`` / ``--replace-version`` options to ``jubamodel`` command (#76, #77)

* Improvements
    * Improve color of version number in docs (#80, #81)

* Bug Fixes
    * Fix CSVLoader not working with ``restkey`` option in Python 2 (#78, #79)

Release 0.4.2 (2017-02-27)
---------------------------------------

* New Features
    * Add scikit-learn wrapper (#73)

* Bug Fixes
    * Fix dead links in documents (#74)

Release 0.4.1 (2016-12-26)
---------------------------------------

* New Features
    * Support Embedded Jubatus (#70)

* Improvements
    * Implement ``__repr__`` method to base classes (#42, #71)
    * Add ``jubakit.model.JubaModel`` example (#68)
    * Add ``jubakit.model.JubaDump`` example (#69, #71)

* Bug Fixes
    * Fix document typos (#67)

Release 0.4.0 (2016-10-31)
---------------------------------------

* New Features
    * Add Recommender service (#52, #58)
    * Add model file manipulation tools (#4, #62)
    * Add ``ConcatLoader`` (#61)

* Improvements
    * Support Jubatus 1.0 (#66)
    * Improve Classifier Schema to accept columns without LABEL (#40, #57)
    * Improve handlign of bool-typed values (#9, #63)
    * Add option to apply Softmax to the resulting score in Classifier (#59)
    * Implement feature to enable logging by environment variable (#39, #65)
    * Improve RPC port allocation method (#44, #54)
    * Improve jubakit to work with non-standard Homebrew installations on macOS (#32, #35)
    * Update theme of docs (#60)

* Bug Fixes
    * Fix non-static Datasets does not allow automatic Schema prediction (#41, #64)
    * Fix error handling in ``jubash`` command (#55)
    * Fix error message when Jubatus servers are not installed on macOS (#56)

Release 0.3.0 (2016-08-29)
---------------------------------------

* New Features
    * Add Shell feature and ``jubash`` command (#38, #45, #51)

* Improvements
    * Add API reference and design documents (#33, #36, #43, #53)
    * Add ``from_data`` method to Classifier service (#46)

* Bug Fixes
    * Fix CSVLoader parameter handling (#34)
    * Fix typo in error message format (#49, #50)

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
    * Add support for ``cosine`` and ``euclidean`` method of Classifier (#27)
    * Improve default configuration of ``NN`` method of Classifier to use multiple CPU cores (#26)
    * Improve Anomaly service to validate invalid method name (#25)
    * Fix deprecated test warning in Python 3.5 (#24)

Release 0.2.0 (2016-05-30)
---------------------------------------

* New Features
    * Add support for Anomaly engine (#20)
    * Add support for Weight engine (#19)

* Improvements
    * Add logging system (#12, #17)
    * Add ``get_status`` API to Service (#15)
    * Add seed option to ``shuffle`` API to Dataset (#14)
    * Revise ``Loader`` API (#13)
    * ``Config.add_mecab`` API now accepts feature filters as list (#16)
    * Improve documentation (#11)
    * Add tests (#21)

* Bug Fixes
    * Fix missing records not ignored as expected (#22)
    * Fix ``get_label`` of Classifier service raise unexpected error when the dataset is not static (#21)
    * Fix ``LineBasedStreamLoader`` not closing file when iteration is terminated (#10)
    * Fix ``classifer_bulk.py`` example not using config object (#18)

Release 0.1.0 (2016-04-25)
---------------------------------------

Initial release.
