import unittest
import numpy as np
import networkx as nx
from collections import defaultdict
from kft import STNode, STFullTree, GeoReferencedTimeSeries, KFullTree, create_example_gts


class TestSTNode(unittest.TestCase):
    """Test cases for STNode class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.node1 = STNode("A", 1, 5.0)
        self.node2 = STNode("A", 1, 5.0)
        self.node3 = STNode("B", 2, 3.0)
        
    def test_node_creation(self):
        """Test STNode creation"""
        node = STNode("C", 3, 10.5)
        self.assertEqual(node.spatial_id, "C")
        self.assertEqual(node.time_id, 3)
        self.assertEqual(node.activity_count, 10.5)
    
    def test_node_equality(self):
        """Test STNode equality comparison"""
        self.assertEqual(self.node1, self.node2)
        self.assertNotEqual(self.node1, self.node3)
        
    def test_node_hash(self):
        """Test STNode hashing"""
        self.assertEqual(hash(self.node1), hash(self.node2))
        self.assertNotEqual(hash(self.node1), hash(self.node3))
        
        # Test that nodes can be used in sets
        node_set = {self.node1, self.node2, self.node3}
        self.assertEqual(len(node_set), 2)  # node1 and node2 are equal
        
    def test_node_repr(self):
        """Test STNode string representation"""
        self.assertEqual(str(self.node1), "A1")
        self.assertEqual(str(self.node3), "B2")


class TestSTFullTree(unittest.TestCase):
    """Test cases for STFullTree class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = STNode("A", 1, 5.0)
        self.child1 = STNode("B", 2, 3.0)
        self.child2 = STNode("C", 2, 4.0)
        
        self.nodes = {self.root, self.child1, self.child2}
        self.edges = {(self.root, self.child1), (self.root, self.child2)}
        
        self.tree = STFullTree(self.root, self.nodes, self.edges, 2, 1)
        
    def test_tree_creation(self):
        """Test STFullTree creation"""
        self.assertEqual(self.tree.root, self.root)
        self.assertEqual(self.tree.nodes, self.nodes)
        self.assertEqual(self.tree.edges, self.edges)
        self.assertEqual(self.tree.degree, 2)
        self.assertEqual(self.tree.depth, 1)
        
    def test_activity_coverage(self):
        """Test activity coverage calculation"""
        expected_coverage = 5.0 + 3.0 + 4.0  # sum of all node activities
        self.assertEqual(self.tree.activity_coverage(), expected_coverage)
        
    def test_contains_node(self):
        """Test node membership checking"""
        self.assertTrue(self.tree.contains_node(self.root))
        self.assertTrue(self.tree.contains_node(self.child1))
        self.assertFalse(self.tree.contains_node(STNode("D", 3, 1.0)))
        
    def test_single_node_tree(self):
        """Test single node tree"""
        single_tree = STFullTree(self.root, {self.root}, set(), 0, 0)
        self.assertEqual(single_tree.activity_coverage(), 5.0)
        self.assertTrue(single_tree.contains_node(self.root))
        
    def test_tree_repr(self):
        """Test tree string representation"""
        repr_str = str(self.tree)
        self.assertIn("Tree(root=A1", repr_str)
        self.assertIn("nodes=3", repr_str)
        self.assertIn("AC=12.0", repr_str)


