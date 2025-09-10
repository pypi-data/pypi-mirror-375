import numpy as np
import networkx as nx
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import random
from itertools import combinations
import heapq

@dataclass
class STNode:
    """Spatio-temporal node"""
    spatial_id: str
    time_id: int
    activity_count: float
    
    def __hash__(self):
        return hash((self.spatial_id, self.time_id))
    
    def __eq__(self, other):
        return self.spatial_id == other.spatial_id and self.time_id == other.time_id
    
    def __lt__(self, other):
        # For heapq comparison - compare by (time_id, spatial_id)
        return (self.time_id, self.spatial_id) < (other.time_id, other.spatial_id)
    
    def __repr__(self):
        return f"{self.spatial_id}{self.time_id}"

@dataclass
class STFullTree:
    """Spatio-temporal full tree"""
    root: STNode
    nodes: Set[STNode]
    edges: Set[Tuple[STNode, STNode]]  # Store actual tree edges
    degree: int
    depth: int
    
    def activity_coverage(self) -> float:
        """Calculate total activity coverage of the tree"""
        return sum(node.activity_count for node in self.nodes)
    
    def contains_node(self, node: STNode) -> bool:
        """Check if node is in this tree"""
        return node in self.nodes
    
    def __repr__(self):
        return f"Tree(root={self.root}, nodes={len(self.nodes)}, AC={self.activity_coverage():.1f})"

class GeoReferencedTimeSeries:
    """Geo-referenced time-series data structure"""
    
    def __init__(self, spatial_framework: List[str], temporal_framework: List[int],
                 spatial_neighbors: Dict[str, List[str]], activity_data: Dict[Tuple[str, int], float]):
        """
        Initialize GTS
        
        Args:
            spatial_framework: List of spatial region IDs (e.g., ['A', 'B', 'C'])
            temporal_framework: List of time periods (e.g., [1, 2, 3])
            spatial_neighbors: Dict mapping region to its neighbors
            activity_data: Dict mapping (region, time) to activity count
        """
        self.spatial_framework = spatial_framework
        self.temporal_framework = temporal_framework
        self.spatial_neighbors = spatial_neighbors
        self.activity_data = activity_data
        
        # Create ST nodes
        self.st_nodes = {}
        for s in spatial_framework:
            for t in temporal_framework:
                node = STNode(s, t, activity_data.get((s, t), 0))
                self.st_nodes[(s, t)] = node
        
        # Build ST neighbor graph
        self.st_graph = nx.DiGraph()
        self._build_st_graph()
    
    def _build_st_graph(self):
        """Build spatio-temporal directed neighbor graph"""
        # Add all nodes first
        for node in self.st_nodes.values():
            self.st_graph.add_node(node)
        
        # Add directed edges based on spatio-temporal neighbor relationship
        for s in self.spatial_framework:
            for t_idx, t in enumerate(self.temporal_framework[:-1]):
                current_node = self.st_nodes[(s, t)]
                next_t = self.temporal_framework[t_idx + 1]
                
                # Add temporal neighbors (including self and spatial neighbors)
                for neighbor_s in [s] + self.spatial_neighbors.get(s, []):
                    if (neighbor_s, next_t) in self.st_nodes:
                        neighbor_node = self.st_nodes[(neighbor_s, next_t)]
                        self.st_graph.add_edge(current_node, neighbor_node)
    
    def get_st_neighbors(self, node: STNode) -> List[STNode]:
        """Get spatio-temporal neighbors of a node (successors in the graph)"""
        if node in self.st_graph:
            return list(self.st_graph.successors(node))
        return []

