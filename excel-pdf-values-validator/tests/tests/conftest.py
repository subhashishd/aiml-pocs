"""
Test configuration and fixtures for autonomous agents tests.
"""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from celery import Celery

# Set test environment
os.environ['TESTING'] = 'True'
os.environ['CELERY_ALWAYS_EAGER'] = 'True'
os.environ['CELERY_BROKER_URL'] = 'redis://localhost:6380/0'
os.environ['CELERY_RESULT_BACKEND'] = 'redis://localhost:6380/0'

@pytest.fixture(scope="session")
def celery_app():
    """Create a Celery app for testing."""
    app = Celery('test_app')
    app.config_from_object('app.celery_config_test')
    
    # Override to use eager execution for tests
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_url='memory://',
        result_backend='cache+memory://',
    )
    
    return app

@pytest.fixture(scope="session")
def celery_worker(celery_app):
    """Create a Celery worker for testing."""
    return celery_app.Worker(include=['app.autonomous_agents.intelligent_agents'])

@pytest.fixture
def temp_files():
    """Create temporary files for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
        pdf_file.write(b'test pdf content')
        pdf_path = pdf_file.name
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as excel_file:
        excel_file.write(b'test excel content')
        excel_path = excel_file.name
    
    yield pdf_path, excel_path
    
    # Cleanup
    try:
        os.unlink(pdf_path)
        os.unlink(excel_path)
    except OSError:
        pass

@pytest.fixture
def mock_pdf_processor():
    """Mock PDF processor for testing."""
    mock = MagicMock()
    mock.process_pdf.return_value = [
        {'text': 'test chunk 1', 'page': 1},
        {'text': 'test chunk 2', 'page': 2}
    ]
    return mock

@pytest.fixture
def mock_excel_processor():
    """Mock Excel processor for testing."""
    mock = MagicMock()
    mock.process_excel.return_value = [
        {'parameter': 'param1', 'value': 'value1', 'row': 1},
        {'parameter': 'param2', 'value': 'value2', 'row': 2}
    ]
    return mock

@pytest.fixture
def mock_validation_service():
    """Mock validation service for testing."""
    mock = MagicMock()
    mock.validate_data.return_value = {
        'matches': 2,
        'mismatches': 0,
        'accuracy': 100.0,
        'details': []
    }
    return mock

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test."""
    # Mock all service imports to prevent import errors
    with patch.dict('sys.modules', {
        'app.services.pdf_processor': MagicMock(),
        'app.services.excel_processor': MagicMock(),
        'app.services.validation_service': MagicMock(),
        'app.services.optimized_multimodal_pdf_processor': MagicMock(),
        'app.services.local_multimodal_pdf_processor': MagicMock(),
        'services.pdf_processor': MagicMock(),
        'services.excel_processor': MagicMock(),
        'services.validation_service': MagicMock(),
        'services.optimized_multimodal_pdf_processor': MagicMock(),
        'services.local_multimodal_pdf_processor': MagicMock(),
    }):
        yield

@pytest.fixture
def redis_connection():
    """Provide Redis connection for tests that need it."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)
        r.ping()  # Test connection
        yield r
    except (ImportError, redis.ConnectionError):
        # If Redis is not available, provide a mock
        mock_redis = MagicMock()
        yield mock_redis
