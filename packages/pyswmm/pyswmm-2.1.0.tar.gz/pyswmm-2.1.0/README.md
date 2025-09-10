<div align="center" style="max-width:500px;margin: auto;">
  <img src="https://raw.githubusercontent.com/pyswmm/pyswmm/master/docs/source/_static/type-logo-black.png"><br>
</div>


# python wrappers for the Stormwater Management Model (SWMM5)

[![Build Wheels](https://github.com/pyswmm/pyswmm/actions/workflows/python-package.yml/badge.svg)](https://github.com/pyswmm/pyswmm/actions/workflows/python-package.yml)
[![Documentation Status](https://github.com/pyswmm/pyswmm/actions/workflows/documentation.yml/badge.svg?branch=main)](http://docs.pyswmm.org/)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://python.org)
[![License](https://img.shields.io/pypi/l/pyswmm.svg)](LICENSE.txt)
[![Latest PyPI version](https://img.shields.io/pypi/v/pyswmm.svg)](https://pypi.python.org/pypi/pyswmm/)
[![PyPI Monthly Downloads](https://img.shields.io/badge/dynamic/json.svg?label=Downloads&url=https%3A%2F%2Fpypistats.org%2Fapi%2Fpackages%2Fpyswmm%2Frecent&query=%24.data.last_month&colorB=green&suffix=%20last%20month)](https://pypi.python.org/pypi/pyswmm/)
[![Cite our Paper](https://joss.theoj.org/papers/10.21105/joss.02292/status.svg)](https://doi.org/10.21105/joss.02292)
[![Discord](https://img.shields.io/badge/Discord-Join%20Chat-7289da?logo=discord&logoColor=white)](https://discord.gg/U8wqxgjt9C)

## Getting started

* Project Website: [www.pyswmm.org](https://www.pyswmm.org)

* [Official PySWMM Documentation](http://docs.pyswmm.org)

* [PySWMM YouTube Channel](https://www.youtube.com/channel/UCv-OYsz2moiMRzZIRhqbpHA/featured)


* [PySWMM Example Bundles](https://www.pyswmm.org/examples)

Introducing the SWAG STORE! All Proceeds go toward the hosting/service fees related to maintaining the PySWMM Project!!!  Get yourself a hoodie or coffee cup!


* [PySWMM SWAG Store](https://www.zazzle.com/store/pyswmm)

🆘Do you need HELP?🆘
> [GitHub Discussions](https://github.com/pyswmm/pyswmm/discussions)
> to answer support questions related to PySWMM.

Cite our Paper  
> McDonnell, Bryant E., Ratliff, Katherine M., Tryby, Michael E., Wu,
> Jennifer Jia Xin, & Mullapudi, Abhiram. (2020). PySWMM: The Python
> Interface to Stormwater Management Model (SWMM). *Journal of Open
> Source Software, 5*(52), 2292, <https://doi.org/10.21105/joss.02292>

# YouTube Training Videos

Setting a manhole inflow during a running simulation!  
> [![image](http://img.youtube.com/vi/i4AOHwKyvNw/0.jpg)](https://www.youtube.com/watch?v=i4AOHwKyvNw)

# Overview

PySWMM is a Python language software package for the creation,
manipulation, and study of the structure, dynamics, and function of
complex networks.

With PySWMM you can load and manipulate USEPA Stormwater Management
Models. With the development of PySWMM, control algorithms can now be
developed exclusively in Python which allows the use of functions and
objects as well as storing and tracking hydraulic trends for control
actions.

As of version v1.1.0, PySWMM includes new features to process metadata
and timeseries stored in SWMM binary output file.

# Who uses PySWMM?

PySWMM is used by engineers, modelers, and researchers who want to
streamline stormwater modeling optimization, controls, and
post-processing results.

# Goals

PySWMM is intended to provide

-   tools for the study of the structure and dynamics within USEPA
    SWMM5,
-   a standard programming interface and graph implementation that is
    suitable for many applications,
-   a rapid development environment for collaborative, multidisciplinary
    projects,
-   an interface to USEPA SWMM5,
-   development and implementation of control logic outside of native
    EPA-SWMM Controls,
-   methods for users to establish their own node inflows,
-   a coding interface to binary output files,
-   new modeling possibilities for the SWMM5 Community.

# Install

Get the latest version of PySWMM from
[PyPI](https://pypi.python.org/pypi/pyswmm/) See the [Quick
Guide](https://www.pyswmm.org/docs)!

```
$ pip install pyswmm
```
As of version 1.3.1, pyswmm can be installed with specific versions of the SWMM engine ranging from 5.1.14 to 5.2.4 using pip extras:

```
$ pip install pyswmm[swmm5.2.4]
```

# Usage

A quick example that steps through a simulation:

Examples:

See the [Latte Example](https://www.pyswmm.org/examples)

``` python
from pyswmm import Simulation, Nodes, Links

with Simulation(r'Example1.inp') as sim:
    Node21 = Nodes(sim)["21"]
    print("Invert Elevation: {}". format(Node21.invert_elevation))

    Link15 = Links(sim)['15']
    print("Outlet Node ID: {}".format(Link15.outlet_node))

    # Launch a simulation!
    for ind, step in enumerate(sim):
        if ind % 100 == 0:
            print(sim.current_time,",",round(sim.percent_complete*100),"%",\
                  Node21.depth, Link15.flow)
```

Opening a SWMM binary output file and accessing model metadata and
timeseries.

``` python
from pyswmm import Output, SubcatchSeries, NodeSeries, LinkSeries, SystemSeries

with Output('model.out') as out:
    print(len(out.subcatchments))
    print(len(out.nodes))
    print(len(out.links))
    print(out.version)

    sub_ts = SubcatchSeries(out)['S1'].runoff_rate
    node_ts = NodeSeries(out)['J1'].invert_depth
    link_ts = LinkSeries(out)['C2'].flow_rate
    sys_ts = SystemSeries(out).rainfall
```

# Contributing

Please check out our Wiki
<https://github.com/pyswmm/pyswmm/wiki> for more information
on contributing, including an Author Contribution Checklist.

# Bugs

Our issue tracker is at
<https://github.com/pyswmm/pyswmm/issues>. Please report any
bugs that you find. Or, even better, fork the repository on GitHub and
create a pull request. All changes are welcome, big or small, and we
will help you make the pull request if you are new to git (just ask on
the issue).

# License

Distributed with a BSD2 license; see LICENSE.txt:

    Copyright (C) 2014-2025 (See Authors)
    Community-Owned See AUTHORS and CITATION.cff

