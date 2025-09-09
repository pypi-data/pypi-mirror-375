"""
Data useful for empirical analysis of merger enforcement policy.

These data are processed for further analysis within relevant
submodules of the parent package. Thus, direct access is
unnecessary in routine use of this package.
"""

from importlib import resources

from .. import _PKG_NAME, VERSION  # noqa: TID252

__version__ = VERSION

data_resources = resources.files(f"{_PKG_NAME}.data")

DAMODARAN_MARGIN_DATA = data_resources / "damodaran_margin_data_serialized.zip"
"""
Included copy of Prof. Damodaran's margin data.

Use for replication/testing.

NOTES
-----
Source data are from Prof. Aswath Damodaran, Stern School of Business, NYU; available online
at https://pages.stern.nyu.edu/~adamodar/pc/datasets/margin.xls
and https://pages.stern.nyu.edu/~adamodar/pc/archives/margin*.xls.

Gross margins are reported in 2017 data and later.

Use as, for example:

.. code-block:: python

    import mergeron.data as mdat

    shutil.copy2(mdat.DAMODARAN_MARGIN_DATA, Path.home() / f"{DAMODARAN_MARGIN_DATA.name}")
"""

FTC_MERGER_INVESTIGATIONS_DATA = data_resources / "ftc_merger_investigations_data.zip"
"""
FTC merger investigations data published in 2004, 2007, 2008, and 2013

NOTES
-----
Raw data tables published by the FTC are loaded into a nested dictionary, organized by
data period, table type, and table number. Each table is stored as a numerical array
(:mod:`numpy` array), with additional attributes for the industry group and additional
evidence noted in the source data.

Data for additional data periods (time spans) not reported in the  source data,
e.g., 2004-2011, are constructed by subtracting counts in the base data from counts
in the cumulative data, by table, for "enforced" mergers and "closed" mergers, when
the cumulative data for the longer period are consistent with the base data for
a sub-period.
"""
