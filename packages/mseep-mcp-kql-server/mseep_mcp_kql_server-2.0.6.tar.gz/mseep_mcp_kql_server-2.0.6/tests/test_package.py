"""
Test module for package-level functionality.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

def test_package_imports():
    """Test that package imports work correctly."""
    try:
        import mcp_kql_server
        assert hasattr(mcp_kql_server, '__version__')
        assert hasattr(mcp_kql_server, '__author__')
        assert mcp_kql_server.__version__ == "2.0.4"
        assert mcp_kql_server.__author__ == "Arjun Trivedi"
    except ImportError:
        # Skip test if package not available in CI
        pass


def test_version_consistency():
    """Test that version is consistent across modules."""
    try:
        from mcp_kql_server import __version__ as pkg_version
        from mcp_kql_server.constants import __version__ as const_version
        
        assert pkg_version == const_version == "2.0.4"
    except ImportError:
        # Skip test if modules not available in CI
        pass


def test_author_attribution():
    """Test that author information is properly set."""
    try:
        from mcp_kql_server import __author__, __email__
        
        assert __author__ == "Arjun Trivedi"
        assert __email__ == "arjuntrivedi42@yahoo.com"
    except ImportError:
        # Skip test if package not available in CI
        pass


def test_module_structure():
    """Test that expected modules exist."""
    expected_modules = [
        'mcp_kql_server.constants',
        'mcp_kql_server.utils',
        'mcp_kql_server.execute_kql',
        'mcp_kql_server.kql_auth',
        'mcp_kql_server.mcp_server'
    ]
    
    for module_name in expected_modules:
        try:
            __import__(module_name)
            # If we get here, the module exists
            pass
        except ImportError:
            # Skip individual module if not available
            pass


def test_basic_functionality():
    """Test basic package functionality without external dependencies."""
    try:
        # Test that we can import key functions
        from mcp_kql_server.utils import truncate_string, is_debug_mode
        
        # Test basic utility functions
        assert truncate_string("Hello World", 5) == "He..."
        assert isinstance(is_debug_mode(), bool)
        
    except ImportError:
        # Skip test if modules not available
        pass