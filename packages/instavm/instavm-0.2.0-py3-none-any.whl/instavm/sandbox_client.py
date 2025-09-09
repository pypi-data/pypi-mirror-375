import requests
import time
import json
from typing import Optional, Dict, Any, Generator, Callable
from .exceptions import InstaVMError, AuthenticationError, SessionError, ExecutionError, NetworkError, RateLimitError
class InstaVM:
    def __init__(self, api_key=None, base_url="https://api.instavm.io", timeout=300, max_retries=0):
        self.base_url = base_url
        self.api_key = api_key
        self.session_id = None
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

        if self.api_key:
            self.start_session()

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic and proper error handling"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )

                # Handle specific HTTP status codes
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key or session expired")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code >= 500:
                    # More details for debugging
                    status_reason = response.reason or ""
                    try:
                        error_text = response.text.strip()
                    except Exception:
                        error_text = "<No response body>"

                    if response.status_code == 504:
                        raise NetworkError(
                            f"504 Gateway Timeout: The server (or a proxy) didn't get a timely response from the upstream service.\n"
                            f"Reason: {status_reason}\n"
                            f"Details: {error_text}"
                        )
                    else:
                        raise NetworkError(
                            f"Server error: {response.status_code} {status_reason}\n"
                            f"Details: {error_text}"
                        )


                response.raise_for_status()
                return response

            except requests.exceptions.Timeout as e:
                last_exception = NetworkError(f"Request timeout after {self.timeout}s")
            except requests.exceptions.ConnectionError as e:
                last_exception = NetworkError(f"Connection failed: {str(e)}")
            except (AuthenticationError, RateLimitError) as e:
                # Don't retry these
                raise e
            except requests.exceptions.HTTPError as e:
                if e.response.status_code < 500:
                    # Client errors shouldn't be retried
                    raise InstaVMError(f"HTTP {e.response.status_code}: {e.response.text}")
                last_exception = NetworkError(f"HTTP error: {str(e)}")

            if attempt < self.max_retries:
                # Exponential backoff
                time.sleep(2 ** attempt)

        raise last_exception or NetworkError("Max retries exceeded")

    def start_session(self):
        if not self.api_key:
            raise AuthenticationError("API key not set. Please provide an API key or create one first.")

        url = f"{self.base_url}/v1/sessions/session"
        data = {"api_key": self.api_key}

        try:
            response = self._make_request("POST", url, json=data)
            result = response.json()
            self.session_id = result.get("session_id")
            if not self.session_id:
                raise SessionError("Failed to get session ID from server response")
            return self.session_id
        except Exception as e:
            if isinstance(e, (InstaVMError)):
                raise e
            raise SessionError(f"Failed to start session: {str(e)}")

    def execute(self, command: str, language: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        if not self.session_id:
            raise SessionError("Session ID not set. Please start a session first.")

        url = f"{self.base_url}/execute"
        data = {
            "command": command,
            "api_key": self.api_key,
            "session_id": self.session_id,
        }
        if language:
            data["language"] = language
        if timeout is not None:
            data["timeout"] = timeout

        try:
            response = self._make_request("POST", url, json=data)
            return response.json()
        except Exception as e:
            if isinstance(e, InstaVMError):
                raise e
            raise ExecutionError(f"Failed to execute command: {str(e)}")

    def get_usage(self) -> Dict[str, Any]:
        if not self.session_id:
            raise SessionError("Session ID not set. Please start a session first.")

        url = f"{self.base_url}/v1/sessions/usage/{self.session_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = self._make_request("GET", url, headers=headers)
            return response.json()
        except Exception as e:
            if isinstance(e, InstaVMError):
                raise e
            raise InstaVMError(f"Failed to get usage: {str(e)}")

    def upload_file(self, file_path: str, remote_path: str,
                    recursive: bool = False) -> Dict[str, Any]:
        if not self.session_id:
            raise SessionError("Session ID not set. Please start a session first.")

        url = f"{self.base_url}/upload"
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f)}
                data = {
                    "remote_path": remote_path,
                    "api_key": self.api_key,
                    "session_id": self.session_id,
                    "recursive": str(recursive).lower()  # ensures 'true'/'false'
                }
                response = self._make_request("POST", url, data=data, files=files)
            return response.json()
        except FileNotFoundError:
            raise InstaVMError(f"File not found: {file_path}")
        except Exception as e:
            if isinstance(e, InstaVMError):
                raise
            raise InstaVMError(f"Failed to upload file: {str(e)}")

    def execute_async(self, command: str, language: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute command asynchronously"""
        if not self.session_id:
            raise SessionError("Session ID not set. Please start a session first.")

        url = f"{self.base_url}/execute_async"
        data = {
            "command": command,
            "api_key": self.api_key,
            "session_id": self.session_id,
        }
        
        if language:
            data["language"] = language
        if timeout is not None:
            data["timeout"] = timeout

        try:
            response = self._make_request("POST", url, json=data)
            return response.json()
        except Exception as e:
            if isinstance(e, InstaVMError):
                raise e
            raise ExecutionError(f"Failed to execute command asynchronously: {str(e)}")

    def execute_streaming(self, command: str, on_output: Optional[Callable[[str], None]] = None) -> Generator[str, None, None]:
        """Execute command with real-time streaming output (deprecated - streaming not supported by current API)"""
        import warnings
        warnings.warn("execute_streaming is deprecated. The API does not support streaming execution. Use execute() or execute_async() instead.", DeprecationWarning, stacklevel=2)
        
        # Fallback to regular execution
        result = self.execute(command)
        output = result.get('output', str(result))
        if on_output:
            on_output(output)
        yield output

    def close_session(self) -> bool:
        """Close the current session (sessions auto-expire on server side)"""
        if not self.session_id:
            return True
        
        # Note: API doesn't provide explicit session deletion endpoint
        # Sessions will auto-expire on the server side
        print(f"Info: Session {self.session_id} will auto-expire on server side.")
        self.session_id = None
        return True

    def is_session_active(self) -> bool:
        """Check if current session is still active by attempting to get usage"""
        try:
            self.get_usage()
            return True
        except (SessionError, AuthenticationError):
            return False
        except Exception:
            return False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically close session"""
        self.close_session()
        # Parameters are standard context manager signature