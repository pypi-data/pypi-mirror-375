"""
k-Full Tree (kFT) Algorithm for Geo-Referenced Time-Series Data Summarization

This package implements the k-Full Tree algorithm for spatio-temporal data analysis
using graph-based clustering and tree structures. The implementation follows the
methodology described in oliver2012.pdf.

Main Classes:
    STNode: Spatio-temporal node data structure
    STFullTree: Spatio-temporal full tree representation  
    GeoReferencedTimeSeries: GTS data structure with spatial-temporal graph
    KFullTree: Main algorithm implementation with Voronoi Partition Assignment (VPA)
"""

from .kft import (
    STNode,
    STFullTree,
    GeoReferencedTimeSeries,
    KFullTree
)

__version__ = "0.0.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "STNode",
    "STFullTree", 
    "GeoReferencedTimeSeries",
    "KFullTree"
]


def main():
    """Entry point for the kft command-line tool."""
    from .kft import main as kft_main
    kft_main()