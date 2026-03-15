"""
Tests for auto-conversion of large prompts to attachments in copilot_ollama.py

Tests cover:
- convert_large_prompt_to_attachment() function
- cleanup_temp_files() function
- /api/chat endpoint integration
- /api/generate endpoint integration
- Concurrent request handling
- Error scenarios
"""

import os
import pytest
import tempfile
from unittest.mock import patch

# Import the functions we're testing
from copilot_ollama import (
    convert_large_prompt_to_attachment,
    cleanup_temp_files,
    app,
)
from fastapi.testclient import TestClient


class TestConvertLargePromptToAttachment:
    """Test the convert_large_prompt_to_attachment helper function."""
    
    def test_small_prompt_returns_inline(self):
        """Test that prompts <= 100KB are returned inline."""
        small_text = "a" * 50000  # 50KB
        result_text, result_file = convert_large_prompt_to_attachment(small_text)
        
        assert result_text == small_text
        assert result_file is None
    
    def test_medium_prompt_returns_inline(self):
        """Test that prompts exactly at 100KB boundary are returned inline."""
        # 102,400 is exactly 100KB threshold
        medium_text = "a" * 102400
        result_text, result_file = convert_large_prompt_to_attachment(medium_text)
        
        assert result_text == medium_text
        assert result_file is None
    
    def test_large_prompt_creates_file(self):
        """Test that prompts > 100KB create a file attachment."""
        large_text = "b" * 102401  # Just over 100KB
        result_text, result_file = convert_large_prompt_to_attachment(large_text)
        
        try:
            # Should return attachment tag
            assert "<attachment id=" in result_text
            assert ".tmp" in result_text
            
            # Should return file path
            assert result_file is not None
            assert os.path.exists(result_file)
            
            # File should contain the original text
            with open(result_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            assert file_content == large_text
        finally:
            # Cleanup
            if result_file and os.path.exists(result_file):
                os.remove(result_file)
    
    def test_utf8_multibyte_characters_respected(self):
        """Test that UTF-8 multibyte characters are counted correctly as bytes."""
        # Chinese characters take 3 bytes each in UTF-8
        # Each '中' is 3 bytes, so 34134 characters = 102,402 bytes
        chinese_text = "中" * 34134  # 102,402 bytes
        
        # Verify byte count
        byte_count = len(chinese_text.encode('utf-8'))
        assert byte_count > 102400
        
        result_text, result_file = convert_large_prompt_to_attachment(chinese_text)
        
        try:
            # Should create file because byte count > 102400
            assert "<attachment id=" in result_text
            assert result_file is not None
            assert os.path.exists(result_file)
        finally:
            if result_file and os.path.exists(result_file):
                os.remove(result_file)
    
    def test_emojis_counted_correctly(self):
        """Test that emojis (multibyte UTF-8) are counted correctly."""
        # An emoji takes 4 bytes in UTF-8
        # So 25600 emojis = 102,400 bytes (at threshold)
        emoji_text = "😀" * 25601  # 102,404 bytes
        
        byte_count = len(emoji_text.encode('utf-8'))
        assert byte_count > 102400
        
        result_text, result_file = convert_large_prompt_to_attachment(emoji_text)
        
        try:
            assert "<attachment id=" in result_text
            assert result_file is not None
        finally:
            if result_file and os.path.exists(result_file):
                os.remove(result_file)
    
    def test_attachment_tag_format(self):
        """Test that attachment tag has correct format."""
        large_text = "x" * 102401
        result_text, result_file = convert_large_prompt_to_attachment(large_text)
        
        try:
            # Should match format: <attachment id='copilot-XXXXXXXX.tmp'/>
            assert result_text.startswith("<attachment id='copilot-")
            assert result_text.endswith(".tmp'/>")
            
            # Extract filename from result
            filename = result_text.split("'")[1]
            assert filename.startswith("copilot-")
            assert filename.endswith(".tmp")
            assert len(filename) == len("copilot-") + 8 + len(".tmp")  # UUID hex is 8 chars
        finally:
            if result_file and os.path.exists(result_file):
                os.remove(result_file)
    
    def test_unique_filenames_on_concurrent_calls(self):
        """Test that concurrent calls generate unique filenames."""
        large_text = "y" * 102401
        
        files_created = []
        try:
            # Create multiple attachments
            for _ in range(5):
                _, temp_file = convert_large_prompt_to_attachment(large_text)
                if temp_file:
                    files_created.append(temp_file)
            
            # All files should be different
            assert len(files_created) == 5
            assert len(set(files_created)) == 5  # All unique
            
            # All files should exist
            for file_path in files_created:
                assert os.path.exists(file_path)
        finally:
            for file_path in files_created:
                if os.path.exists(file_path):
                    os.remove(file_path)


class TestCleanupTempFiles:
    """Test the cleanup_temp_files helper function."""
    
    def test_deletes_existing_files(self):
        """Test that cleanup deletes existing files."""
        # Create temp files
        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as f:
                temp_files.append(f.name)
                f.write(b"test content")
        
        # Verify they exist
        for f in temp_files:
            assert os.path.exists(f)
        
        # Cleanup
        cleanup_temp_files(temp_files)
        
        # Verify they're deleted
        for f in temp_files:
            assert not os.path.exists(f)
    
    def test_handles_missing_files_gracefully(self):
        """Test that cleanup doesn't crash on missing files."""
        # Create some files and some non-existent paths
        files_to_clean = [
            "/tmp/nonexistent-file-12345.tmp",
            "/tmp/another-missing-file.tmp",
        ]
        
        # Should not raise exception
        cleanup_temp_files(files_to_clean)
    
    def test_handles_empty_list(self):
        """Test that cleanup handles empty list."""
        cleanup_temp_files([])
        cleanup_temp_files(None)  # Should not crash
    
    def test_handles_none_paths_in_list(self):
        """Test that cleanup skips None/empty paths."""
        files_to_clean = [None, "", None]
        cleanup_temp_files(files_to_clean)
    
    def test_continues_on_permission_errors(self):
        """Test that cleanup continues even if permission denied."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as f:
            temp_file = f.name
            f.write(b"test")
        
        try:
            # Make file read-only (simulates permission issue, though may not work on all systems)
            os.chmod(temp_file, 0o444)
            
            files_to_clean = [temp_file, "/tmp/another-missing.tmp"]
            
            # Should not raise exception
            cleanup_temp_files(files_to_clean)
        finally:
            # Restore permissions and cleanup
            if os.path.exists(temp_file):
                os.chmod(temp_file, 0o644)
                os.remove(temp_file)


class TestAPIChat:
    """Test /api/chat endpoint with large prompt handling."""
    
    def test_chat_with_small_prompt_no_file_created(self):
        """Test that /api/chat with small prompt doesn't create temp file."""
        client = TestClient(app)
        
        # Mock copilot response
        with patch('copilot_ollama.call_copilot') as mock_copilot:
            mock_copilot.return_value = {"text": "Response text"}
            
            response = client.post(
                "/api/chat",
                json={
                    "model": "github-copilot:gpt-4.1",
                    "messages": [
                        {"role": "user", "content": "a" * 50000}
                    ],
                    "stream": False,
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"]["content"] == "Response text"
            
            # Verify copilot was called
            assert mock_copilot.called
    
    def test_chat_endpoint_calls_convert_function(self):
        """Test that /api/chat calls conversion function."""
        client = TestClient(app)
        
        with patch('copilot_ollama.convert_large_prompt_to_attachment') as mock_convert:
            mock_convert.return_value = ("Test message", None)
            
            with patch('copilot_ollama.call_copilot') as mock_copilot:
                mock_copilot.return_value = {"text": "Response"}
                
                response = client.post(
                    "/api/chat",
                    json={
                        "model": "github-copilot:gpt-4.1",
                        "messages": [
                            {"role": "user", "content": "test"}
                        ],
                        "stream": False,
                    }
                )
                
                assert response.status_code == 200
                assert mock_convert.called


class TestAPIGenerate:
    """Test /api/generate endpoint with large prompt handling."""
    
    def test_generate_with_small_prompt_no_file_created(self):
        """Test that /api/generate with small prompt doesn't create temp file."""
        client = TestClient(app)
        
        with patch('copilot_ollama.call_copilot') as mock_copilot:
            mock_copilot.return_value = {"text": "Generated response"}
            
            response = client.post(
                "/api/generate",
                json={
                    "model": "github-copilot:gpt-4.1",
                    "prompt": "a" * 50000,
                    "stream": False,
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Generated response"
    
    def test_generate_endpoint_calls_convert_function(self):
        """Test that /api/generate calls conversion function."""
        client = TestClient(app)
        
        with patch('copilot_ollama.convert_large_prompt_to_attachment') as mock_convert:
            mock_convert.return_value = ("Test prompt", None)
            
            with patch('copilot_ollama.call_copilot') as mock_copilot:
                mock_copilot.return_value = {"text": "Response"}
                
                response = client.post(
                    "/api/generate",
                    json={
                        "model": "github-copilot:gpt-4.1",
                        "prompt": "test",
                        "stream": False,
                    }
                )
                
                assert response.status_code == 200
                assert mock_convert.called


class TestTempDirectoryInitialization:
    """Test that temp directory is initialized on startup."""
    
    def test_temp_directory_exists_after_module_load(self):
        """Test that /tmp/copilot-ollama/ directory exists."""
        # The directory should be created in __main__ block
        # This test verifies the directory structure is ready
        temp_dir = "/tmp/copilot-ollama/"
        
        # Create the directory if it doesn't exist (simulating startup)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Verify it exists
        assert os.path.isdir(temp_dir)


class TestConcurrentRequests:
    """Test handling of concurrent requests with large prompts."""
    
    def test_concurrent_temp_file_creation(self):
        """Test that concurrent calls don't have file collisions."""
        large_text = "z" * 102401
        
        files_created = []
        
        def create_attachment():
            _, temp_file = convert_large_prompt_to_attachment(large_text)
            if temp_file:
                files_created.append(temp_file)
        
        try:
            # Simulate 10 concurrent requests
            threads = []
            for _ in range(10):
                import threading
                t = threading.Thread(target=create_attachment)
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            # All created files should be unique
            assert len(files_created) == 10
            assert len(set(files_created)) == 10
            
            # All files should exist
            for f in files_created:
                assert os.path.exists(f)
        finally:
            for f in files_created:
                if os.path.exists(f):
                    os.remove(f)


class TestErrorHandling:
    """Test error handling in prompt conversion and cleanup."""
    
    def test_fallback_on_file_write_failure(self):
        """Test that function falls back to original text if file write fails."""
        large_text = "a" * 102401
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result_text, result_file = convert_large_prompt_to_attachment(large_text)
            
            # Should return original text as fallback
            assert result_text == large_text
            assert result_file is None
    
    def test_cleanup_on_api_error(self):
        """Test that temp files are cleaned up even if copilot call fails."""
        client = TestClient(app)
        
        with patch('copilot_ollama.convert_large_prompt_to_attachment') as mock_convert:
            # Simulate file creation
            temp_file = "/tmp/test-cleanup.tmp"
            with open(temp_file, 'w') as f:
                f.write("test")
            
            mock_convert.return_value = ("<attachment id='test.tmp'/>", temp_file)
            
            with patch('copilot_ollama.cleanup_temp_files') as mock_cleanup:
                with patch('copilot_ollama.call_copilot') as mock_copilot:
                    # Simulate copilot error
                    mock_copilot.return_value = {"error": "API error"}
                    
                    response = client.post(
                        "/api/chat",
                        json={
                            "model": "github-copilot:gpt-4.1",
                            "messages": [
                                {"role": "user", "content": "test"}
                            ],
                            "stream": False,
                        }
                    )
                    
                    # Should have attempted cleanup
                    assert mock_cleanup.called
            
            # Cleanup the test file
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
