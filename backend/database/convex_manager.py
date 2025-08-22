"""
Convex Database Connection Manager
Handles all Convex client operations with singleton pattern
"""

import os
import logging
import time
from typing import Optional, Dict, Any, TypeVar, Callable
from convex import ConvexClient
import asyncio
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

T = TypeVar('T')


class ConvexManager:
    """Singleton manager for Convex database operations"""
    
    _instance: Optional['ConvexManager'] = None
    _client: Optional[ConvexClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            convex_url = os.getenv("CONVEX_URL")
            
            if not convex_url:
                logger.error("Convex URL not found in environment variables")
                raise ValueError("Missing CONVEX_URL")
            
            try:
                # ConvexClient takes only the URL, authentication is handled via the URL
                self._client = ConvexClient(convex_url)
                logger.info("Convex client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Convex client: {e}")
                raise
    
    @property
    def client(self) -> ConvexClient:
        """Get the Convex client instance"""
        if self._client is None:
            raise RuntimeError("Convex client not initialized")
        return self._client
    
    async def _retry_with_backoff(
        self,
        operation: Callable,
        operation_name: str,
        max_retries: int = 3,
        base_delay: float = 0.1,
        max_delay: float = 2.0
    ) -> Optional[T]:
        """
        Execute an operation with exponential backoff retry logic
        
        Args:
            operation: The operation to execute
            operation_name: Name for logging
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            
        Returns:
            Operation result or None if all retries failed
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                result = await operation()
                if attempt > 0:
                    logger.info(f"{operation_name} succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exception = e
                
                # Don't retry on certain errors
                error_msg = str(e).lower()
                if any(x in error_msg for x in ['invalid', 'not found', 'permission', 'unauthorized']):
                    logger.error(f"{operation_name} failed with non-retryable error: {e}")
                    return None
                
                if attempt < max_retries - 1:
                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        base_delay * (2 ** attempt) + random.uniform(0, 0.1),
                        max_delay
                    )
                    logger.warning(
                        f"{operation_name} failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {delay:.2f}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"{operation_name} failed after {max_retries} attempts: {e}"
                    )
        
        return None
    
    async def mutation(self, name: str, data: Dict[str, Any], retry: bool = True) -> Optional[Any]:
        """
        Execute a Convex mutation asynchronously with retry logic
        
        Args:
            name: Mutation name (e.g., 'create_flight')
            data: Data to pass to the mutation
            retry: Whether to enable retry logic (default: True)
            
        Returns:
            Result from mutation or None if failed
        """
        async def execute():
            # Convex mutations are in mutations.js file
            mutation_path = f"mutations.js:{name}" if not name.startswith("mutations.") else name
            logger.debug(f"Executing mutation {mutation_path} with data: {data}")
            return await asyncio.to_thread(
                self._client.mutation,
                mutation_path,
                data
            )
        
        if retry:
            result = await self._retry_with_backoff(
                execute,
                f"Mutation {name}",
                max_retries=3
            )
        else:
            try:
                result = await execute()
                logger.debug(f"Mutation {name} executed successfully")
            except Exception as e:
                logger.error(f"Convex mutation {name} failed: {e}")
                result = None
        
        return result
    
    async def query(self, name: str, data: Dict[str, Any] = None, retry: bool = True) -> Optional[Any]:
        """
        Execute a Convex query asynchronously with retry logic
        
        Args:
            name: Query name
            data: Query parameters
            retry: Whether to enable retry logic (default: True)
            
        Returns:
            Query result or None if failed
        """
        async def execute():
            return await asyncio.to_thread(
                self._client.query,
                f"queries:{name}",
                data or {}
            )
        
        if retry:
            result = await self._retry_with_backoff(
                execute,
                f"Query {name}",
                max_retries=2  # Fewer retries for queries
            )
        else:
            try:
                result = await execute()
                logger.debug(f"Query {name} executed successfully")
            except Exception as e:
                logger.error(f"Convex query {name} failed: {e}")
                result = None
        
        return result
    
    async def batch_mutations(
        self,
        mutations: list[tuple[str, Dict[str, Any]]],
        continue_on_error: bool = True
    ) -> list[Optional[Any]]:
        """
        Execute multiple mutations in parallel with error handling
        
        Args:
            mutations: List of (mutation_name, data) tuples
            continue_on_error: Whether to continue if a mutation fails
            
        Returns:
            List of results (None for failed mutations)
        """
        tasks = []
        for mutation_name, mutation_data in mutations:
            tasks.append(self.mutation(mutation_name, mutation_data))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                mutation_name = mutations[i][0]
                logger.error(f"Batch mutation {mutation_name} failed: {result}")
                if not continue_on_error:
                    raise result
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results


def get_convex_manager() -> ConvexManager:
    """Get or create the global Convex manager instance"""
    return ConvexManager()