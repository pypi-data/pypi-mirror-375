import os
from pathlib import Path
from typing import Optional
import uuid
import socket

from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
import os
from .utils.logging import setup_logger

logger = setup_logger(__name__)


def ensure_config() -> None:
    """Ensure the provider configuration directory and defaults exist."""
    base_dir = Path.home() / ".golem" / "provider"
    env_file = base_dir / ".env"
    subdirs = ["keys", "ssh", "vms", "proxy"]
    created = False

    for sub in subdirs:
        path = base_dir / sub
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created = True

    if not env_file.exists():
        env_file.write_text("GOLEM_PROVIDER_ENVIRONMENT=production\n")
        created = True

    from .security.ethereum import EthereumIdentity

    identity = EthereumIdentity(str(base_dir / "keys"))
    if not identity.key_file.exists():
        identity.get_or_create_identity()
        created = True

    if created:
        print("Using default settings – run with --help to customize")


if not os.environ.get("GOLEM_PROVIDER_SKIP_BOOTSTRAP") and not os.environ.get("PYTEST_CURRENT_TEST"):
    ensure_config()


class Settings(BaseSettings):
    """Provider configuration settings."""

    # API Settings
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 7466
    SKIP_PORT_VERIFICATION: bool = False
    ENVIRONMENT: str = "production"
    # Logical network selector for annotation and client defaults
    NETWORK: str = "mainnet"  # one of: "testnet", "mainnet"

    @property
    def DEV_MODE(self) -> bool:
        return self.ENVIRONMENT == "development"

    @field_validator("SKIP_PORT_VERIFICATION", mode='before')
    def set_skip_verification(cls, v: bool, values: dict) -> bool:
        """Set skip verification based on debug mode."""
        return v or values.data.get("DEBUG", False)

    # Provider Settings
    PROVIDER_NAME: str = "golem-provider"
    PROVIDER_COUNTRY: str = "SE"
    ETHEREUM_KEY_DIR: str = ""
    ETHEREUM_PRIVATE_KEY: Optional[str] = None
    PROVIDER_ID: str = ""  # Will be set from Ethereum identity
 
    @field_validator("ETHEREUM_KEY_DIR", mode='before')
    def resolve_key_dir(cls, v: str) -> str:
        """Resolve Ethereum key directory path."""
        if not v:
            return str(Path.home() / ".golem" / "provider" / "keys")
        path = Path(v)
        if not path.is_absolute():
            path = Path.home() / path
        return str(path)

    @field_validator("ETHEREUM_PRIVATE_KEY", mode='before')
    def get_private_key(cls, v: Optional[str], values: dict) -> str:
        """Get private key from key file if not provided."""
        from provider.security.ethereum import EthereumIdentity

        if v:
            return v
        
        key_dir = values.data.get("ETHEREUM_KEY_DIR")
        identity = EthereumIdentity(key_dir)
        _, private_key = identity.get_or_create_identity()
        return private_key

    @field_validator("PROVIDER_ID", mode='before')
    def get_provider_id(cls, v: str, values: dict) -> str:
        """Get provider ID from private key."""
        from eth_account import Account

        private_key = values.data.get("ETHEREUM_PRIVATE_KEY")
        if not private_key:
            raise ValueError("ETHEREUM_PRIVATE_KEY is not set")

        acct = Account.from_key(private_key)
        provider_id_from_key = acct.address

        # If ID was provided via env, warn if it doesn't match
        if v and v != provider_id_from_key:
            logger.warning(
                f"Provider ID from env ('{v}') does not match ID from key file ('{provider_id_from_key}'). "
                "Using ID from key file."
            )
        
        return provider_id_from_key
 
    @field_validator("PROVIDER_NAME", mode='before')
    def set_provider_name(cls, v: str, values: dict) -> str:
        """Prefix provider name with DEVMODE if in development."""
        if values.data.get("ENVIRONMENT") == "development":
            return f"DEVMODE-{v}"
        return v
 
    # Discovery Service Settings
    DISCOVERY_URL: str = "http://195.201.39.101:9001"
    ADVERTISER_TYPE: str = "golem_base"  # or "discovery_server"
    # Deprecated: use platform-specific intervals below
    ADVERTISEMENT_INTERVAL: int = 240  # seconds
    DISCOVERY_ADVERTISEMENT_INTERVAL: int = 240  # seconds
    GOLEM_BASE_ADVERTISEMENT_INTERVAL: int = 3600  # seconds (on-chain cost, keep higher)

    # Golem Base Settings
    GOLEM_BASE_RPC_URL: str = "https://ethwarsaw.holesky.golemdb.io/rpc"
    GOLEM_BASE_WS_URL: str = "wss://ethwarsaw.holesky.golemdb.io/rpc/ws"

    # Polygon / Payments
    POLYGON_RPC_URL: str = Field(
        default="https://l2.holesky.golemdb.io/rpc",
        description="EVM RPC URL for streaming payments (L2 by default)"
    )
    STREAM_PAYMENT_ADDRESS: str = Field(
        default="0x0000000000000000000000000000000000000000",
        description="Deployed StreamPayment contract address"
    )
    GLM_TOKEN_ADDRESS: str = Field(
        default="0x0000000000000000000000000000000000000000",
        description="Token address (0x0 means native ETH)"
    )
    STREAM_MIN_REMAINING_SECONDS: int = Field(
        default=3600,
        description="Minimum remaining seconds required to keep a VM running"
    )
    STREAM_MONITOR_ENABLED: bool = Field(
        default=False,
        description="Enable background monitor to stop VMs when runway < threshold"
    )
    STREAM_WITHDRAW_ENABLED: bool = Field(
        default=False,
        description="Enable background withdrawals for active streams"
    )
    STREAM_MONITOR_INTERVAL_SECONDS: int = Field(
        default=60,
        description="How frequently to check stream runway"
    )
    STREAM_WITHDRAW_INTERVAL_SECONDS: int = Field(
        default=1800,
        description="How frequently to attempt withdrawals"
    )
    STREAM_MIN_WITHDRAW_WEI: int = Field(
        default=0,
        description="Min withdrawable amount (wei) before triggering withdraw"
    )

    # Faucet settings (L3 for Golem Base adverts)
    FAUCET_URL: str = "https://ethwarsaw.holesky.golemdb.io/faucet"
    CAPTCHA_URL: str = "https://cap.gobas.me"
    CAPTCHA_API_KEY: str = "05381a2cef5e"

    # L2 payments faucet (native ETH)
    L2_FAUCET_URL: str = Field(
        default="https://l2.holesky.golemdb.io/faucet",
        description="L2 faucet base URL (no trailing /api)"
    )
    L2_CAPTCHA_URL: str = Field(
        default="https://cap.gobas.me",
        description="CAPTCHA base URL"
    )
    L2_CAPTCHA_API_KEY: str = Field(
        default="05381a2cef5e",
        description="CAPTCHA API key path segment"
    )

    @field_validator("POLYGON_RPC_URL", mode='before')
    @classmethod
    def prefer_custom_env(cls, v: str) -> str:
        # Accept alternative aliases for payments RPC
        for key in ("GOLEM_PROVIDER_L2_RPC_URL", "GOLEM_PROVIDER_KAOLIN_RPC_URL"):
            if os.environ.get(key):
                return os.environ[key]
        return v

    # VM Settings
    MAX_VMS: int = 10
    DEFAULT_VM_IMAGE: str = "ubuntu:24.04"
    VM_DATA_DIR: str = ""
    SSH_KEY_DIR: str = ""
    CLOUD_INIT_DIR: str = ""
    CLOUD_INIT_FALLBACK_DIR: str = ""  # Will be set to a temp directory if needed

    @field_validator("CLOUD_INIT_DIR", mode='before')
    def resolve_cloud_init_dir(cls, v: str) -> str:
        """Resolve and create cloud-init directory path."""
        import platform
        import tempfile
        from .utils.setup import setup_cloud_init_dir, check_setup_needed, mark_setup_complete
        
        def verify_dir_permissions(path: Path) -> bool:
            """Verify directory has correct permissions and is accessible."""
            try:
                # Create test file
                test_file = path / "permission_test"
                test_file.write_text("test")
                test_file.unlink()
                return True
            except Exception:
                return False

        if v:
            path = Path(v)
            if not path.is_absolute():
                path = Path.home() / path
        else:
            system = platform.system().lower()
            # Try OS-specific paths first
            if system == "linux" and Path("/snap/bin/multipass").exists():
                # Linux with snap
                path = Path("/var/snap/multipass/common/cloud-init")
                
                # Check if we need to set up permissions
                if check_setup_needed():
                    logger.info("First run detected, setting up cloud-init directory...")
                    success, error = setup_cloud_init_dir(path)
                    if success:
                        logger.info("✓ Cloud-init directory setup complete")
                        mark_setup_complete()
                    else:
                        logger.error(f"Failed to set up cloud-init directory: {error}")
                        logger.error("\nTo fix this manually, run these commands:")
                        logger.error("  sudo mkdir -p /var/snap/multipass/common/cloud-init")
                        logger.error("  sudo chown -R $USER:$USER /var/snap/multipass/common/cloud-init")
                        logger.error("  sudo chmod -R 755 /var/snap/multipass/common/cloud-init\n")
                        # Fall back to user's home directory
                        path = Path.home() / ".local" / "share" / "golem" / "provider" / "cloud-init"
                
            elif system == "linux":
                # Linux without snap
                path = Path.home() / ".local" / "share" / "golem" / "provider" / "cloud-init"
            elif system == "darwin":
                # macOS
                path = Path.home() / "Library" / "Application Support" / "golem" / "provider" / "cloud-init"
            elif system == "windows":
                # Windows
                path = Path(os.path.expandvars("%LOCALAPPDATA%")) / "golem" / "provider" / "cloud-init"
            else:
                path = Path.home() / ".golem" / "provider" / "cloud-init"

        try:
            # Try to create and verify the directory
            path.mkdir(parents=True, exist_ok=True)
            if platform.system().lower() != "windows":
                path.chmod(0o755)  # Readable and executable by owner and others, writable by owner

            if verify_dir_permissions(path):
                logger.debug(f"Created cloud-init directory at {path}")
                return str(path)
            
            # If verification fails, fall back to temp directory
            fallback_path = Path(tempfile.gettempdir()) / "golem" / "cloud-init"
            fallback_path.mkdir(parents=True, exist_ok=True)
            if platform.system().lower() != "windows":
                fallback_path.chmod(0o755)
            
            if verify_dir_permissions(fallback_path):
                logger.warning(f"Using fallback cloud-init directory at {fallback_path}")
                return str(fallback_path)
            
            raise ValueError("Could not create a writable cloud-init directory")
            
        except Exception as e:
            logger.error(f"Failed to create cloud-init directory at {path}: {e}")
            raise ValueError(f"Failed to create cloud-init directory: {e}")

    @field_validator("VM_DATA_DIR", mode='before')
    def resolve_vm_data_dir(cls, v: str) -> str:
        """Resolve and create VM data directory path."""
        if not v:
            path = Path.home() / ".golem" / "provider" / "vms"
        else:
            path = Path(v)
            if not path.is_absolute():
                path = Path.home() / path
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created VM data directory at {path}")
        except Exception as e:
            logger.error(f"Failed to create VM data directory at {path}: {e}")
            raise ValueError(f"Failed to create VM data directory: {e}")
            
        return str(path)

    @field_validator("SSH_KEY_DIR", mode='before')
    def resolve_ssh_key_dir(cls, v: str) -> str:
        """Resolve and create SSH key directory path with secure permissions."""
        if not v:
            path = Path.home() / ".golem" / "provider" / "ssh"
        else:
            path = Path(v)
            if not path.is_absolute():
                path = Path.home() / path
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            path.chmod(0o700)  # Secure permissions for SSH keys
            logger.debug(f"Created SSH key directory at {path} with secure permissions")
        except Exception as e:
            logger.error(f"Failed to create SSH key directory at {path}: {e}")
            raise ValueError(f"Failed to create SSH key directory: {e}")
            
        return str(path)

    # Resource Settings
    MIN_MEMORY_GB: int = 1
    MIN_STORAGE_GB: int = 10
    MIN_CPU_CORES: int = 1

    # Resource Thresholds (%)
    CPU_THRESHOLD: int = 90
    MEMORY_THRESHOLD: int = 85
    STORAGE_THRESHOLD: int = 90

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Retry/Timeout Settings (for long-running external calls)
    RETRY_ATTEMPTS: int = 5
    RETRY_DELAY_SECONDS: float = 2.0
    RETRY_BACKOFF: float = 2.0
    CREATE_VM_MAX_RETRIES: int = 15
    CREATE_VM_RETRY_DELAY_SECONDS: float = 5.0
    LAUNCH_TIMEOUT_SECONDS: int = 300

    # Multipass Settings
    MULTIPASS_BINARY_PATH: str = Field(
        default="",
        description="Path to multipass binary"
    )

    @field_validator("MULTIPASS_BINARY_PATH")
    def detect_multipass_path(cls, v: str) -> str:
        """Detect and validate Multipass binary path."""
        import platform
        import subprocess
        
        def validate_path(path: str) -> bool:
            """Validate that a path exists and is executable."""
            return os.path.isfile(path) and os.access(path, os.X_OK)

        # If path provided via environment variable, ONLY validate that path
        if v:
            logger.info(f"Checking multipass binary at: {v}")
            if not validate_path(v):
                msg = f"Invalid multipass binary path: {v} (not found or not executable)"
                logger.error(msg)
                raise ValueError(msg)
            logger.info(f"✓ Found valid multipass binary at: {v}")
            return v

        logger.info("No multipass path provided, attempting auto-detection...")
        system = platform.system().lower()
        logger.info(f"Detected OS: {system}")
        binary_name = "multipass.exe" if system == "windows" else "multipass"
        
        # Try to find multipass based on OS
        if system == "linux":
            logger.info("Checking for snap installation...")
            # First try to find snap and check if multipass is installed
            try:
                # Check if snap exists
                snap_result = subprocess.run(
                    ["which", "snap"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if snap_result.returncode == 0:
                    logger.info("✓ Found snap, checking for multipass installation...")
                    # Check if multipass is installed via snap
                    try:
                        snap_list = subprocess.run(
                            ["snap", "list", "multipass"],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        if snap_list.returncode == 0:
                            snap_path = "/snap/bin/multipass"
                            if validate_path(snap_path):
                                logger.info(f"✓ Found multipass via snap at {snap_path}")
                                return snap_path
                    except subprocess.CalledProcessError:
                        logger.info("✗ Multipass not installed via snap")
                        pass
            except subprocess.CalledProcessError:
                logger.info("✗ Snap not found")
                pass
                
            # Common Linux paths if snap installation not found
            search_paths = [
                "/usr/local/bin",
                "/usr/bin",
                "/snap/bin"
            ]
            logger.info(f"Checking common Linux paths: {', '.join(search_paths)}")
                
        elif system == "darwin":  # macOS
            search_paths = [
                "/opt/homebrew/bin",    # M1 Mac
                "/usr/local/bin",       # Intel Mac
                "/opt/local/bin"        # MacPorts
            ]
            logger.info(f"Checking macOS paths: {', '.join(search_paths)}")
                
        elif system == "windows":
            search_paths = [
                os.path.join(os.path.expandvars(r"%ProgramFiles%"), "Multipass", "bin"),
                os.path.join(os.path.expandvars(r"%ProgramFiles(x86)%"), "Multipass", "bin"),
                os.path.join(os.path.expandvars(r"%LocalAppData%"), "Multipass", "bin")
            ]
            logger.info(f"Checking Windows paths: {', '.join(search_paths)}")
                
        else:
            search_paths = ["/usr/local/bin", "/usr/bin"]
            logger.info(f"Checking default paths: {', '.join(search_paths)}")

        # Search for multipass binary in OS-specific paths
        for directory in search_paths:
            path = os.path.join(directory, binary_name)
            if validate_path(path):
                logger.info(f"✓ Found valid multipass binary at: {path}")
                return path

        # OS-specific installation instructions
        if system == "linux":
            raise ValueError(
                "Multipass binary not found. Please install using:\n"
                "sudo snap install multipass\n"
                "Or set GOLEM_PROVIDER_MULTIPASS_BINARY_PATH to your Multipass binary path."
            )
        elif system == "darwin":
            raise ValueError(
                "Multipass binary not found. Please install using:\n"
                "brew install multipass\n"
                "Or set GOLEM_PROVIDER_MULTIPASS_BINARY_PATH to your Multipass binary path."
            )
        elif system == "windows":
            raise ValueError(
                "Multipass binary not found. Please install from:\n"
                "Microsoft Store or https://multipass.run/download/windows\n"
                "Or set GOLEM_PROVIDER_MULTIPASS_BINARY_PATH to your Multipass binary path."
            )
        else:
            raise ValueError(
                "Multipass binary not found. Please install Multipass or set "
                "GOLEM_PROVIDER_MULTIPASS_BINARY_PATH to your Multipass binary path."
            )

    # Proxy Settings
    PORT_RANGE_START: int = 50800
    PORT_RANGE_END: int = 50900
    PROXY_STATE_DIR: str = ""
    PUBLIC_IP: Optional[str] = None

    @field_validator("PROXY_STATE_DIR", mode='before')
    def resolve_proxy_state_dir(cls, v: str) -> str:
        """Resolve and create proxy state directory path."""
        if not v:
            path = Path.home() / ".golem" / "provider" / "proxy"
        else:
            path = Path(v)
            if not path.is_absolute():
                path = Path.home() / path
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created proxy state directory at {path}")
        except Exception as e:
            logger.error(f"Failed to create proxy state directory at {path}: {e}")
            raise ValueError(f"Failed to create proxy state directory: {e}")
            
        return str(path)

    @field_validator("PUBLIC_IP", mode='before')
    def get_public_ip(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Get public IP if set to 'auto'."""
        if values.data.get("ENVIRONMENT") == "development":
            try:
                hostname = socket.gethostname()
                ips = socket.gethostbyname_ex(hostname)[2]
                local_ips = [ip for ip in ips if not ip.startswith("127.")]
                if local_ips:
                    ip = local_ips[0]
                    logger.info(f"Found local IP for development: {ip}")
                    return ip
            except socket.gaierror:
                pass

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                IP = s.getsockname()[0]
                if IP:
                    logger.info(f"Found local IP for development: {IP}")
                    return IP
            except Exception:
                pass
            finally:
                s.close()

            raise ValueError("Could not determine local IP address in development mode. "
                             "Please ensure you have a valid network connection.")
        if v == "auto":
            try:
                import requests
                response = requests.get("https://api.ipify.org")
                ip = response.text.strip()
                logger.info(f"Found public IP: {ip}")
                return ip
            except Exception:
                return None
        
        if v:
            logger.info(f"Using manually provided IP: {v}")
        return v

    # Pricing Settings (configured in USD; auto-converted to GLM)
    # Per-month prices per unit
    PRICE_USD_PER_CORE_MONTH: float = Field(default=5.0, ge=0)
    PRICE_USD_PER_GB_RAM_MONTH: float = Field(default=2.0, ge=0)
    PRICE_USD_PER_GB_STORAGE_MONTH: float = Field(default=0.1, ge=0)

    # Auto-updated GLM-denominated prices (derived from USD via CoinGecko)
    PRICE_GLM_PER_CORE_MONTH: float = Field(default=0.0, ge=0)
    PRICE_GLM_PER_GB_RAM_MONTH: float = Field(default=0.0, ge=0)
    PRICE_GLM_PER_GB_STORAGE_MONTH: float = Field(default=0.0, ge=0)

    # CoinGecko integration
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_IDS: str = "golem,golem-network-tokens"  # try both, first wins
    PRICING_UPDATE_ENABLED: bool = True
    PRICING_UPDATE_MIN_DELTA_PERCENT: float = Field(default=1.0, ge=0.0)
    PRICING_UPDATE_INTERVAL_DISCOVERY: int = 900    # 15 minutes
    PRICING_UPDATE_INTERVAL_GOLEM_BASE: int = 14400 # 4 hours

    class Config:
        env_prefix = "GOLEM_PROVIDER_"
        case_sensitive = True


# Global settings instance
settings = Settings()