class KFullTree:
    """k-Full Tree Algorithm for GTS Summarization"""
    
    def __init__(self, gts: GeoReferencedTimeSeries, k: int, max_tree_degree: int = 3):
        """
        Initialize kFT algorithm
        
        Args:
            gts: Geo-referenced time-series data
            k: Number of summary trees to find
            max_tree_degree: Maximum degree for full trees
        """
        self.gts = gts
        self.k = k
        self.max_tree_degree = max_tree_degree
        self.summary_trees = []
        self.partitions = defaultdict(set)
        self.node_assignments = {}  # Track which tree each node belongs to
    
    def _build_full_tree_recursive(self, root: STNode, degree: int, 
                                  max_depth: int, used_nodes: Set[STNode]) -> List[STFullTree]:
        """
        Build all possible full trees from root following ST-neighbor relationships.
        Returns list of valid ST-full trees.
        """
        trees = []
        
        def build_tree_bfs(root: STNode) -> List[STFullTree]:
            """Use BFS to build all possible full trees of given degree"""
            result_trees = []
            
            # Queue stores: (current_tree_nodes, current_tree_edges, current_level_nodes)
            initial_state = ({root}, set(), [root])
            queue = deque([initial_state])
            
            while queue:
                tree_nodes, tree_edges, level_nodes = queue.popleft()
                
                # Check if we've reached max depth
                current_depth = max(n.time_id for n in tree_nodes) - root.time_id
                if current_depth >= max_depth:
                    # Create tree with current nodes
                    if len(tree_nodes) > 1:
                        result_trees.append(STFullTree(root, tree_nodes, tree_edges, degree, current_depth))
                    continue
                
                # Find all possible children for current level
                all_children = set()
                for parent in level_nodes:
                    children = self.gts.get_st_neighbors(parent)
                    for child in children:
                        if child not in used_nodes and child not in tree_nodes:
                            all_children.add(child)
                
                # If we can't find enough children for a full tree, save current tree
                if len(all_children) < degree * len(level_nodes):
                    if len(tree_nodes) > 1:
                        result_trees.append(STFullTree(root, tree_nodes, tree_edges, degree, current_depth))
                    continue
                
                # Generate all valid combinations of children
                # Each node in level_nodes needs exactly 'degree' children
                valid_assignments = self._find_valid_child_assignments(
                    level_nodes, all_children, degree
                )
                
                for assignment in valid_assignments[:10]:  # Limit combinations to avoid explosion
                    new_nodes = tree_nodes.copy()
                    new_edges = tree_edges.copy()
                    new_level = []
                    
                    for parent, children in assignment.items():
                        for child in children:
                            new_nodes.add(child)
                            new_edges.add((parent, child))
                            new_level.append(child)
                    
                    queue.append((new_nodes, new_edges, new_level))
            
            return result_trees
        
        # Build trees starting from root
        trees = build_tree_bfs(root)
        
        # Filter to keep only valid full trees
        valid_trees = []
        for tree in trees:
            if self._is_valid_full_tree(tree, degree):
                valid_trees.append(tree)
        
        return valid_trees
    
    def _find_valid_child_assignments(self, parents: List[STNode], 
                                     available_children: Set[STNode], 
                                     degree: int) -> List[Dict[STNode, List[STNode]]]:
        """
        Find valid assignments of children to parents where each parent gets exactly 'degree' children.
        Returns list of assignment dictionaries.
        """
        assignments = []
        
        # Build parent-child possibility matrix
        parent_children_map = {}
        for parent in parents:
            possible_children = []
            for child in available_children:
                if self.gts.st_graph.has_edge(parent, child):
                    possible_children.append(child)
            parent_children_map[parent] = possible_children
        
        # Check if assignment is possible
        for parent, children in parent_children_map.items():
            if len(children) < degree:
                return []  # Cannot create full tree
        
        # Generate assignments (simplified - just take first valid combination)
        assignment = {}
        used_children = set()
        
        for parent in parents:
            available = [c for c in parent_children_map[parent] if c not in used_children]
            if len(available) >= degree:
                selected = available[:degree]
                assignment[parent] = selected
                used_children.update(selected)
            else:
                return []  # Cannot complete assignment
        
        if assignment:
            assignments.append(assignment)
        
        return assignments
    
    def _is_valid_full_tree(self, tree: STFullTree, expected_degree: int) -> bool:
        """
        Verify if tree is a valid ST-full tree:
        - All non-leaf nodes have exactly 'degree' children
        - All leaves are at the same depth
        - Follows ST-neighbor relationships
        """
        if not tree.edges:
            return len(tree.nodes) == 1  # Single node is valid
        
        # Build adjacency lists
        children_map = defaultdict(list)
        parent_map = {}
        
        for parent, child in tree.edges:
            children_map[parent].append(child)
            parent_map[child] = parent
        
        # Check root
        if tree.root in parent_map:
            return False  # Root should not have parent
        
        # Find leaves (nodes with no children)
        leaves = [n for n in tree.nodes if n not in children_map]
        
        if not leaves:
            return False
        
        # Check all leaves are at same depth
        leaf_depths = [n.time_id - tree.root.time_id for n in leaves]
        if len(set(leaf_depths)) > 1:
            return False
        
        # Check all non-leaf nodes have exactly 'degree' children
        for node in tree.nodes:
            if node not in leaves:  # Non-leaf node
                if len(children_map.get(node, [])) != expected_degree:
                    return False
        
        return True
    
    def _select_initial_seeds(self) -> List[STFullTree]:
        """Randomly select k initial summary trees"""
        initial_trees = []
        used_nodes = set()
        
        # Get all nodes that can be roots (earliest time nodes)
        min_time = min(self.gts.temporal_framework)
        potential_roots = [n for n in self.gts.st_nodes.values() 
                          if n.time_id == min_time and n not in used_nodes]
        
        attempts = 0
        max_attempts = len(potential_roots) * 2
        
        while len(initial_trees) < self.k and potential_roots and attempts < max_attempts:
            attempts += 1
            
            # Randomly select a root
            root = random.choice(potential_roots)
            
            # Try to build a tree from this root
            max_depth = len(self.gts.temporal_framework) - 1
            possible_trees = self._build_full_tree_recursive(
                root, self.max_tree_degree, max_depth, used_nodes
            )
            
            if possible_trees:
                # Select tree with maximum coverage
                best_tree = max(possible_trees, key=lambda t: t.activity_coverage())
                initial_trees.append(best_tree)
                used_nodes.update(best_tree.nodes)
                potential_roots = [n for n in potential_roots if n not in used_nodes]
        
        # If we couldn't find k trees, create single-node trees
        while len(initial_trees) < self.k:
            remaining_nodes = [n for n in self.gts.st_nodes.values() if n not in used_nodes]
            if not remaining_nodes:
                break
            
            node = random.choice(remaining_nodes)
            single_tree = STFullTree(node, {node}, set(), self.max_tree_degree, 0)
            initial_trees.append(single_tree)
            used_nodes.add(node)
        
        return initial_trees
    
    def _distance(self, node: STNode, tree: STFullTree) -> float:
        """Calculate distance from node to tree (minimum distance to any tree node)"""
        if not tree.nodes:
            return float('inf')
        
        min_dist = float('inf')
        for tree_node in tree.nodes:
            try:
                # Use shortest path length in undirected version of ST graph
                dist = nx.shortest_path_length(
                    self.gts.st_graph.to_undirected(), 
                    node, tree_node
                )
                min_dist = min(min_dist, dist)
            except nx.NetworkXNoPath:
                continue
        
        return min_dist
    
    def _assign_nodes_vpa(self):
        """Phase 1: Assign nodes using Voronoi Partition Assignment"""
        self.partitions = defaultdict(set)
        self.node_assignments = {}
        
        # Create virtual graph with virtual node connected to all tree nodes
        virtual_graph = self.gts.st_graph.to_undirected().copy()
        virtual_node = STNode("VIRTUAL", -1, 0)
        
        # Add edges from virtual node to all nodes in summary trees with tree info
        for tree_idx, tree in enumerate(self.summary_trees):
            for node in tree.nodes:
                virtual_graph.add_edge(virtual_node, node, tree_id=tree_idx)
        
        # Use Dijkstra-like approach for assignment
        distances = {node: float('inf') for node in self.gts.st_nodes.values()}
        tree_assignments = {}
        
        # Priority queue: (distance, node, tree_idx)
        pq = []
        
        # Initialize with tree nodes
        for tree_idx, tree in enumerate(self.summary_trees):
            for node in tree.nodes:
                distances[node] = 0
                tree_assignments[node] = tree_idx
                heapq.heappush(pq, (0, node, tree_idx))
        
        # Propagate assignments
        while pq:
            dist, current, tree_idx = heapq.heappop(pq)
            
            if current in virtual_graph:
                for neighbor in virtual_graph.neighbors(current):
                    if neighbor != virtual_node:
                        new_dist = dist + 1
                        if new_dist < distances.get(neighbor, float('inf')):
                            distances[neighbor] = new_dist
                            tree_assignments[neighbor] = tree_idx
                            heapq.heappush(pq, (new_dist, neighbor, tree_idx))
        
        # Build partitions from assignments
        for node, tree_idx in tree_assignments.items():
            self.partitions[tree_idx].add(node)
            self.node_assignments[node] = tree_idx
    
    def _update_summary_trees(self):
        """Phase 2: Recompute summary tree for each partition"""
        new_trees = []
        
        for partition_idx in range(self.k):
            partition_nodes = self.partitions.get(partition_idx, set())
            
            if not partition_nodes:
                # Keep existing tree if partition is empty
                if partition_idx < len(self.summary_trees):
                    new_trees.append(self.summary_trees[partition_idx])
                continue
            
            # Find best valid ST-full tree in partition
            best_tree = None
            best_coverage = -1
            
            # Try each node in partition as potential root
            # Focus on nodes that can be roots (earliest time in partition)
            min_time_in_partition = min(n.time_id for n in partition_nodes)
            potential_roots = [n for n in partition_nodes if n.time_id == min_time_in_partition]
            
            for root in potential_roots:
                # Build full trees from this root using only partition nodes
                max_depth = max(n.time_id for n in partition_nodes) - root.time_id
                
                # Get nodes already assigned to other trees
                used_nodes = set()
                for other_idx in range(self.k):
                    if other_idx != partition_idx and other_idx < len(new_trees):
                        used_nodes.update(new_trees[other_idx].nodes)
                
                # Build trees considering partition constraint
                possible_trees = self._build_full_tree_within_partition(
                    root, self.max_tree_degree, max_depth, partition_nodes, used_nodes
                )
                
                for tree in possible_trees:
                    coverage = tree.activity_coverage()
                    if coverage > best_coverage:
                        best_coverage = coverage
                        best_tree = tree
            
            # If no valid full tree found, keep previous or create single-node tree
            if best_tree:
                new_trees.append(best_tree)
            elif partition_idx < len(self.summary_trees):
                new_trees.append(self.summary_trees[partition_idx])
            elif partition_nodes:
                # Create single-node tree from node with highest activity
                best_node = max(partition_nodes, key=lambda n: n.activity_count)
                new_trees.append(STFullTree(best_node, {best_node}, set(), self.max_tree_degree, 0))
        
        self.summary_trees = new_trees[:self.k]
    
    def _build_full_tree_within_partition(self, root: STNode, degree: int, 
                                         max_depth: int, partition_nodes: Set[STNode],
                                         used_nodes: Set[STNode]) -> List[STFullTree]:
        """Build full trees using only nodes from the partition"""
        trees = []
        
        # Similar to _build_full_tree_recursive but constrained to partition
        queue = deque([({root}, set(), [root])])
        
        while queue:
            tree_nodes, tree_edges, level_nodes = queue.popleft()
            
            current_depth = max(n.time_id for n in tree_nodes) - root.time_id
            if current_depth >= max_depth:
                if len(tree_nodes) > 1:
                    trees.append(STFullTree(root, tree_nodes, tree_edges, degree, current_depth))
                continue
            
            # Find children within partition
            all_children = set()
            for parent in level_nodes:
                children = self.gts.get_st_neighbors(parent)
                for child in children:
                    if (child in partition_nodes and 
                        child not in used_nodes and 
                        child not in tree_nodes):
                        all_children.add(child)
            
            if len(all_children) < degree * len(level_nodes):
                if len(tree_nodes) > 1:
                    trees.append(STFullTree(root, tree_nodes, tree_edges, degree, current_depth))
                continue
            
            # Simplified: just take first valid assignment
            assignment = self._find_valid_child_assignments(level_nodes, all_children, degree)
            
            for assign in assignment[:5]:  # Limit to avoid explosion
                new_nodes = tree_nodes.copy()
                new_edges = tree_edges.copy()
                new_level = []
                
                for parent, children in assign.items():
                    for child in children:
                        new_nodes.add(child)
                        new_edges.add((parent, child))
                        new_level.append(child)
                
                queue.append((new_nodes, new_edges, new_level))
        
        return trees
    
    def fit(self, use_vpa: bool = True, max_iterations: int = 100, verbose: bool = False):
        """
        Run kFT algorithm
        
        Args:
            use_vpa: Whether to use Voronoi Partition Assignment
            max_iterations: Maximum number of iterations
            verbose: Whether to print progress
        
        Returns:
            List of summary trees and their partitions
        """
        # Select initial seeds
        self.summary_trees = self._select_initial_seeds()
        
        if not self.summary_trees:
            raise ValueError("Could not find initial summary trees")
        
        if verbose:
            print(f"Initial trees: {len(self.summary_trees)}")
            for i, tree in enumerate(self.summary_trees):
                print(f"  Tree {i}: {tree}")
        
        prev_coverage = -1
        for iteration in range(max_iterations):
            # Phase 1: Assign nodes to partitions
            if use_vpa:
                self._assign_nodes_vpa()
            else:
                self._assign_nodes_basic()
            
            # Phase 2: Update summary trees
            self._update_summary_trees()
            
            # Check convergence
            current_coverage = self.get_total_coverage()
            
            if verbose and iteration % 10 == 0:
                print(f"Iteration {iteration}: Coverage = {current_coverage:.2f}")
            
            if abs(current_coverage - prev_coverage) < 1e-6:
                if verbose:
                    print(f"Converged after {iteration + 1} iterations")
                break
            prev_coverage = current_coverage
        
        return self.summary_trees, self.partitions
    
    def _assign_nodes_basic(self):
        """Phase 1: Basic assignment (for comparison)"""
        self.partitions = defaultdict(set)
        self.node_assignments = {}
        
        for node in self.gts.st_nodes.values():
            min_dist = float('inf')
            assigned_tree_idx = 0
            
            for idx, tree in enumerate(self.summary_trees):
                dist = self._distance(node, tree)
                if dist < min_dist:
                    min_dist = dist
                    assigned_tree_idx = idx
            
            self.partitions[assigned_tree_idx].add(node)
            self.node_assignments[node] = assigned_tree_idx
    
    def get_total_coverage(self) -> float:
        """Get total activity coverage across all summary trees"""
        # Since trees partition the nodes, sum their coverages
        total = 0
        counted_nodes = set()
        
        for tree in self.summary_trees:
            for node in tree.nodes:
                if node not in counted_nodes:
                    total += node.activity_count
                    counted_nodes.add(node)
        
        return total
    
    def get_partition_coverage(self) -> float:
        """Get total coverage based on partitions (should match tree coverage)"""
        total = 0
        for nodes in self.partitions.values():
            total += sum(node.activity_count for node in nodes)
        return total

