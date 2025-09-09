"""
QbitShield v2.0 Python SDK (packaged from src/qbitshield)

Aligned to v2 API prefix and headers:
- Base URL default: https://api.qbitshield.com/api/v2
- Header: X-API-Key
"""

import asyncio
import aiohttp
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class KeyGenerationResult:
    key_id: int
    key: str
    entropy: float
    latency_ms: float
    timestamp: str
    qasm: Optional[str] = None
    qasm_base64: Optional[str] = None
    modulation: str = "prime_harmonics_v2"
    hash_proof: Optional[str] = None
    noise_profile: str = "optimized_simulator_v2"
    prime_sequence: Optional[List[int]] = None
    harmonic_factors: Optional[List[float]] = None
    security_level: int = 256
    performance_metrics: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    valid: bool
    key_id: Optional[int]
    verification_details: Dict[str, Any]
    timestamp: str


@dataclass
class BulkGenerationResult:
    success: bool
    keys_generated: int
    security_level: int
    performance_metrics: Dict[str, Any]
    keys: List[Dict[str, Any]]


class QbitShieldError(Exception):
    pass


class AuthenticationError(QbitShieldError):
    pass


class RateLimitError(QbitShieldError):
    pass


class ValidationError(QbitShieldError):
    pass


class QbitShieldClient:
    """QbitShield v2.0 Python SDK Client"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.qbitshield.com/api/v2",
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        if not api_key:
            raise AuthenticationError("API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.qkd = QKDService(self)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "QbitShield-SDK/2.0.1 Python",
            "Accept": "application/json",
        }

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            data = response.json()
        except ValueError:
            raise QbitShieldError(f"Invalid JSON response: {response.text}")

        if response.status_code == 401:
            raise AuthenticationError(data.get("detail", "Authentication failed"))
        elif response.status_code == 403:
            raise AuthenticationError(data.get("detail", "Insufficient permissions"))
        elif response.status_code == 429:
            raise RateLimitError(data.get("detail", "Rate limit exceeded"))
        elif response.status_code >= 400:
            error_detail = data.get("detail", f"HTTP {response.status_code} error")
            if isinstance(error_detail, dict):
                error_detail = error_detail.get("message", str(error_detail))
            raise QbitShieldError(f"API error: {error_detail}")
        return data

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            raise QbitShieldError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise QbitShieldError("Connection error")
        except requests.exceptions.RequestException as e:
            raise QbitShieldError(f"Request failed: {e}")

    async def _make_async_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    ssl=self.verify_ssl,
                ) as response:
                    try:
                        data = await response.json()
                    except ValueError:
                        text = await response.text()
                        raise QbitShieldError(f"Invalid JSON response: {text}")

                    if response.status == 401:
                        raise AuthenticationError(data.get("detail", "Authentication failed"))
                    elif response.status == 403:
                        raise AuthenticationError(data.get("detail", "Insufficient permissions"))
                    elif response.status == 429:
                        raise RateLimitError(data.get("detail", "Rate limit exceeded"))
                    elif response.status >= 400:
                        error_detail = data.get("detail", f"HTTP {response.status} error")
                        if isinstance(error_detail, dict):
                            error_detail = error_detail.get("message", str(error_detail))
                        raise QbitShieldError(f"API error: {error_detail}")
                    return data
        except asyncio.TimeoutError:
            raise QbitShieldError("Request timeout")
        except aiohttp.ClientError as e:
            raise QbitShieldError(f"Request failed: {e}")


class QKDService:
    def __init__(self, client: QbitShieldClient):
        self.client = client

    def generate_key(
        self,
        security_level: int = 256,
        enable_nist_validation: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KeyGenerationResult:
        request_data = {
            "security_level": security_level,
            "enable_nist_validation": enable_nist_validation,
            "metadata": metadata,
        }
        response = self.client._make_request("POST", "/generate", request_data)
        return KeyGenerationResult(
            key_id=response["key_id"],
            key=response["key"],
            entropy=response.get("entropy", 0.0),
            latency_ms=response.get("latency_ms", 0.0),
            timestamp=response["timestamp"],
            qasm=response.get("qasm_circuit") or response.get("qasm"),
            qasm_base64=response.get("qasm_base64"),
            modulation=response.get("modulation", "prime_harmonics_v2"),
            hash_proof=response.get("hash_proof"),
            noise_profile=response.get("noise_profile", "optimized_simulator_v2"),
            prime_sequence=response.get("prime_sequence"),
            harmonic_factors=response.get("harmonic_factors"),
            security_level=response.get("security_level", security_level),
            performance_metrics=response.get("performance_metrics"),
        )

    async def generate_key_async(
        self,
        security_level: int = 256,
        enable_nist_validation: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KeyGenerationResult:
        request_data = {
            "security_level": security_level,
            "enable_nist_validation": enable_nist_validation,
            "metadata": metadata,
        }
        response = await self.client._make_async_request("POST", "/generate", request_data)
        return KeyGenerationResult(
            key_id=response["key_id"],
            key=response["key"],
            entropy=response.get("entropy", 0.0),
            latency_ms=response.get("latency_ms", 0.0),
            timestamp=response["timestamp"],
            qasm=response.get("qasm_circuit") or response.get("qasm"),
            qasm_base64=response.get("qasm_base64"),
            modulation=response.get("modulation", "prime_harmonics_v2"),
            hash_proof=response.get("hash_proof"),
            noise_profile=response.get("noise_profile", "optimized_simulator_v2"),
            prime_sequence=response.get("prime_sequence"),
            harmonic_factors=response.get("harmonic_factors"),
            security_level=response.get("security_level", security_level),
            performance_metrics=response.get("performance_metrics"),
        )

    def validate_key(self, key: str, qasm: str, hash_proof: str) -> ValidationResult:
        request_data = {"key": key, "qasm_circuit": qasm, "hash_proof": hash_proof}
        response = self.client._make_request("POST", "/validate", request_data)
        return ValidationResult(
            valid=response["valid"],
            key_id=response.get("key_id"),
            verification_details=response.get("validation_details", {}),
            timestamp=response["timestamp"],
        )

    def get_metrics(self, hours: int = 24) -> Dict[str, Any]:
        return self.client._make_request("GET", "/metrics", params={"hours": hours})

    def bulk_generate(
        self, count: int, security_level: int = 256, enable_nist_validation: bool = True
    ) -> BulkGenerationResult:
        keys: List[Dict[str, Any]] = []
        perf: Dict[str, Any] = {"total_latency_ms": 0.0}
        for _ in range(count):
            r = self.generate_key(security_level, enable_nist_validation)
            keys.append({"key_id": r.key_id, "key": r.key})
            perf["total_latency_ms"] += r.latency_ms
        return BulkGenerationResult(
            success=True,
            keys_generated=len(keys),
            security_level=security_level,
            performance_metrics=perf,
            keys=keys,
        )


def generate_quantum_key(
    api_key: str, security_level: int = 256, base_url: str = "https://api.qbitshield.com/api/v2"
) -> KeyGenerationResult:
    client = QbitShieldClient(api_key=api_key, base_url=base_url)
    return client.qkd.generate_key(security_level=security_level)


def validate_quantum_key(
    api_key: str, key: str, qasm: str, hash_proof: str, base_url: str = "https://api.qbitshield.com/api/v2"
) -> ValidationResult:
    client = QbitShieldClient(api_key=api_key, base_url=base_url)
    return client.qkd.validate_key(key=key, qasm=qasm, hash_proof=hash_proof)

