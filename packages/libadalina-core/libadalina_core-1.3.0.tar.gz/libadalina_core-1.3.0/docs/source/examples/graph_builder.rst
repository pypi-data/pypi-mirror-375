Build a graph from Open Street Map data
=======================================

This example demonstrates how to build a networkx graph from Open Street Map data using *libadalina-core* functionalities.

It reads a GeoDataFrame containing Open Street Map data and a
DataFrame representing a grid where each cell contains details about
the population living in that area.
Then, it constructs a graph representation of the road network where edges
are enriched with two attributes: the length of the road segment and the population living
within a specified distance from the road segment.

.. toctree::

   /_collections/notebooks/read_osm_graph.ipynb
