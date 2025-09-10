import aiohttp
import asyncio
from typing import Optional, Dict, Any
import ssl
import certifi
from aiohttp import TCPConnector, ClientTimeout
import structlog
from .circuit_breaker import CircuitBreaker

logger = structlog.get_logger()


class AsyncHTTPTransport:
    """Async HTTP/HTTPS transport with connection pooling"""
    
    def __init__(self, config: 'Config'):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=config.performance.circuit_breaker_threshold,
            recovery_timeout=config.performance.circuit_breaker_timeout
        ) if config.performance.enable_circuit_breaker else None
        
    async def initialize(self):
        """Initialize transport with connection pool"""
        ssl_context = self._create_ssl_context()
        
        connector = TCPConnector(
            limit=self.config.performance.connection_pool_size,
            limit_per_host=self.config.performance.connection_pool_size // 2,
            ssl=ssl_context,
            force_close=True,
            enable_cleanup_closed=True
        )
        
        timeout = ClientTimeout(
            total=self.config.connection.timeout,
            connect=self.config.connection.timeout / 3,
            sock_read=self.config.connection.timeout / 3
        )
        
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'CMS-NBI-Client/2.0'}
        )
        
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with proper configuration"""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        if self.config.connection.ca_bundle:
            ssl_context.load_verify_locations(self.config.connection.ca_bundle)
            
        if not self.config.connection.verify_ssl:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
        return ssl_context
    
    async def request(
        self,
        method: str,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None
    ) -> aiohttp.ClientResponse:
        """Execute HTTP request with circuit breaker"""
        if not self._session:
            await self.initialize()
            
        if self._circuit_breaker:
            return await self._circuit_breaker.call(
                self._do_request, method, url, data, headers, auth
            )
        else:
            return await self._do_request(method, url, data, headers, auth)
    
    async def _do_request(
        self,
        method: str,
        url: str,
        data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None
    ) -> aiohttp.ClientResponse:
        """Execute actual HTTP request"""
        async with self._session.request(
            method=method,
            url=url,
            data=data,
            headers=headers,
            auth=auth
        ) as response:
            response.raise_for_status()
            return response
    
    async def close(self):
        """Close transport connections"""
        if self._session:
            await self._session.close()
            # Wait for connection cleanup
            await asyncio.sleep(0.25)