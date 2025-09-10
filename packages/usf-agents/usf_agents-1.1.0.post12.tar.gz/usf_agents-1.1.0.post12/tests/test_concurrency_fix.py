"""
Test suite for the USFAgent concurrency fix.

This test verifies that the request queueing system properly handles
concurrent calls without throwing sequencing errors.
"""
import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from usf_agents.usfAgent import USFAgent
from usf_agents.runtime.concurrency import ConcurrencyManager


class MockUSFAgent(USFAgent):
    """Mock USFAgent for testing without requiring real API calls."""
    
    def __init__(self, config=None):
        # Initialize with minimal config to avoid API key validation
        if config is None:
            config = {}
        
        # Set a dummy API key to pass validation
        config['api_key'] = 'test-api-key'
        
        super().__init__(config)
        
        # Replace the internal run method with a mock
        self._original_run_internal = self._run_internal
        self._run_internal = self._mock_run_internal
        
        # Add delay simulation for testing
        self.processing_delay = config.get('processing_delay', 0.1)
    
    async def _mock_run_internal(self, messages, options=None):
        """Mock implementation that simulates processing time."""
        if options is None:
            options = {}
        
        # Simulate processing time
        await asyncio.sleep(self.processing_delay)
        
        # Return a simple response
        yield {
            'type': 'final_answer',
            'content': f'Mock response for: {messages if isinstance(messages, str) else "complex message"}'
        }


@pytest.mark.asyncio
async def test_concurrent_calls_no_sequencing_error():
    """Test that concurrent calls don't raise sequencing errors."""
    
    # Create agent with short processing delay
    agent = MockUSFAgent({'processing_delay': 0.2})
    
    async def make_request(message: str):
        """Make a single request and collect results."""
        results = []
        async for chunk in agent.run(message):
            results.append(chunk)
        return results
    
    # Make multiple concurrent requests
    messages = [f"Test message {i}" for i in range(5)]
    
    start_time = time.time()
    
    # This should NOT raise "USFAgent Sequencing Error"
    tasks = [make_request(msg) for msg in messages]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    
    # Verify all requests completed successfully
    assert len(results) == 5
    for i, result in enumerate(results):
        assert len(result) == 1
        assert result[0]['type'] == 'final_answer'
        assert f"Test message {i}" in result[0]['content']
    
    # Since requests are queued, total time should be roughly:
    # 5 requests * 0.2 seconds each = ~1 second
    # Allow some tolerance for overhead
    assert end_time - start_time >= 0.8  # At least 0.8 seconds (sequential processing)
    assert end_time - start_time <= 1.5  # But not too much overhead


@pytest.mark.asyncio
async def test_queue_stats():
    """Test that concurrency manager provides accurate statistics."""
    
    agent = MockUSFAgent({'processing_delay': 0.1})
    
    # Check initial stats
    stats = agent._concurrency_manager.get_stats()
    assert stats['total_requests'] == 0
    assert stats['completed_requests'] == 0
    assert stats['failed_requests'] == 0
    
    # Make some requests
    async def make_request(message: str):
        async for chunk in agent.run(message):
            pass
    
    # Make concurrent requests
    tasks = [make_request(f"Message {i}") for i in range(3)]
    await asyncio.gather(*tasks)
    
    # Check final stats
    stats = agent._concurrency_manager.get_stats()
    assert stats['total_requests'] == 3
    assert stats['completed_requests'] == 3
    assert stats['failed_requests'] == 0
    assert stats['success_rate'] == 1.0


@pytest.mark.asyncio
async def test_queue_timeout():
    """Test that requests timeout properly."""
    
    # Create agent with long processing delay
    agent = MockUSFAgent({'processing_delay': 2.0})
    
    # Override timeout to be very short
    agent._concurrency_manager.default_timeout = 0.5
    
    with pytest.raises(asyncio.TimeoutError):
        async for chunk in agent.run("Test message", {'timeout': 0.5}):
            pass


@pytest.mark.asyncio
async def test_queue_full_error():
    """Test queue capacity limits."""
    
    # Create agent with very small queue and long processing delay
    config = {
        'processing_delay': 1.0,
        'concurrency': {
            'max_queue_size': 2,
            'default_timeout': 5.0
        }
    }
    agent = MockUSFAgent(config)
    
    async def slow_request():
        async for chunk in agent.run("Slow request"):
            pass
    
    # Start requests that will fill the queue
    tasks = []
    
    # First two requests should be queued successfully
    tasks.append(asyncio.create_task(slow_request()))
    tasks.append(asyncio.create_task(slow_request()))
    
    # Give them a moment to enter the queue
    await asyncio.sleep(0.1)
    
    # Third request should raise QueueFull error
    with pytest.raises(asyncio.QueueFull):
        await slow_request()
    
    # Clean up
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_backward_compatibility():
    """Test that existing code still works with the new implementation."""
    
    agent = MockUSFAgent({'processing_delay': 0.1})
    
    # Single request (like existing code)
    result = []
    async for chunk in agent.run("Single request"):
        result.append(chunk)
    
    assert len(result) == 1
    assert result[0]['type'] == 'final_answer'
    assert 'Single request' in result[0]['content']
    
    # Request with options (like existing code)
    result = []
    async for chunk in agent.run(
        [{'role': 'user', 'content': 'Complex request'}], 
        {'temperature': 0.7}
    ):
        result.append(chunk)
    
    assert len(result) == 1
    assert result[0]['type'] == 'final_answer'


def test_concurrency_manager_creation():
    """Test that ConcurrencyManager is properly initialized."""
    
    agent = MockUSFAgent({
        'concurrency': {
            'max_queue_size': 50,
            'default_timeout': 120.0
        }
    })
    
    assert agent._concurrency_manager.max_queue_size == 50
    assert agent._concurrency_manager.default_timeout == 120.0
    assert not agent._concurrency_manager._is_running  # Should start when first request comes in


if __name__ == "__main__":
    # Simple demonstration that can be run directly
    async def demo():
        print("🚀 Demonstrating USFAgent Concurrency Fix")
        print("=" * 50)
        
        agent = MockUSFAgent({'processing_delay': 0.2})
        
        print("Making 3 concurrent requests...")
        start_time = time.time()
        
        async def demo_request(i):
            print(f"  Starting request {i}")
            async for chunk in agent.run(f"Demo message {i}"):
                print(f"  ✓ Request {i}: {chunk['content']}")
        
        # This would have failed with "USFAgent Sequencing Error" before the fix
        tasks = [demo_request(i) for i in range(3)]
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        print(f"\n✅ All requests completed in {end_time - start_time:.2f} seconds")
        
        # Show stats
        stats = agent._concurrency_manager.get_stats()
        print(f"📊 Stats: {stats['total_requests']} total, {stats['completed_requests']} completed, success rate: {stats['success_rate']:.1%}")
        
        print("\n🎉 Concurrency fix is working!")
    
    asyncio.run(demo())