"""Pytest fixtures for TVS Credit NIRNAY tests."""

import pytest
from app.services.model_service import model_service


@pytest.fixture(scope="session", autouse=True)
def setup_model_service():
    """Ensure model artifacts are loaded once for the entire test session."""
    try:
        model_service.load_artifacts()
    except Exception as e:
        print(f"Warning in conftest: could not load model artifacts: {e}")
