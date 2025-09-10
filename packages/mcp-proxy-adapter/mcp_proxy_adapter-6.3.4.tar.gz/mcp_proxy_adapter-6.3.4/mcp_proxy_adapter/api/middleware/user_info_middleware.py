"""
User Info Middleware

This middleware extracts user information from authentication headers
and sets it in request.state for use by commands.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from typing import Dict, Any, Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from mcp_proxy_adapter.core.logging import logger

# Import mcp_security_framework components
try:
    from mcp_security_framework import AuthManager, PermissionManager
    from mcp_security_framework.schemas.config import (
        AuthConfig, PermissionConfig
    )
    _MCP_SECURITY_AVAILABLE = True
    print("✅ mcp_security_framework available in middleware")
except ImportError:
    _MCP_SECURITY_AVAILABLE = False
    print("⚠️ mcp_security_framework not available in middleware, "
          "using basic auth")


class UserInfoMiddleware(BaseHTTPMiddleware):
    """
    Middleware for setting user information in request.state.

    This middleware extracts user information from authentication headers
    and sets it in request.state for use by commands.
    """
    def __init__(self, app, config: Dict[str, Any]):
        """
        Initialize user info middleware.

        Args:
            app: FastAPI application
            config: Configuration dictionary
        """
        super().__init__(app)
        self.config = config

        # Initialize AuthManager if available
        self.auth_manager = None
        self._security_available = _MCP_SECURITY_AVAILABLE

        if self._security_available:
            try:
                # Get API keys configuration
                security_config = config.get("security", {})
                auth_config = security_config.get("auth", {})
                permissions_config = security_config.get("permissions", {})

                # Check if permissions are enabled
                permissions_enabled = permissions_config.get("enabled", False)
                
                # Create AuthConfig for mcp_security_framework
                mcp_auth_config = AuthConfig(
                    enabled=True,
                    methods=["api_key"],
                    api_keys=auth_config.get("api_keys", {})
                )

                # Initialize PermissionManager only if permissions are enabled
                if permissions_enabled:
                    # Create PermissionConfig for mcp_security_framework
                    mcp_permission_config = PermissionConfig(
                        roles_file=permissions_config.get("roles_file"),
                        default_role=permissions_config.get("default_role", "guest"),
                        admin_role=permissions_config.get("admin_role", "admin"),
                        role_hierarchy=permissions_config.get("role_hierarchy", {}),
                        permission_cache_enabled=permissions_config.get(
                            "permission_cache_enabled", True
                        ),
                        permission_cache_ttl=permissions_config.get(
                            "permission_cache_ttl", 300
                        ),
                        wildcard_permissions=permissions_config.get(
                            "wildcard_permissions", False
                        ),
                        strict_mode=permissions_config.get("strict_mode", True),
                        roles=permissions_config.get("roles", {})
                    )

                    # Initialize PermissionManager first
                    self.permission_manager = PermissionManager(mcp_permission_config)
                else:
                    # Create a minimal PermissionManager when permissions are disabled
                    mcp_permission_config = PermissionConfig(
                        roles_file=None,
                        default_role="guest",
                        admin_role="admin",
                        role_hierarchy={},
                        permission_cache_enabled=False,
                        permission_cache_ttl=300,
                        wildcard_permissions=False,
                        strict_mode=False,
                        roles={}
                    )
                    self.permission_manager = PermissionManager(mcp_permission_config)

                # Initialize AuthManager with permission_manager
                self.auth_manager = AuthManager(
                    mcp_auth_config, self.permission_manager
                )
                logger.info("✅ User info middleware initialized with "
                            "mcp_security_framework")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize AuthManager: {e}")
                self._security_available = False

        if not self._security_available:
            # Fallback to basic API key handling
            security_config = config.get("security", {})
            auth_config = security_config.get("auth", {})
            self.api_keys = auth_config.get("api_keys", {})
            logger.info("ℹ️ User info middleware initialized with basic auth")

    async def dispatch(
        self, request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process request and set user info in request.state.

        Args:
            request: Request object
            call_next: Next handler

        Returns:
            Response object
        """
        # Extract API key from headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            if self.auth_manager and self._security_available:
                try:
                    # Use mcp_security_framework AuthManager
                    auth_result = self.auth_manager.authenticate_api_key(api_key)

                    if auth_result.is_valid:
                        # Set user info from AuthManager result
                        request.state.user = {
                            "id": api_key,
                            "role": (auth_result.roles[0]
                                     if auth_result.roles else "guest"),
                            "roles": auth_result.roles or ["guest"],
                            "permissions": getattr(
                                auth_result, 'permissions', ["read"]
                            )
                        }
                        logger.debug(f"✅ Authenticated user with "
                                     f"mcp_security_framework: "
                                     f"{request.state.user}")
                    else:
                        # Authentication failed
                        request.state.user = {
                            "id": None,
                            "role": "guest",
                            "roles": ["guest"],
                            "permissions": ["read"]
                        }
                        logger.debug(f"❌ Authentication failed for API key: "
                                     f"{api_key[:8]}...")
                except Exception as e:
                    logger.warning(f"⚠️ AuthManager error: {e}, "
                                   f"falling back to basic auth")
                    self._security_available = False

            if not self._security_available:
                # Fallback to basic API key handling
                if api_key in getattr(self, 'api_keys', {}):
                    user_role = self.api_keys[api_key]

                    # Get permissions for this role from roles file if available
                    role_permissions = ["read"]  # default permissions
                    if (hasattr(self, 'roles_config') and
                            self.roles_config and
                            user_role in self.roles_config):
                        role_permissions = self.roles_config[user_role].get(
                            "permissions", ["read"]
                        )

                    # Set user info in request.state
                    request.state.user = {
                        "id": api_key,
                        "role": user_role,
                        "roles": [user_role],
                        "permissions": role_permissions
                    }

                    logger.debug(f"✅ Authenticated user with basic auth: "
                                 f"{request.state.user}")
                else:
                    # API key not found
                    request.state.user = {
                        "id": None,
                        "role": "guest",
                        "roles": ["guest"],
                        "permissions": ["read"]
                    }
                    logger.debug(f"❌ API key not found: {api_key[:8]}...")
        else:
            # No API key provided - guest access
            request.state.user = {
                "id": None,
                "role": "guest",
                "roles": ["guest"],
                "permissions": ["read"]
            }
            logger.debug("ℹ️ No API key provided, using guest access")

        return await call_next(request)
