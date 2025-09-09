import json
from typing import Dict, Any, Optional, Union


class Response:
    """Response object similar to requests.Response."""

    def __init__(
            self,
            status_code: int,
            headers: Dict[str, str],
            content: Union[str, bytes],
            url: str,
            request_headers: Dict[str, str],
            tls_version: str = "",
            cipher_suite: str = "",
            ja3_hash: str = ""
    ):
        self.status_code = status_code
        self.headers = headers
        self._raw_content = content
        self.url = url
        self.request = type('Request', (), {
            'headers': request_headers,
            'url': url
        })()

        # TLS info
        self.tls_version = tls_version
        self.cipher_suite = cipher_suite
        self.ja3_hash = ja3_hash

        # Decompress content if needed
        self._content = self._raw_content

        # Parse cookies
        self.cookies = self._parse_cookies()

    @property
    def content(self) -> bytes:
        """Response content as bytes (decompressed)."""
        return self._content

    @property
    def text(self) -> str:
        """Response content as text (decompressed)."""
        # Try to detect encoding from headers
        content_type = self.headers.get('content-type', '')
        encoding = 'utf-8'  # default

        if 'charset=' in content_type:
            try:
                encoding = content_type.split('charset=')[-1].split(';')[0].strip()
            except:
                encoding = 'utf-8'

        try:
            return self._content
        except UnicodeDecodeError:
            # Fallback to utf-8 with error handling
            return self._content.decode('utf-8', errors='replace')

    def json(self) -> Any:
        """Parse response as JSON."""
        return json.loads(self.text)

    @property
    def ok(self) -> bool:
        """Returns True if status_code is less than 400."""
        return self.status_code < 400

    @property
    def is_redirect(self) -> bool:
        """Returns True if this response is a redirect."""
        return self.status_code in (301, 302, 303, 307, 308)

    @property
    def is_permanent_redirect(self) -> bool:
        """Returns True if this response is a permanent redirect."""
        return self.status_code in (301, 308)

    def raise_for_status(self):
        """Raises an HTTPError if status code indicates an error."""
        if not self.ok:
            from .exceptions import TlsClientError
            raise TlsClientError(f"HTTP {self.status_code} Error for URL: {self.url}")

    def _parse_cookies(self) -> Dict[str, str]:
        """Parse cookies from response headers - pragmatic approach."""
        cookies = {}

        set_cookie = self.headers.get('set-cookie', '')
        if not set_cookie:
            return cookies

        # Split by comma, but only if followed by a space and word character
        # This avoids splitting cookie values that contain commas
        import re
        cookie_parts = re.split(r',\s*(?=[a-zA-Z])', set_cookie)

        for cookie in cookie_parts:
            # Get only the name=value part (before first semicolon)
            main_part = cookie.split(';')[0].strip()
            if '=' in main_part:
                name, value = main_part.split('=', 1)
                cookies[name.strip()] = value.strip()

        return cookies

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"

    def __bool__(self) -> bool:
        """Returns True if status_code is less than 400."""
        return self.ok