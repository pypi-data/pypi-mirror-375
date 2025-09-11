from .logger import logger, format_log_message as flm
from .context import RequestContext
from pathlib import Path
from typing import ClassVar
import aiodns
import asyncio
import os
import re
import sys

# Regex to parse a line in the hosts file.
# It captures the IP address and all hostnames on the line.
# It ignores comments starting with '#'.
HOSTS_LINE_REGEX = re.compile(r"^\s*([^\s#]+)\s+([^#]+)")


class Resolver:
    """
    A DNS resolver that uses aiodns and a persistent hosts file cache.
    This class is implemented as a singleton to ensure only one instance
    is used throughout the application.
    """

    # Class variable to hold the singleton instance
    _instance: ClassVar["Resolver | None"] = None

    def __init__(self) -> None:
        """
        Initializes the resolver, loads the hosts file, and sets the
        singleton instance. The aiodns.DNSResolver is created lazily.
        """
        if not Resolver._instance:
            self.resolver: aiodns.DNSResolver | None = None
            self.hosts_cache: dict[str, str] = {}
            self.verbose: int = 0  # Verbosity level, configured separately
            Resolver._instance = self

    def initialize(self, verbose: int) -> None:
        """
        Initializes the resolver with a verbosity level and loads the hosts file.

        Args:
            verbose (int): The verbosity level for logging.

        Returns:
            None
        """
        self.verbose = verbose
        self._load_hosts_file()

    @staticmethod
    def get_instance() -> "Resolver":
        """
        Static access method to get the singleton instance of the resolver.

        Returns:
            Resolver: The singleton instance of the resolver.
        """
        if Resolver._instance is None:
            Resolver()
        return Resolver._instance  # type: ignore

    def _get_hosts_path(self) -> Path:
        """
        Determines the correct path to the hosts file based on the operating system.

        This method returns the path to the hosts file, which is used by the resolver to
        fetch DNS mappings from the local hosts file.

        Returns:
            Path: The path to the hosts file.
        """
        if sys.platform == "win32":
            # Use the SYSTEMROOT environment variable on Windows
            return (
                Path(os.environ["SYSTEMROOT"])
                / "System32"
                / "drivers"
                / "etc"
                / "hosts"
            )
        else:
            # For Linux, macOS, and other UNIX-like systems
            return Path("/etc/hosts")

    def _load_hosts_file(self) -> None:
        """
        Parses the system's hosts file and populates the cache.

        This method reads the hosts file, which maps hostnames to IP addresses, and
        populates the internal cache with this information. The cache is used to quickly
        resolve hostnames without querying DNS.

        Returns:
            None
        """
        hosts_path = self._get_hosts_path()
        ident = {"id": "000000", "client": "0.0.0.0"}

        if not hosts_path.exists():
            logger.warning(
                flm(
                    f"Hosts file not found at {hosts_path}, skipping.",
                    ident,
                    self.verbose,
                )
            )
            return

        try:
            with open(hosts_path, "r", encoding="utf-8") as f:
                for line in f:
                    match = HOSTS_LINE_REGEX.match(line)
                    if not match:
                        continue

                    ip_address = match.group(1)
                    hostnames_str = match.group(2)
                    hostnames = hostnames_str.strip().split()

                    for hostname in hostnames:
                        self.hosts_cache[hostname.lower()] = ip_address

            logger.info(
                flm(
                    f"Loaded {len(self.hosts_cache)} entries from {hosts_path}",
                    ident,
                    self.verbose,
                )
            )
        except Exception as e:
            logger.error(
                flm(
                    f"Failed to load or parse hosts file at {hosts_path}: {e}",
                    ident,
                    self.verbose,
                )
            )

    async def resolve_with_ttl(self, hostname: str) -> tuple[list[str], int]:
        """
        Resolves a hostname to a list of IP addresses and the minimum TTL.

        1. Checks the local hosts file cache first.
        2. If not found, queries DNS for A and AAAA records using aiodns and extracts TTL.

        Args:
            hostname (str): The hostname to resolve.

        Returns:
            tuple[list[str], int]: A list of IP addresses and the minimum TTL value.

        Raises:
            OSError: If no IP addresses could be resolved.
        """
        # Create a specific ident for this resolution request
        ident = {"id": "resolver", "client": hostname}

        # Lazily initialize the resolver on first use to attach to the correct event loop.
        if self.resolver is None:
            loop = asyncio.get_running_loop()
            self.resolver = aiodns.DNSResolver(loop=loop)

        hostname_lower = hostname.lower()
        # 1. Check hosts file cache
        if ip := self.hosts_cache.get(hostname_lower):
            logger.debug(
                flm(
                    f"Resolved to {ip} from hosts file cache.",
                    ident,
                    self.verbose,
                )
            )
            # Hosts file entries don't have TTL, use a default high value
            return [ip], 3600

        # 2. Query DNS using aiodns for IPv4 and IPv6 addresses concurrently
        results = await asyncio.gather(
            self.resolver.query(hostname, "A"),
            self.resolver.query(hostname, "AAAA"),
            return_exceptions=True,
        )

        resolved_ips: set[str] = set()
        min_ttl = float("inf")

        for res in results:
            if isinstance(res, list):
                for record in res:
                    if isinstance(record.host, bytes):
                        resolved_ips.add(record.host.decode())
                    else:
                        resolved_ips.add(record.host)
                    # Extract TTL from record
                    if hasattr(record, "ttl") and record.ttl < min_ttl:
                        min_ttl = record.ttl
            elif isinstance(res, aiodns.error.DNSError):
                # Ignore common "not found" errors. Log other DNS errors for debugging.
                if res.args[0] not in (
                    aiodns.error.ARES_ENODATA,
                    aiodns.error.ARES_ENOTFOUND,
                ):
                    logger.debug(
                        flm(f"aiodns query failed: {res}", ident, self.verbose)
                    )
            elif isinstance(res, Exception):
                logger.warning(
                    flm(
                        f"Unexpected error during DNS resolution: {res}",
                        ident,
                        self.verbose,
                    )
                )

        if not resolved_ips:
            raise OSError(f"Failed to resolve host: {hostname}")

        # If no TTL was found (shouldn't happen but just in case), use default
        if min_ttl == float("inf"):
            min_ttl = 300

        return list(resolved_ips), int(min_ttl)

    async def resolve(self, hostname: str) -> list[str]:
        """
        Resolves a hostname to a list of IP addresses.

        1. Checks the local hosts file cache first.
        2. If not found, queries DNS for A and AAAA records using aiodns.

        Args:
            hostname (str): The hostname to resolve.

        Returns:
            list[str]: A list of IP addresses associated with the hostname.

        Raises:
            OSError: If no IP addresses could be resolved.
        """
        ips, _ = await self.resolve_with_ttl(hostname)
        return ips


# Initialize the singleton instance so it's ready for other modules to import
resolver = Resolver.get_instance()
