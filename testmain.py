import unittest

# Discover and load all test cases from the 'tests' directory
loader = unittest.TestLoader()
suite = loader.discover(start_dir='tests', pattern='*.py')

# Run the test suite
runner = unittest.TextTestRunner()
result = runner.run(suite)

# Exit with appropriate code depending on the test results
exit_code = 0 if result.wasSuccessful() else 1
exit(exit_code)