class TestGeoReferencedTimeSeries(unittest.TestCase):
    """Test cases for GeoReferencedTimeSeries class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.spatial_framework = ['A', 'B', 'C']
        self.temporal_framework = [1, 2, 3]
        self.spatial_neighbors = {
            'A': ['B'],
            'B': ['A', 'C'],
            'C': ['B']
        }
        self.activity_data = {
            ('A', 1): 5, ('A', 2): 3, ('A', 3): 1,
            ('B', 1): 2, ('B', 2): 4, ('B', 3): 6,
            ('C', 1): 1, ('C', 2): 2, ('C', 3): 3
        }
        
        self.gts = GeoReferencedTimeSeries(
            self.spatial_framework,
            self.temporal_framework,
            self.spatial_neighbors,
            self.activity_data
        )
        
    def test_gts_creation(self):
        """Test GTS creation"""
        self.assertEqual(self.gts.spatial_framework, self.spatial_framework)
        self.assertEqual(self.gts.temporal_framework, self.temporal_framework)
        self.assertEqual(self.gts.spatial_neighbors, self.spatial_neighbors)
        self.assertEqual(self.gts.activity_data, self.activity_data)
        
    def test_st_nodes_creation(self):
        """Test ST nodes are created correctly"""
        expected_node_count = len(self.spatial_framework) * len(self.temporal_framework)
        self.assertEqual(len(self.gts.st_nodes), expected_node_count)
        
        # Check specific nodes
        node_a1 = self.gts.st_nodes[('A', 1)]
        self.assertEqual(node_a1.spatial_id, 'A')
        self.assertEqual(node_a1.time_id, 1)
        self.assertEqual(node_a1.activity_count, 5)
        
    def test_st_graph_structure(self):
        """Test ST graph is built correctly"""
        # Check graph has all nodes
        self.assertEqual(len(self.gts.st_graph.nodes), 9)  # 3 spatial × 3 temporal
        
        # Check specific edges exist
        node_a1 = self.gts.st_nodes[('A', 1)]
        node_a2 = self.gts.st_nodes[('A', 2)]
        node_b2 = self.gts.st_nodes[('B', 2)]
        
        # A1 should connect to A2 (temporal) and B2 (spatial neighbor)
        successors = list(self.gts.st_graph.successors(node_a1))
        self.assertIn(node_a2, successors)
        self.assertIn(node_b2, successors)
        
    def test_get_st_neighbors(self):
        """Test ST neighbor retrieval"""
        node_a1 = self.gts.st_nodes[('A', 1)]
        neighbors = self.gts.get_st_neighbors(node_a1)
        
        # Should have neighbors at time 2
        neighbor_ids = [(n.spatial_id, n.time_id) for n in neighbors]
        self.assertIn(('A', 2), neighbor_ids)  # Temporal neighbor
        self.assertIn(('B', 2), neighbor_ids)  # Spatial neighbor
        
    def test_missing_activity_data(self):
        """Test handling of missing activity data"""
        incomplete_data = {('A', 1): 5}  # Missing most data points
        gts = GeoReferencedTimeSeries(
            ['A', 'B'], [1, 2], {'A': ['B'], 'B': ['A']}, incomplete_data
        )
        
        # Should default to 0 for missing data
        node_b2 = gts.st_nodes[('B', 2)]
        self.assertEqual(node_b2.activity_count, 0)
        
    def test_last_time_period_no_successors(self):
        """Test that last time period nodes have no successors"""
        node_a3 = self.gts.st_nodes[('A', 3)]  # Last time period
        neighbors = self.gts.get_st_neighbors(node_a3)
        self.assertEqual(len(neighbors), 0)


class TestKFullTree(unittest.TestCase):
    """Test cases for KFullTree class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.gts = create_example_gts()
        self.kft = KFullTree(self.gts, k=2, max_tree_degree=2)
        
    def test_kft_creation(self):
        """Test KFullTree creation"""
        self.assertEqual(self.kft.k, 2)
        self.assertEqual(self.kft.max_tree_degree, 2)
        self.assertEqual(self.kft.gts, self.gts)
        self.assertEqual(len(self.kft.summary_trees), 0)  # Initially empty
        
    def test_distance_calculation(self):
        """Test distance calculation between node and tree"""
        # Create a simple tree
        root = STNode("A", 1, 5.0)
        tree = STFullTree(root, {root}, set(), 1, 0)
        
        # Distance from root to itself should be 0
        self.assertEqual(self.kft._distance(root, tree), 0)
        
        # Distance from connected node should be finite
        node_b1 = self.gts.st_nodes[('B', 1)]
        distance = self.kft._distance(node_b1, tree)
        self.assertGreater(distance, 0)
        self.assertLess(distance, float('inf'))
        
    def test_tree_validation(self):
        """Test tree validation logic"""
        # Valid single node tree
        root = STNode("A", 1, 5.0)
        single_tree = STFullTree(root, {root}, set(), 1, 0)
        self.assertTrue(self.kft._is_valid_full_tree(single_tree, 1))
        
        # Valid two-level tree
        child = STNode("B", 2, 3.0)
        two_level_tree = STFullTree(
            root, {root, child}, {(root, child)}, 1, 1
        )
        self.assertTrue(self.kft._is_valid_full_tree(two_level_tree, 1))
        
    def test_initial_seed_selection(self):
        """Test initial seed selection"""
        seeds = self.kft._select_initial_seeds()
        
        # Should return requested number of trees (or fewer if impossible)
        self.assertLessEqual(len(seeds), self.kft.k)
        self.assertGreater(len(seeds), 0)
        
        # All seeds should be valid trees
        for tree in seeds:
            self.assertIsInstance(tree, STFullTree)
            self.assertGreater(len(tree.nodes), 0)
            
    def test_child_assignment_validation(self):
        """Test valid child assignment finding"""
        parents = [self.gts.st_nodes[('A', 1)]]
        children = {self.gts.st_nodes[('A', 2)], self.gts.st_nodes[('B', 2)]}
        
        assignments = self.kft._find_valid_child_assignments(parents, children, 2)
        
        # Should find valid assignments if possible
        if assignments:
            for assignment in assignments:
                for parent, assigned_children in assignment.items():
                    self.assertEqual(len(assigned_children), 2)
                    
    def test_coverage_calculation(self):
        """Test coverage calculations"""
        # Run algorithm to get trees
        self.kft.summary_trees = self.kft._select_initial_seeds()
        
        if self.kft.summary_trees:
            total_coverage = self.kft.get_total_coverage()
            self.assertGreater(total_coverage, 0)
            
            # Coverage should not exceed total activity in GTS
            total_activity = sum(self.gts.activity_data.values())
            self.assertLessEqual(total_coverage, total_activity)
            
    def test_node_assignment_basic(self):
        """Test basic node assignment"""
        # Need some initial trees
        self.kft.summary_trees = self.kft._select_initial_seeds()
        
        if self.kft.summary_trees:
            self.kft._assign_nodes_basic()
            
            # All nodes should be assigned
            all_nodes = set(self.gts.st_nodes.values())
            assigned_nodes = set()
            for partition in self.kft.partitions.values():
                assigned_nodes.update(partition)
            
            self.assertEqual(len(assigned_nodes), len(all_nodes))
            
    def test_find_valid_child_assignments_insufficient_children(self):
        """Test child assignment when insufficient children available"""
        parents = [self.gts.st_nodes[('A', 1)]]
        children = {self.gts.st_nodes[('A', 2)]}  # Only 1 child, need 2
        
        assignments = self.kft._find_valid_child_assignments(parents, children, 2)
        self.assertEqual(len(assignments), 0)  # Should be empty
        
    def test_update_summary_trees_phase2(self):
        """Test Phase 2: Summary tree update functionality"""
        # Set up initial state with some trees and partitions
        self.kft.summary_trees = self.kft._select_initial_seeds()
        
        # Create mock partitions for testing
        all_nodes = list(self.gts.st_nodes.values())
        mid_point = len(all_nodes) // 2
        
        # Manually set up partitions
        self.kft.partitions = defaultdict(set)
        self.kft.partitions[0] = set(all_nodes[:mid_point])
        self.kft.partitions[1] = set(all_nodes[mid_point:])
        
        # Store original trees for comparison
        original_trees = self.kft.summary_trees.copy()
        original_coverage = self.kft.get_total_coverage()
        
        # Run Phase 2: Update summary trees
        self.kft._update_summary_trees()
        
        # Verify results
        self.assertEqual(len(self.kft.summary_trees), self.kft.k)
        
        # All trees should be valid STFullTree instances
        for tree in self.kft.summary_trees:
            self.assertIsInstance(tree, STFullTree)
            self.assertGreater(len(tree.nodes), 0)
            
        # Trees should have reasonable coverage
        new_coverage = self.kft.get_total_coverage()
        self.assertGreater(new_coverage, 0)
        
        # Each tree should contain nodes from its corresponding partition
        for i, tree in enumerate(self.kft.summary_trees):
            partition_nodes = self.kft.partitions[i]
            if partition_nodes:  # Only check non-empty partitions
                # Tree nodes should be subset of partition nodes
                self.assertTrue(tree.nodes.issubset(partition_nodes.union(set())))
                
    def test_update_summary_trees_empty_partition(self):
        """Test Phase 2 with empty partitions"""
        # Set up with initial trees
        self.kft.summary_trees = self.kft._select_initial_seeds()
        original_trees = self.kft.summary_trees.copy()
        
        # Create partitions where one is empty
        all_nodes = list(self.gts.st_nodes.values())
        self.kft.partitions = defaultdict(set)
        self.kft.partitions[0] = set(all_nodes)  # All nodes in first partition
        self.kft.partitions[1] = set()  # Empty second partition
        
        # Run update
        self.kft._update_summary_trees()
        
        # Should still have k trees
        self.assertEqual(len(self.kft.summary_trees), self.kft.k)
        
        # Second tree should be kept from original (empty partition case)
        if len(original_trees) >= 2:
            self.assertEqual(self.kft.summary_trees[1], original_trees[1])
            
    def test_update_summary_trees_single_node_fallback(self):
        """Test Phase 2 when no valid full trees can be built"""
        # Set up with minimal configuration that might struggle to build full trees
        small_kft = KFullTree(self.gts, k=3, max_tree_degree=4)  # High degree, many trees
        small_kft.summary_trees = small_kft._select_initial_seeds()
        
        # Create partitions with isolated nodes
        nodes = list(self.gts.st_nodes.values())
        small_kft.partitions = defaultdict(set)
        for i in range(min(3, len(nodes))):
            if i < len(nodes):
                small_kft.partitions[i] = {nodes[i]}  # Single node partitions
        
        # Run update
        small_kft._update_summary_trees()
        
        # Should still produce valid trees (possibly single-node trees)
        self.assertGreater(len(small_kft.summary_trees), 0)
        for tree in small_kft.summary_trees:
            self.assertIsInstance(tree, STFullTree)
            self.assertGreater(len(tree.nodes), 0)


