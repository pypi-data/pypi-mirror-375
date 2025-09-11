scikit-surgeryarucotracker
===============================

.. image:: https://github.com/SciKit-Surgery/scikit-surgeryarucotracker/raw/master/project-icon.gif
   :height: 128px
   :width: 128px
   :target: https://github.com/SciKit-Surgery/scikit-surgeryarucotracker
   :alt: Logo

|

.. image:: https://bestpractices.coreinfrastructure.org/projects/6116/badge
   :target: https://bestpractices.coreinfrastructure.org/projects/6116
   :alt: OpenSSF Best Practices

.. image:: https://github.com/SciKit-Surgery/scikit-surgeryarucotracker/workflows/.github/workflows/ci.yml/badge.svg
   :target: https://github.com/SciKit-Surgery/scikit-surgeryarucotracker/actions/
   :alt: GitHub CI test status

.. image:: https://coveralls.io/repos/github/SciKit-Surgery/scikit-surgeryarucotracker/badge.svg?branch=master&service=github 
    :target: https://coveralls.io/github/SciKit-Surgery/scikit-surgeryarucotracker?branch=master
    :alt: Test coverage

.. image:: https://readthedocs.org/projects/scikit-surgeryarucotracker/badge/?version=latest
    :target: http://scikit-surgeryarucotracker.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg
   :target: CODE_OF_CONDUCT.md

.. image:: https://img.shields.io/badge/Cite-SciKit--Surgery-informational
   :target: https://doi.org/10.1007/s11548-020-02180-5
   :alt: The SciKit-Surgery paper

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3971640.svg
   :target: https://doi.org/10.5281/zenodo.3971640
   :alt: Software DOI

.. image:: https://img.shields.io/twitter/follow/scikit_surgery?style=social
   :target: https://twitter.com/scikit_surgery?ref_src=twsrc%5Etfw
   :alt: Follow scikit_surgery on twitter

Author: Stephen Thompson

scikit-surgeryarucotracker provides a simple Python interface between OpenCV's ARuCo marker tracking libraries and other Python packages designed around scikit-surgerytrackers. It allows you to treat an object tracked using ARuCo markers in the same way as an object tracked using other tracking hardware (e.g. aruco - scikit-surgerynditracker). 

scikit-surgeryarucotracker is part of the `SciKit-Surgery`_ software project, developed at the `Wellcome EPSRC Centre for Interventional and Surgical Sciences`_, part of `University College London (UCL)`_.

scikit-surgeryarucotracker is tested with Python 3.6 and may support other Python versions.

.. features-start

.. features-end

Installing
----------

::

    pip install scikit-surgeryarucotracker

Using
-----
Configuration is done using Python libraries. Tracking data is returned in NumPy arrays.

::

    from sksurgeryarucotracker.arucotracker import ArUcoTracker
    config = {
        "video source" : 0
            }
    tracker = ArUcoTracker(config)

    tracker.start_tracking()
    print(tracker.get_frame())
    tracker.stop_tracking()
    tracker.close()

Developing
----------

Cloning
^^^^^^^

You can clone the repository using the following command:

::

    git clone https://github.com/SciKit-Surgery/scikit-surgeryarucotracker


Running the tests
^^^^^^^^^^^^^^^^^

You can run the unit tests by installing and running tox:

::

    pip install tox
    tox

Contributing
^^^^^^^^^^^^

Please see the `contributing guidelines`_.


Useful links
^^^^^^^^^^^^

* `Source code repository`_
* `Documentation`_


Licensing and copyright
-----------------------

Copyright 2019 University College London.
scikit-surgeryarucotracker is released under the BSD-3 license. Please see the `license file`_ for details.


Acknowledgements
----------------

Supported by `Wellcome`_ and `EPSRC`_.


.. _`Wellcome EPSRC Centre for Interventional and Surgical Sciences`: http://www.ucl.ac.uk/weiss
.. _`source code repository`: https://github.com/SciKit-Surgery/scikit-surgeryarucotracker
.. _`Documentation`: https://scikit-surgeryarucotracker.readthedocs.io
.. _`SciKit-Surgery`: https://github.com/UCL/scikit-surgery/wikis/home
.. _`University College London (UCL)`: http://www.ucl.ac.uk/
.. _`Wellcome`: https://wellcome.ac.uk/
.. _`EPSRC`: https://www.epsrc.ac.uk/
.. _`contributing guidelines`: https://github.com/SciKit-Surgery/scikit-surgeryarucotracker/blob/master/CONTRIBUTING.rst
.. _`license file`: https://github.com/SciKit-Surgery/scikit-surgeryarucotracker/blob/master/LICENSE