# Example usage
def create_example_gts():
    """Create example GTS from the paper (Figure 2)"""
    spatial_framework = ['A', 'B', 'C', 'D', 'E']
    temporal_framework = [1, 2, 3]
    
    spatial_neighbors = {
        'A': ['B'],
        'B': ['A', 'C', 'D'],
        'C': ['B', 'E'],
        'D': ['B', 'E'],
        'E': ['C', 'D']
    }
    
    # Activity data from Figure 2 in the paper
    activity_data = {
        ('A', 1): 5, ('A', 2): 5, ('A', 3): 0,
        ('B', 1): 0, ('B', 2): 5, ('B', 3): 0,
        ('C', 1): 0, ('C', 2): 5, ('C', 3): 0,
        ('D', 1): 0, ('D', 2): 0, ('D', 3): 5,
        ('E', 1): 0, ('E', 2): 5, ('E', 3): 5
    }
    
    return GeoReferencedTimeSeries(spatial_framework, temporal_framework, 
                                  spatial_neighbors, activity_data)

def visualize_tree(tree: STFullTree, gts: GeoReferencedTimeSeries):
    """Simple text visualization of a tree structure"""
    print(f"\nTree rooted at {tree.root}:")
    print(f"  Nodes: {sorted([str(n) for n in tree.nodes])}")
    print(f"  Activity Coverage: {tree.activity_coverage()}")
    
    if tree.edges:
        print("  Structure:")
        # Group by parent
        children_map = defaultdict(list)
        for parent, child in tree.edges:
            children_map[parent].append(child)
        
        # Print tree structure
        for parent in sorted(children_map.keys(), key=lambda x: (x.time_id, x.spatial_id)):
            children = sorted(children_map[parent], key=lambda x: x.spatial_id)
            print(f"    {parent} -> {', '.join(str(c) for c in children)}")

# Run example
def main():
    """Main function for running the kFT algorithm example."""
    # Create example GTS
    gts = create_example_gts()
    
    print("GTS Spatial Framework:", gts.spatial_framework)
    print("GTS Temporal Framework:", gts.temporal_framework)
    print("Number of ST nodes:", len(gts.st_nodes))
    
    # Run kFT algorithm
    kft = KFullTree(gts, k=2, max_tree_degree=3)
    
    print("\n" + "="*50)
    print("Running kFT with VPA...")
    print("="*50)
    
    trees, partitions = kft.fit(use_vpa=True, verbose=True)
    
    print(f"\n{'='*50}")
    print(f"RESULTS: Found {len(trees)} summary trees")
    print(f"{'='*50}")
    
    for i, tree in enumerate(trees):
        print(f"\n--- Summary Tree {i+1} ---")
        visualize_tree(tree, gts)
        print(f"  Partition size: {len(partitions[i])} nodes")
        partition_list = sorted([str(n) for n in partitions[i]])
        print(f"  Partition nodes: {partition_list}")
    
    print(f"\n{'='*50}")
    print(f"Total activity coverage (from trees): {kft.get_total_coverage()}")
    print(f"Total activity coverage (from partitions): {kft.get_partition_coverage()}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()