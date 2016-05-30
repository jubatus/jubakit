ChangeLog
====================================================

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
