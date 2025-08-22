import pytest
import json
from app import create_app, db

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_status(client):
    """Test the /api/gpts/status endpoint."""
    response = client.get("/api/gpts/status")
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["status"] == "active"
    assert "version" in data
    assert "api_version" in data["version"]

def test_health_check(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    # Should return 200 or 503 depending on database connection
    assert response.status_code in [200, 503]
    
    data = json.loads(response.data)
    assert "status" in data
    assert "components" in data
    assert "database" in data["components"]
    assert "okx_api" in data["components"]

def test_status_endpoint_structure(client):
    """Test the structure of status endpoint response."""
    response = client.get("/api/gpts/status")
    data = json.loads(response.data)
    
    # Check required fields
    required_fields = ["status", "version", "components", "supported_symbols", "supported_timeframes", "timestamp"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Check components
    required_components = ["signal_generator", "smc_analyzer", "okx_api", "openai", "database"]
    for component in required_components:
        assert component in data["components"], f"Missing component: {component}"

def test_health_endpoint_structure(client):
    """Test the structure of health endpoint response."""
    response = client.get("/health")
    data = json.loads(response.data)
    
    # Check required fields
    required_fields = ["status", "components", "version", "timestamp"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Check components structure
    for component_name, component_data in data["components"].items():
        assert "status" in component_data, f"Component {component_name} missing status"
        assert "message" in component_data, f"Component {component_name} missing message"