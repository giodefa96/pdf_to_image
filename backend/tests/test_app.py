import pytest
import logging
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.db.database import db
from src.utils.blob_storage import AzureBlobManager
from src.app import create_app, lifespan

from dotenv import load_dotenv
load_dotenv(override=True)

@pytest.fixture
def app():
    """Fixture that provides the FastAPI application instance."""
    return create_app()


@pytest.fixture
def client(app):
    """Fixture that provides a test client for the FastAPI application."""
    with TestClient(app) as c:
        yield c


class TestAppCreation:
    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        app = create_app()
        assert isinstance(app, FastAPI)

    def test_app_includes_router(self, app):
        """Test that the application includes the router with the correct prefix."""
        routes = [route for route in app.routes if route.path.startswith("/api")]
        assert len(routes) > 0


@pytest.mark.asyncio
class TestLifespan:
    @patch('src.app.blob_storage', new_callable=AsyncMock)
    @patch('src.app.db')  
    async def test_lifespan_success_flow(self, mock_db, mock_blob_storage):
        """Test the successful flow of the lifespan function."""
        mock_app = MagicMock()
        mock_db.initialize = AsyncMock()
        mock_db.create_tables = AsyncMock()
        mock_db.close = AsyncMock()
        
        mock_blob_storage.initialize.return_value = True
        
        async with lifespan(mock_app):
            pass
        
        mock_db.initialize.assert_called_once()
        mock_db.create_tables.assert_called_once()
        mock_blob_storage.initialize.assert_called_once()
        mock_db.close.assert_called_once()
        assert hasattr(mock_app.state, 'blob_storage')