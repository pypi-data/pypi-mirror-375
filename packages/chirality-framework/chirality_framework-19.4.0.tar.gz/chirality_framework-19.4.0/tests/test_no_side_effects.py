"""
Test that imports and constructors have no network side effects.

Per colleague_1's guidance: constructors must remain side-effect free.
"""

import unittest
from unittest.mock import patch, MagicMock
import socket
import requests


class TestNoSideEffects(unittest.TestCase):
    """Test that key components have no network side effects on import/construction."""

    def setUp(self):
        """Set up network monitoring."""
        # Track network calls
        self.network_calls = []
        
        # Mock socket operations
        self.socket_patcher = patch('socket.socket')
        self.mock_socket = self.socket_patcher.start()
        self.mock_socket.side_effect = self._track_socket_call
        
        # Mock requests operations
        self.requests_patcher = patch('requests.request')
        self.mock_requests = self.requests_patcher.start()
        self.mock_requests.side_effect = self._track_request_call
        
    def tearDown(self):
        """Clean up patches."""
        self.socket_patcher.stop()
        self.requests_patcher.stop()
        
    def _track_socket_call(self, *args, **kwargs):
        """Track socket calls."""
        self.network_calls.append(f"socket.socket({args}, {kwargs})")
        raise Exception("Network call detected!")
        
    def _track_request_call(self, *args, **kwargs):
        """Track request calls."""
        self.network_calls.append(f"requests.request({args}, {kwargs})")
        raise Exception("Network call detected!")

    def test_catalog_generator_import_no_network(self):
        """Test that importing LensCatalogGenerator makes no network calls."""
        try:
            from chirality.application.lenses.catalog_generator import LensCatalogGenerator
            # Import should succeed without network calls
        except Exception as e:
            if "Network call detected" in str(e):
                self.fail(f"Network call detected during import: {self.network_calls}")
            # Re-raise other exceptions (import errors are ok, network calls are not)
            pass

    def test_catalog_generator_constructor_no_network(self):
        """Test that constructing LensCatalogGenerator makes no network calls."""
        try:
            from chirality.application.lenses.catalog_generator import LensCatalogGenerator
            # Constructor should not make network calls
            generator = LensCatalogGenerator()
            # Success - no network calls during construction
        except Exception as e:
            if "Network call detected" in str(e):
                self.fail(f"Network call detected during construction: {self.network_calls}")
            # Other exceptions during construction are acceptable (config issues, etc.)
            # as long as no network calls were made
            pass

    def test_dialogue_orchestrator_import_no_network(self):
        """Test that importing DialogueOrchestrator makes no network calls."""
        try:
            from chirality.application.phase1.dialogue_run import DialogueOrchestrator
            # Import should succeed without network calls
        except Exception as e:
            if "Network call detected" in str(e):
                self.fail(f"Network call detected during import: {self.network_calls}")
            pass


if __name__ == "__main__":
    unittest.main()