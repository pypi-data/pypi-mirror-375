# k-Full Tree (kFT) Algorithm for Geo-Referenced Time-Series

A Python implementation of the k-Full Tree algorithm for summarizing geo-referenced time-series (GTS) data using spatio-temporal clustering and tree structures.

## Overview

This package implements the k-Full Tree algorithm, which provides efficient summarization of spatio-temporal data by identifying k representative tree structures that capture the most significant activity patterns across both space and time dimensions.

### Key Features

- **Spatio-Temporal Analysis**: Handles data with both spatial (geographic) and temporal (time-series) dimensions
- **Tree-Based Summarization**: Uses tree structures to represent activity patterns
- **Voronoi Partition Assignment (VPA)**: Advanced partitioning strategy for optimal node assignment
- **Flexible Configuration**: Configurable tree degree, number of summary trees (k), and algorithm parameters
- **Comprehensive Testing**: Full test suite with 31+ unit and integration tests

## Algorithm Description

The k-Full Tree algorithm operates in two main phases:

1. **Phase 1 - Voronoi Partition Assignment**: Assigns spatio-temporal nodes to k partitions based on distance to current summary trees
2. **Phase 2 - Summary Tree Update**: Recomputes optimal ST-full trees for each partition to maximize activity coverage

The algorithm iterates between these phases until convergence, producing k summary trees that best represent the underlying spatio-temporal patterns in the data.

## Installation

This project uses `uv` for dependency management. Make sure you have `uv` installed, then:

```bash
# Clone or navigate to the project directory
cd kft

# Install dependencies
uv sync
```

### Requirements

- Python >= 3.13
- NetworkX >= 3.5
- NumPy >= 2.3.2

## Usage

### Basic Example

```python
from kft import create_example_gts, KFullTree

# Create example geo-referenced time-series data
gts = create_example_gts()

# Initialize k-Full Tree algorithm
kft = KFullTree(gts, k=2, max_tree_degree=2)

# Run the algorithm
summary_trees, partitions = kft.fit(use_vpa=True, verbose=True)

# Analyze results
print(f"Found {len(summary_trees)} summary trees")
print(f"Total activity coverage: {kft.get_total_coverage()}")
```

### Advanced Usage

```python
from kft import GeoReferencedTimeSeries, KFullTree, STNode

# Create custom GTS data
spatial_framework = ['A', 'B', 'C', 'D']
temporal_framework = [1, 2, 3, 4]
spatial_neighbors = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'], 
    'D': ['B', 'C']
}
activity_data = {
    ('A', 1): 10, ('A', 2): 8, ('A', 3): 5, ('A', 4): 2,
    ('B', 1): 3, ('B', 2): 7, ('B', 3): 9, ('B', 4): 6,
    # ... more activity data
}

# Initialize GTS
gts = GeoReferencedTimeSeries(
    spatial_framework, 
    temporal_framework, 
    spatial_neighbors, 
    activity_data
)

# Configure and run algorithm
kft = KFullTree(gts, k=3, max_tree_degree=2)
trees, partitions = kft.fit(
    use_vpa=True,           # Use Voronoi Partition Assignment
    max_iterations=100,     # Maximum iterations
    verbose=True           # Show progress
)

# Access results
for i, tree in enumerate(trees):
    print(f"Tree {i}: {tree}")
    print(f"  Activity Coverage: {tree.activity_coverage()}")
    print(f"  Nodes: {[str(n) for n in tree.nodes]}")
```

## Data Structure

### Input Data Format

The algorithm expects:

- **Spatial Framework**: List of spatial region identifiers (e.g., `['A', 'B', 'C']`)
- **Temporal Framework**: List of time periods (e.g., `[1, 2, 3, 4]`)
- **Spatial Neighbors**: Dictionary mapping each region to its spatial neighbors
- **Activity Data**: Dictionary mapping (region, time) tuples to activity values

### Example Data Structure

```python
# Spatial regions
spatial_framework = ['Region1', 'Region2', 'Region3']

# Time periods
temporal_framework = [2020, 2021, 2022, 2023]

# Adjacency relationships
spatial_neighbors = {
    'Region1': ['Region2'],
    'Region2': ['Region1', 'Region3'],
    'Region3': ['Region2']
}

# Activity measurements
activity_data = {
    ('Region1', 2020): 15.5,
    ('Region1', 2021): 18.2,
    ('Region2', 2020): 12.1,
    # ... more measurements
}
```

## Running the Code

```bash
# Run the built-in example
uv run python kft.py

# Run the test suite
uv run python test_kft.py

# Run specific test categories
uv run python -m unittest test_kft.TestSTNode -v
uv run python -m unittest test_kft.TestKFullTree -v
```

## API Reference

### Core Classes

#### `STNode`
Represents a spatio-temporal node with spatial ID, time ID, and activity count.

#### `STFullTree` 
Represents a spatio-temporal full tree with root, nodes, edges, degree, and depth.

#### `GeoReferencedTimeSeries`
Container for GTS data that builds the spatio-temporal neighbor graph.

#### `KFullTree`
Main algorithm class that implements the k-Full Tree algorithm.

### Key Methods

- `KFullTree.fit(use_vpa=True, max_iterations=100, verbose=False)`: Run the complete algorithm
- `KFullTree.get_total_coverage()`: Get total activity coverage of summary trees
- `STFullTree.activity_coverage()`: Get activity coverage of a single tree
- `GeoReferencedTimeSeries.get_st_neighbors(node)`: Get spatio-temporal neighbors

## Testing

The package includes comprehensive tests covering:

- **Unit Tests**: Individual class and method testing
- **Integration Tests**: Complete algorithm execution
- **Edge Cases**: Empty partitions, single nodes, convergence scenarios
- **Phase-Specific Tests**: Detailed testing of both algorithm phases

Run all tests:
```bash
uv run python test_kft.py -v
```

## Academic Reference

This implementation is based on the k-Full Tree algorithm described in the academic paper included as `oliver2012.pdf`. The example data and methodology follow the research presented in that work.

## Development

### Project Structure

```
kft/
├── kft.py              # Main algorithm implementation
├── test_kft.py         # Comprehensive test suite
├── pyproject.toml      # Project configuration
├── CLAUDE.md           # Development guidance
├── oliver2012.pdf      # Reference paper
└── README.md           # This file
```

### Contributing

1. Ensure all tests pass: `uv run python test_kft.py`
2. Follow the existing code style and patterns
3. Add tests for new functionality
4. Update documentation as needed

## License

This implementation is provided for educational and research purposes. Please refer to the original academic paper for citation requirements.