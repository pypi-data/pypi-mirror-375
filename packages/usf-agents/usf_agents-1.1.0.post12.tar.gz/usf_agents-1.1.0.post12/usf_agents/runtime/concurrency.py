import asyncio
import uuid
import time
from typing import Dict, Any, Optional, Union, List, AsyncGenerator, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum


class RequestStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueuedRequest:
    """Represents a queued request for USFAgent execution."""
    request_id: str
    messages: Union[str, List[Dict[str, Any]]]
    options: Optional[Dict[str, Any]]
    future: asyncio.Future
    created_at: float
    timeout: Optional[float] = None
    status: RequestStatus = RequestStatus.PENDING
    
    def is_expired(self) -> bool:
        """Check if the request has exceeded its timeout."""
        if self.timeout is None:
            return False
        return time.time() - self.created_at > self.timeout


class ConcurrencyManager:
    """
    Manages concurrent access to USFAgent instances through request queueing.
    
    This class ensures that USFAgent instances are accessed sequentially while
    allowing multiple callers to submit requests concurrently. Requests are
    processed in FIFO order with optional timeout handling.
    """
    
    def __init__(self, max_queue_size: int = 100, default_timeout: float = 300.0):
        self.max_queue_size = max_queue_size
        self.default_timeout = default_timeout
        
        # Request queue and processing state
        self._queue: asyncio.Queue[QueuedRequest] = asyncio.Queue(maxsize=max_queue_size)
        self._active_requests: Dict[str, QueuedRequest] = {}
        self._processor_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._shutdown_event = asyncio.Event()
        
        # Statistics
        self._total_requests = 0
        self._completed_requests = 0
        self._failed_requests = 0
        self._cancelled_requests = 0
        
        # The actual USFAgent execution function
        self._executor: Optional[Callable] = None
    
    def set_executor(self, executor: Callable) -> None:
        """Set the executor function that will handle the actual USFAgent run logic."""
        self._executor = executor
    
    async def start(self) -> None:
        """Start the background request processor."""
        if self._is_running:
            return
        
        self._is_running = True
        self._shutdown_event.clear()
        self._processor_task = asyncio.create_task(self._process_requests())
    
    async def stop(self) -> None:
        """Stop the background request processor and cancel pending requests."""
        if not self._is_running:
            return
        
        self._is_running = False
        self._shutdown_event.set()
        
        # Cancel all pending requests
        while not self._queue.empty():
            try:
                request = self._queue.get_nowait()
                request.status = RequestStatus.CANCELLED
                if not request.future.done():
                    request.future.cancel()
                self._cancelled_requests += 1
            except asyncio.QueueEmpty:
                break
        
        # Wait for processor to finish
        if self._processor_task:
            try:
                await asyncio.wait_for(self._processor_task, timeout=5.0)
            except asyncio.TimeoutError:
                self._processor_task.cancel()
                try:
                    await self._processor_task
                except asyncio.CancelledError:
                    pass
            self._processor_task = None
    
    async def submit_request(
        self,
        messages: Union[str, List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Submit a request for USFAgent execution.
        
        Args:
            messages: The messages to process
            options: Optional execution options
            timeout: Optional timeout for this specific request
            
        Returns:
            AsyncGenerator that yields execution results
            
        Raises:
            asyncio.QueueFull: If the queue is at capacity
            asyncio.TimeoutError: If the request times out
            Exception: Any other errors from the USFAgent execution
        """
        if not self._is_running:
            await self.start()
        
        request_id = str(uuid.uuid4())
        future: asyncio.Future = asyncio.Future()
        
        request = QueuedRequest(
            request_id=request_id,
            messages=messages,
            options=options or {},
            future=future,
            created_at=time.time(),
            timeout=timeout or self.default_timeout
        )
        
        try:
            # Add to queue (this will raise QueueFull if at capacity)
            await self._queue.put(request)
            self._active_requests[request_id] = request
            self._total_requests += 1
            
            # Wait for the request to complete
            try:
                result = await future
                # The result should be an async generator
                async for chunk in result:
                    yield chunk
            except asyncio.CancelledError:
                request.status = RequestStatus.CANCELLED
                self._cancelled_requests += 1
                raise
            except Exception as e:
                request.status = RequestStatus.FAILED
                self._failed_requests += 1
                raise
            finally:
                # Clean up
                self._active_requests.pop(request_id, None)
                
        except asyncio.QueueFull:
            raise asyncio.QueueFull(f"Request queue is full (max size: {self.max_queue_size})")
    
    async def _process_requests(self) -> None:
        """Background task that processes requests sequentially."""
        while self._is_running:
            try:
                # Wait for a request or shutdown signal
                try:
                    request = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=1.0  # Check shutdown every second
                    )
                except asyncio.TimeoutError:
                    # Check if we should shutdown
                    if self._shutdown_event.is_set():
                        break
                    continue
                
                # Check if request has expired
                if request.is_expired():
                    request.status = RequestStatus.CANCELLED
                    if not request.future.done():
                        request.future.set_exception(
                            asyncio.TimeoutError(f"Request {request.request_id} expired after {request.timeout}s")
                        )
                    self._cancelled_requests += 1
                    continue
                
                # Process the request
                request.status = RequestStatus.PROCESSING
                try:
                    if self._executor is None:
                        raise RuntimeError("No executor function set")
                    
                    # Execute the actual USFAgent run
                    result = self._executor(request.messages, request.options)
                    
                    # If the executor returns a coroutine, await it
                    if asyncio.iscoroutine(result):
                        result = await result
                    
                    # Set the result (async generator) in the future
                    if not request.future.done():
                        request.future.set_result(result)
                    
                    request.status = RequestStatus.COMPLETED
                    self._completed_requests += 1
                    
                except Exception as e:
                    request.status = RequestStatus.FAILED
                    if not request.future.done():
                        request.future.set_exception(e)
                    self._failed_requests += 1
                
            except Exception as e:
                # Log unexpected errors but continue processing
                print(f"Unexpected error in request processor: {e}")
                continue
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics about request processing."""
        return {
            "total_requests": self._total_requests,
            "completed_requests": self._completed_requests,
            "failed_requests": self._failed_requests,
            "cancelled_requests": self._cancelled_requests,
            "queue_size": self._queue.qsize(),
            "active_requests": len(self._active_requests),
            "is_running": self._is_running,
            "success_rate": (
                self._completed_requests / max(1, self._total_requests - self._cancelled_requests)
                if self._total_requests > 0 else 0.0
            )
        }
    
    def is_queue_full(self) -> bool:
        """Check if the request queue is at capacity."""
        return self._queue.qsize() >= self.max_queue_size
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()