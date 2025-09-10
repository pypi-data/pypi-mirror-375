##########
pyHeimdall
##########

.. image:: https://gitlab.huma-num.fr/datasphere/doc/assets/-/raw/main/banners/HEIMDALL.png
   :target: https://datasphere.readthedocs.io/projects/heimdall/en/latest/
   :width: 100%
   :align: center

.. image:: https://img.shields.io/badge/license-AGPL3.0-informational?logo=gnu&color=success
   :target: https://www.gnu.org/licenses/agpl-3.0.html
   :alt: License
.. image:: https://www.repostatus.org/badges/latest/active.svg
   :target: https://www.repostatus.org/#project-statuses
   :alt: Project status
.. image:: https://img.shields.io/pypi/v/pyheimdall
   :target: https://pypi.org/project/pyheimdall/
   :alt: PyPI - Python Version
.. image:: https://gitlab.huma-num.fr/datasphere/heimdall/python/-/badges/release.svg
   :target: https://gitlab.huma-num.fr/datasphere/heimdall/python/-/releases
   :alt: GitLab - Latest release
.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.12795206.svg
   :target: https://doi.org/10.5281/zenodo.12795206
   :alt: Digital Object Identifier (DOI)
.. image:: https://img.shields.io/badge/documentation-api-green
   :target: https://datasphere.gitpages.huma-num.fr/heimdall/python/doc/
   :alt: API Documentation

.. image:: https://gitlab.huma-num.fr/datasphere/heimdall/python/badges/main/pipeline.svg
   :target: https://gitlab.huma-num.fr/datasphere/heimdall/python/pipelines/latest
   :alt: Build status
.. image:: https://gitlab.huma-num.fr/datasphere/heimdall/python/badges/main/coverage.svg
   :target: https://datasphere.gitpages.huma-num.fr/heimdall/python/coverage/index.html
   :alt: Code coverage
.. image:: https://www.bestpractices.dev/badge_static/passing
   :target: https://www.bestpractices.dev/en/projects/9841
   :alt: Open Source Security Foundation (OpenSSF) best practices badge

*************
What is this?
*************

Heimdall is a tool for converting more easily one or more databases from one format to another.



********************
Why should I use it?
********************

If, for example, you find yourself in one of the following situations...

- you need access to data, but it is not stored in a format compatible with your favorite software...
- you'd prefer to merge several heterogeneous databases into a single corpus, easier to analyze...
- you're considering which input format to use for your software or database...
- you want to make your data more accessible and interoperable...

... then Heimdall can offer you an exchange format, and abstract the details of data implementation: yours, but also those of others.

Thanks to Heimdall, you can also switch from one technology to another in a matter of moments, as and when you need to, without ever losing, disorganizing or corrupting your data.

In a nutshell, **HEIMDALL** is your **H**\ igh **E**\ nd **I**\ nteroperability **M**\ odule when **D**\ ata is **ALL** over the place.
It's a bridge between scattered islands of data.



*****************
How can I use it?
*****************

Setup
=====

You can install Heimdall using the `pip <https://pip.pypa.io/en/stable/>`_ package manager:

.. code-block:: bash

   pip install pyheimdall

You can use `pip <https://pip.pypa.io/en/stable/>`_ to either upgrade or uninstall Heimdall, too:

.. code-block:: bash

   pip install --upgrade pyheimdall
   pip uninstall pyheimdall

Usage
=====

.. code-block:: python

   import heimdall

   config = {
       'format': 'sql:mysql',
       'url': 'mysql://user:password@localhost:3306/database',
   }
   tree = heimdall.getDatabase(**config)



*****************
Is it documented?
*****************

Sure!
You can read the `user manual here <https://datasphere.readthedocs.io/projects/heimdall/en/latest/python/>`_,
or jump directly to the `technical reference here <https://datasphere.gitpages.huma-num.fr/heimdall/python/doc/>`_.
You can use Python's build-in ``help`` function, too.



*************
Is it tested?
*************

Of course!
Here's `the coverage report <https://datasphere.gitpages.huma-num.fr/heimdall/python/coverage/index.html>`_.

You can run all tests on your machine, too.
After having cloned this repository, enter it, setup your dev environment, and then:

.. code-block:: bash

   pytest



*********************
How can I contribute?
*********************

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


*******
License
*******

`GNU Affero General Public License version 3.0 or later <https://choosealicense.com/licenses/agpl/>`_


***************
Acknowledgments
***************

Heimdall would like to thank all its contributors and users for their support and feedback. ʕᵔᴥᵔʔ

.. list-table::
   :widths: 1 1 1 1

   * - .. image:: https://gitlab.huma-num.fr/uploads/-/system/user/avatar/728/avatar.png?width=128
         :alt: rwitz

       | `rwitz <https://gitlab.huma-num.fr/rwitz>`_ 💡💻✅📝
     - .. image:: https://gitlab.huma-num.fr/uploads/-/system/user/avatar/1955/avatar.png?width=128
         :alt: emichelet

       | `emichelet <https://gitlab.huma-num.fr/emichelet>`_ 💻💡
     - .. image:: https://gitlab.huma-num.fr/uploads/-/system/user/avatar/2064/avatar.png?width=128
         :alt: abrody

       | `abrody <https://gitlab.huma-num.fr/abrody>`_ 💻
     - .. image:: https://gitlab.huma-num.fr/uploads/-/system/user/avatar/1682/avatar.png?width=128
         :alt: evankote

       | `evankote <https://gitlab.huma-num.fr/evankote>`_ 📝✅
   * - .. image:: https://gitlab.huma-num.fr/uploads/-/system/user/avatar/727/avatar.png?width=128
         :alt: mbenkhalid

       | `mbenkhalid <https://gitlab.huma-num.fr/mbenkhalid>`_ 💻
     - .. image:: https://gitlab.huma-num.fr/uploads/-/system/user/avatar/535/avatar.png?width=128
         :alt: mariebizaislillig

       | `mariebizaislillig <https://gitlab.huma-num.fr/mariebizaislillig>`_ 💡✅
     - .. image:: https://gitlab.huma-num.fr/uploads/-/system/user/avatar/263/avatar.png?width=128
         :alt: gporte

       | `gporte <https://gitlab.huma-num.fr/gporte>`_ 💡✅
     - .. image:: https://gitlab.huma-num.fr/uploads/-/system/user/avatar/107/avatar.png?width=128
         :alt: cplancq

       | `cplancq <https://gitlab.huma-num.fr/cplancq>`_ 🐛✅
   * - .. image:: https://gitlab.huma-num.fr/uploads/-/system/user/avatar/2058/avatar.png?width=128
         :alt: tbrissetsabouraud

       | `tbrissetsabouraud <https://gitlab.huma-num.fr/tbrissetsabouraud>`_ 💻
     -
     -
     -
