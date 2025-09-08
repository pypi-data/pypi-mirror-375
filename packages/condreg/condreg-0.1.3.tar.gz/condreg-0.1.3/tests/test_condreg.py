"""
Test cases for CondrReg package
"""
import numpy as np
import unittest
import sys
import os

# Add the parent directory to the path so we can import condreg
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the condreg package properly
import condreg

class TestCondrReg(unittest.TestCase):
    def setUp(self):
        # This runs before each test
        np.random.seed(123)  # For reproducibility
        self.n = 30  # samples
        self.p = 10  # features
        
        # Create synthetic data with known covariance structure
        sigma = np.eye(self.p)
        sigma[2, 3] = sigma[3, 2] = 0.7  # Add some covariance
        
        # Generate multivariate normal data
        mean = np.zeros(self.p)
        self.X = np.random.multivariate_normal(mean, sigma, self.n)
        
    def test_import(self):
        """Test that the module imports successfully"""
        self.assertIsNotNone(condreg)
        self.assertTrue(hasattr(condreg, 'kgrid'))
        self.assertTrue(hasattr(condreg, 'select_condreg'))
        self.assertTrue(hasattr(condreg, 'condreg'))
        self.assertTrue(hasattr(condreg, 'pfweights'))
        self.assertTrue(hasattr(condreg, 'transcost'))
        
    def test_kgrid(self):
        """Test kgrid function creates appropriate penalty grid"""
        grid = condreg.kgrid(20, 10)
        
        # Check grid properties
        self.assertEqual(len(grid), 10)
        self.assertGreaterEqual(grid[0], 1.0)
        self.assertLessEqual(grid[-1], 20.0)
        self.assertTrue(np.all(np.diff(grid) > 0))  # Should be monotonically increasing
        
    def test_condreg(self):
        """Test condreg function with a fixed penalty"""
        result = condreg.condreg(self.X, 5.0)
        
        # Check output contains expected keys
        self.assertIn('S', result)
        self.assertIn('invS', result)
        
        # Check dimensions
        self.assertEqual(result['S'].shape, (self.p, self.p))
        self.assertEqual(result['invS'].shape, (self.p, self.p))
        
        # Check properties of the regularized covariance
        eigenvalues = np.linalg.eigvalsh(result['S'])
        condition_number = eigenvalues[-1] / eigenvalues[0]
        
        # Condition number should be at most the specified bound
        self.assertLessEqual(condition_number, 5.01)  # Allow small numerical error
        
        # Covariance and precision should be inverses of each other
        identity = np.matmul(result['S'], result['invS'])
        np.testing.assert_almost_equal(identity, np.eye(self.p), decimal=10)
        
    def test_select_condreg(self):
        """Test select_condreg function with cross-validation"""
        # Create penalty grid
        k_grid = condreg.kgrid(10, 5)
        
        # Run with cross-validation
        result = condreg.select_condreg(self.X, k_grid)
        
        # Check output contains expected keys
        self.assertIn('S', result)
        self.assertIn('invS', result)
        self.assertIn('kmax', result)
        
        # Check dimensions
        self.assertEqual(result['S'].shape, (self.p, self.p))
        self.assertEqual(result['invS'].shape, (self.p, self.p))
        
        # kmax should be a scalar in the range of k_grid
        self.assertGreaterEqual(result['kmax'], min(k_grid))
        self.assertLessEqual(result['kmax'], max(k_grid))
        
        # Covariance and precision should be inverses of each other
        identity = np.matmul(result['S'], result['invS'])
        np.testing.assert_almost_equal(identity, np.eye(self.p), decimal=10)
        
    def test_pfweights(self):
        """Test portfolio weight calculation"""
        # Create a simple covariance matrix
        sigma = np.eye(5)
        sigma[0, 1] = sigma[1, 0] = 0.5
        
        # Calculate weights
        weights = condreg.pfweights(sigma)
        
        # Check properties
        self.assertEqual(len(weights), 5)
        self.assertAlmostEqual(np.sum(weights), 1.0)  # Should sum to 1
        
        # With identity covariance (plus small perturbation),
        # weights should be approximately equal
        self.assertTrue(np.allclose(weights, np.ones(5)/5, rtol=0.3))
        
    def test_transcost(self):
        """Test transaction cost calculation"""
        old_weights = np.array([0.2, 0.3, 0.5])
        new_weights = np.array([0.4, 0.3, 0.3])
        
        cost = condreg.transcost(
            new_weights, old_weights, 
            lastearnings=1.0, reltc=0.01, wealth=1000.0
        )
        
        # Manual calculation: wealth * reltc * sum(abs(wnew - wold))
        expected = 1000.0 * 0.01 * (0.2 + 0.0 + 0.2)
        self.assertAlmostEqual(cost, expected)
        
    def test_select_kmax(self):
        """Test penalty parameter selection"""
        # Create penalty grid
        k_grid = condreg.kgrid(10, 5)
        
        # Run cross-validation
        result = condreg.select_kmax(self.X, k_grid)
        
        # Check output contains expected keys
        self.assertIn('kmax', result)
        self.assertIn('negL', result)
        
        # Check dimensions
        self.assertEqual(len(result['negL']), len(k_grid))
        
        # kmax should be a scalar in the range of k_grid
        self.assertGreaterEqual(result['kmax'], min(k_grid))
        self.assertLessEqual(result['kmax'], max(k_grid))
        
if __name__ == '__main__':
    unittest.main()
