# Copyright 2024 Heinrich Krupp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for Cloudflare storage backend."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import List

from src.mcp_memory_service.storage.cloudflare import CloudflareStorage
from src.mcp_memory_service.models.memory import Memory
from src.mcp_memory_service.utils.hashing import generate_content_hash


@pytest.fixture
def cloudflare_storage():
    """Create a CloudflareStorage instance for testing."""
    return CloudflareStorage(
        api_token="test-token",
        account_id="test-account",
        vectorize_index="test-index",
        d1_database_id="test-db",
        r2_bucket="test-bucket",
        embedding_model="@cf/baai/bge-base-en-v1.5"
    )


@pytest.fixture
def sample_memory():
    """Create a sample memory for testing."""
    content = "This is a test memory"
    return Memory(
        content=content,
        content_hash=generate_content_hash(content),
        tags=["test", "memory"],
        memory_type="standard"
    )


class TestCloudflareStorage:
    """Test suite for CloudflareStorage."""
    
    def test_initialization(self, cloudflare_storage):
        """Test CloudflareStorage initialization."""
        assert cloudflare_storage.api_token == "test-token"
        assert cloudflare_storage.account_id == "test-account"
        assert cloudflare_storage.vectorize_index == "test-index"
        assert cloudflare_storage.d1_database_id == "test-db"
        assert cloudflare_storage.r2_bucket == "test-bucket"
        assert not cloudflare_storage._initialized
        
    @pytest.mark.asyncio
    async def test_get_client(self, cloudflare_storage):
        """Test HTTP client creation."""
        client = await cloudflare_storage._get_client()
        assert client is not None
        assert cloudflare_storage.client == client
        
        # Verify headers are set correctly
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test-token"
        assert client.headers["Content-Type"] == "application/json"
        
    @pytest.mark.asyncio
    async def test_generate_embedding_cache(self, cloudflare_storage):
        """Test embedding generation and caching."""
        test_text = "Test content for embedding"
        
        # Mock the API call
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "result": {"data": [[0.1, 0.2, 0.3, 0.4, 0.5]]}
        }
        
        with patch.object(cloudflare_storage, '_retry_request', return_value=mock_response):
            # First call should make API request
            embedding1 = await cloudflare_storage._generate_embedding(test_text)
            assert embedding1 == [0.1, 0.2, 0.3, 0.4, 0.5]
            
            # Second call should use cache
            embedding2 = await cloudflare_storage._generate_embedding(test_text)
            assert embedding2 == [0.1, 0.2, 0.3, 0.4, 0.5]
            assert embedding1 == embedding2
            
            # Verify cache is populated
            assert len(cloudflare_storage._embedding_cache) == 1
    
    @pytest.mark.asyncio
    async def test_embedding_api_failure(self, cloudflare_storage):
        """Test handling of embedding API failures."""
        test_text = "Test content"
        
        # Mock failed API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": False,
            "errors": ["API error"]
        }
        
        with patch.object(cloudflare_storage, '_retry_request', return_value=mock_response):
            with pytest.raises(ValueError, match="Workers AI embedding failed"):
                await cloudflare_storage._generate_embedding(test_text)
    
    @pytest.mark.asyncio
    async def test_retry_logic(self, cloudflare_storage):
        """Test retry logic with rate limiting."""
        import httpx
        
        # Mock rate limited response followed by success
        responses = [
            Mock(status_code=429, raise_for_status=Mock(side_effect=httpx.HTTPStatusError("Rate limited", request=Mock(), response=Mock()))),
            Mock(status_code=200, raise_for_status=Mock(), json=Mock(return_value={"success": True}))
        ]
        
        with patch('httpx.AsyncClient.request', side_effect=responses):
            with patch('asyncio.sleep'):  # Speed up test
                response = await cloudflare_storage._retry_request("GET", "https://test.com")
                assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_initialization_schema_creation(self, cloudflare_storage):
        """Test D1 schema initialization."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        
        with patch.object(cloudflare_storage, '_retry_request', return_value=mock_response) as mock_request:
            with patch.object(cloudflare_storage, '_verify_vectorize_index'):
                with patch.object(cloudflare_storage, '_verify_r2_bucket'):
                    await cloudflare_storage.initialize()
                    
                    # Verify D1 schema creation was called
                    assert any("CREATE TABLE" in str(call) for call in mock_request.call_args_list)
                    assert cloudflare_storage._initialized
    
    @pytest.mark.asyncio 
    async def test_store_memory_small_content(self, cloudflare_storage, sample_memory):
        """Test storing memory with small content (no R2)."""
        # Mock successful responses
        mock_embedding = [0.1, 0.2, 0.3]
        mock_d1_response = Mock()
        mock_d1_response.json.return_value = {
            "success": True, 
            "result": [{"meta": {"last_row_id": 123}}]
        }
        mock_vectorize_response = Mock()
        mock_vectorize_response.json.return_value = {"success": True}
        
        with patch.object(cloudflare_storage, '_generate_embedding', return_value=mock_embedding):
            with patch.object(cloudflare_storage, '_retry_request') as mock_request:
                mock_request.side_effect = [mock_vectorize_response, mock_d1_response, mock_d1_response]
                
                success, message = await cloudflare_storage.store(sample_memory)
                
                assert success
                assert "successfully" in message.lower()
                
                # Verify Vectorize and D1 calls were made
                assert mock_request.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_store_memory_large_content(self, cloudflare_storage):
        """Test storing memory with large content (uses R2)."""
        # Create memory with large content
        large_content = "x" * (2 * 1024 * 1024)  # 2MB content
        memory = Memory(
            content=large_content,
            content_hash=generate_content_hash(large_content),
            tags=["large"],
            memory_type="standard"
        )
        
        mock_embedding = [0.1, 0.2, 0.3]
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "result": [{"meta": {"last_row_id": 123}}]}
        mock_response.status_code = 200
        
        with patch.object(cloudflare_storage, '_generate_embedding', return_value=mock_embedding):
            with patch.object(cloudflare_storage, '_retry_request', return_value=mock_response):
                success, message = await cloudflare_storage.store(memory)
                
                assert success
                assert "successfully" in message.lower()
    
    @pytest.mark.asyncio
    async def test_retrieve_memories(self, cloudflare_storage):
        """Test retrieving memories by semantic search."""
        mock_embedding = [0.1, 0.2, 0.3]
        mock_vectorize_response = Mock()
        mock_vectorize_response.json.return_value = {
            "success": True,
            "result": {
                "matches": [{
                    "id": "mem_test123",
                    "score": 0.95,
                    "metadata": {"content_hash": "test123"}
                }]
            }
        }
        
        mock_d1_response = Mock()
        mock_d1_response.json.return_value = {
            "success": True,
            "result": [{
                "results": [{
                    "id": 1,
                    "content_hash": "test123",
                    "content": "Test memory content",
                    "memory_type": "standard",
                    "created_at": 1234567890,
                    "metadata_json": "{}"
                }]
            }]
        }
        
        # Mock tag loading
        mock_tags_response = Mock()
        mock_tags_response.json.return_value = {
            "success": True,
            "result": [{"results": [{"name": "test"}, {"name": "memory"}]}]
        }
        
        with patch.object(cloudflare_storage, '_generate_embedding', return_value=mock_embedding):
            with patch.object(cloudflare_storage, '_retry_request') as mock_request:
                mock_request.side_effect = [mock_vectorize_response, mock_d1_response, mock_tags_response]
                
                results = await cloudflare_storage.retrieve("test query", 5)
                
                assert len(results) == 1
                assert results[0].similarity_score == 0.95
                assert results[0].memory.content == "Test memory content"
                assert results[0].memory.content_hash == "test123"
    
    @pytest.mark.asyncio
    async def test_search_by_tag(self, cloudflare_storage):
        """Test searching memories by tags."""
        mock_d1_response = Mock()
        mock_d1_response.json.return_value = {
            "success": True,
            "result": [{
                "results": [{
                    "id": 1,
                    "content_hash": "test123",
                    "content": "Tagged memory",
                    "memory_type": "standard"
                }]
            }]
        }
        
        mock_tags_response = Mock()
        mock_tags_response.json.return_value = {
            "success": True,
            "result": [{"results": [{"name": "test"}]}]
        }
        
        with patch.object(cloudflare_storage, '_retry_request') as mock_request:
            mock_request.side_effect = [mock_d1_response, mock_tags_response]
            
            memories = await cloudflare_storage.search_by_tag(["test"])
            
            assert len(memories) == 1
            assert memories[0].content == "Tagged memory"
            assert memories[0].content_hash == "test123"
    
    @pytest.mark.asyncio
    async def test_delete_memory(self, cloudflare_storage):
        """Test deleting a memory."""
        mock_find_response = Mock()
        mock_find_response.json.return_value = {
            "success": True,
            "result": [{
                "results": [{
                    "id": 1,
                    "vector_id": "mem_test123",
                    "r2_key": None
                }]
            }]
        }
        
        mock_delete_response = Mock()
        mock_delete_response.json.return_value = {"success": True}
        
        with patch.object(cloudflare_storage, '_retry_request') as mock_request:
            mock_request.side_effect = [mock_find_response, mock_delete_response, mock_delete_response]
            
            success, message = await cloudflare_storage.delete("test123")
            
            assert success
            assert "successfully" in message.lower()
    
    @pytest.mark.asyncio
    async def test_get_stats(self, cloudflare_storage):
        """Test getting storage statistics."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "result": [{
                "results": [{
                    "total_memories": 10,
                    "total_content_size": 1024,
                    "total_vectors": 10,
                    "r2_stored_count": 2
                }]
            }]
        }
        
        with patch.object(cloudflare_storage, '_retry_request', return_value=mock_response):
            stats = await cloudflare_storage.get_stats()
            
            assert stats["total_memories"] == 10
            assert stats["total_content_size_bytes"] == 1024
            assert stats["storage_backend"] == "cloudflare"
            assert stats["vectorize_index"] == "test-index"
            assert stats["status"] == "operational"
    
    @pytest.mark.asyncio
    async def test_cleanup_duplicates(self, cloudflare_storage):
        """Test cleaning up duplicate memories."""
        mock_find_response = Mock()
        mock_find_response.json.return_value = {
            "success": True,
            "result": [{
                "results": [{
                    "content_hash": "duplicate123",
                    "count": 3,
                    "keep_id": 1
                }]
            }]
        }
        
        mock_delete_response = Mock()
        mock_delete_response.json.return_value = {
            "success": True,
            "result": [{"meta": {"changes": 2}}]
        }
        
        with patch.object(cloudflare_storage, '_retry_request') as mock_request:
            mock_request.side_effect = [mock_find_response, mock_delete_response]
            
            count, message = await cloudflare_storage.cleanup_duplicates()
            
            assert count == 2
            assert "2 duplicates" in message
    
    @pytest.mark.asyncio
    async def test_close(self, cloudflare_storage):
        """Test closing the storage backend."""
        # Create a mock client
        mock_client = AsyncMock()
        cloudflare_storage.client = mock_client
        cloudflare_storage._embedding_cache = {"test": [1, 2, 3]}
        
        await cloudflare_storage.close()
        
        # Verify client was closed and cache cleared
        mock_client.aclose.assert_called_once()
        assert cloudflare_storage.client is None
        assert len(cloudflare_storage._embedding_cache) == 0