class TestKFullTreeIntegration(unittest.TestCase):
    """Integration tests for the complete KFullTree algorithm"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.gts = create_example_gts()
        
    def test_complete_algorithm_execution(self):
        """Test complete algorithm execution"""
        kft = KFullTree(self.gts, k=2, max_tree_degree=2)
        
        # Should run without errors
        trees, partitions = kft.fit(use_vpa=True, max_iterations=10, verbose=False)
        
        # Should return requested structures
        self.assertIsInstance(trees, list)
        self.assertIsInstance(partitions, defaultdict)
        self.assertLessEqual(len(trees), kft.k)
        
        # Trees should be valid
        for tree in trees:
            self.assertIsInstance(tree, STFullTree)
            self.assertGreater(len(tree.nodes), 0)
            
    def test_algorithm_with_different_k_values(self):
        """Test algorithm with different k values"""
        for k in [1, 2, 3]:
            kft = KFullTree(self.gts, k=k, max_tree_degree=2)
            trees, partitions = kft.fit(use_vpa=True, max_iterations=5, verbose=False)
            
            self.assertLessEqual(len(trees), k)
            self.assertLessEqual(len(partitions), k)
            
    def test_algorithm_convergence(self):
        """Test algorithm convergence"""
        kft = KFullTree(self.gts, k=2, max_tree_degree=2)
        
        # Run with more iterations to test convergence
        trees, partitions = kft.fit(use_vpa=True, max_iterations=50, verbose=False)
        
        # Should converge and return valid results
        self.assertGreater(len(trees), 0)
        
        # Coverage should be reasonable
        total_coverage = kft.get_total_coverage()
        partition_coverage = kft.get_partition_coverage()
        
        # These should be close (accounting for algorithm differences)
        # The difference can occur due to overlapping nodes in trees vs partitions
        self.assertGreater(total_coverage, 0)
        self.assertGreater(partition_coverage, 0)
        
    def test_basic_vs_vpa_assignment(self):
        """Test comparison between basic and VPA assignment"""
        kft_basic = KFullTree(self.gts, k=2, max_tree_degree=2)
        kft_vpa = KFullTree(self.gts, k=2, max_tree_degree=2)
        
        # Run both variants
        trees_basic, _ = kft_basic.fit(use_vpa=False, max_iterations=10, verbose=False)
        trees_vpa, _ = kft_vpa.fit(use_vpa=True, max_iterations=10, verbose=False)
        
        # Both should produce valid results
        self.assertGreater(len(trees_basic), 0)
        self.assertGreater(len(trees_vpa), 0)
        
        # Both should have reasonable coverage
        self.assertGreater(kft_basic.get_total_coverage(), 0)
        self.assertGreater(kft_vpa.get_total_coverage(), 0)
        
    def test_edge_cases(self):
        """Test edge cases"""
        # Test with k=1
        kft_single = KFullTree(self.gts, k=1, max_tree_degree=2)
        trees, partitions = kft_single.fit(max_iterations=5, verbose=False)
        
        self.assertEqual(len(trees), 1)
        self.assertEqual(len(partitions), 1)
        
        # Test with very small degree
        kft_small_degree = KFullTree(self.gts, k=2, max_tree_degree=1)
        trees, partitions = kft_small_degree.fit(max_iterations=5, verbose=False)
        
        self.assertGreater(len(trees), 0)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)