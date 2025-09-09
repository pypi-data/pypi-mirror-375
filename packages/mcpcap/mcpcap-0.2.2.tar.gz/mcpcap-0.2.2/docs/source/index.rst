mcpcap Documentation
======================

.. image:: https://img.shields.io/pypi/v/mcpcap.svg
   :target: https://pypi.org/project/mcpcap/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/mcpcap.svg
   :target: https://pypi.org/project/mcpcap/
   :alt: Python versions

.. image:: https://github.com/danohn/mcpcap/workflows/Test/badge.svg
   :target: https://github.com/danohn/mcpcap/actions
   :alt: Test status

A modular Python MCP (Model Context Protocol) Server for analyzing PCAP files. mcpcap enables LLMs to read and analyze network packet captures from local or remote sources, providing structured JSON responses about network traffic.

Features
--------

✅ **Modular Architecture**: Easily extensible to support new protocols

✅ **DNS Analysis**: Comprehensive DNS packet parsing and analysis

✅ **Robust Error Handling**: Gracefully handles malformed packets

✅ **MCP Integration**: Seamless integration with LLM clients

✅ **Security Focus**: Built-in security analysis prompts and indicators

✅ **Real-world Ready**: Tested with actual network captures

Quick Start
-----------

Install mcpcap:

.. code-block:: bash

   pip install mcpcap

Start the MCP server:

.. code-block:: bash

   mcpcap --pcap-path /path/to/pcap/files

Then connect with your favorite MCP client to analyze DNS traffic!

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user-guide/installation
   user-guide/quickstart
   user-guide/mcp-integration
   user-guide/analysis-guides

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/modules
   api/cli

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide
   :hidden:

.. toctree::
   :maxdepth: 1
   :caption: Examples
   :hidden:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`