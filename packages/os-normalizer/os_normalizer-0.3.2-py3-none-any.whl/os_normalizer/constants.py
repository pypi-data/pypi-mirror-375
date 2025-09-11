"""Constants and static lookup tables for the OS fingerprinting package."""

# Architecture synonyms
ARCH_SYNONYMS = {
    "x64": "x86_64",
    "x86_64": "x86_64",
    "amd64": "x86_64",
    "x86": "x86",
    "i386": "x86",
    "i686": "x86",
    "aarch64": "arm64",
    "arm64": "arm64",
    "armv8": "arm64",
    "armv7": "arm",
    "armv7l": "arm",
    "ppc64le": "ppc64le",
}

# Windows build map (build number range -> product name, marketing channel)
WINDOWS_BUILD_MAP = [
    # Windows 10
    (10240, 10240, "Windows 10", "1507"),
    (10586, 10586, "Windows 10", "1511"),
    (14393, 14393, "Windows 10", "1607"),
    (15063, 15063, "Windows 10", "1703"),
    (16299, 16299, "Windows 10", "1709"),
    (17134, 17134, "Windows 10", "1803"),
    (17763, 17763, "Windows 10", "1809"),
    (18362, 18363, "Windows 10", "1903/1909"),
    (19041, 19045, "Windows 10", "2004/20H2/21H1/21H2/22H2"),
    # Windows 11
    (22000, 22000, "Windows 11", "21H2"),
    (22621, 22630, "Windows 11", "22H2"),
    (22631, 25999, "Windows 11", "23H2"),
    (26100, 26199, "Windows 11", "24H2"),
]

# Windows NT version tuple -> client product (ambiguous NT 6.x split out)
WINDOWS_NT_CLIENT_MAP = {
    (4, 0): "Windows NT 4.0",
    (5, 0): "Windows 2000",
    (5, 1): "Windows XP",
    (5, 2): "Windows XP x64/Server 2003",  # NT 5.2 often maps to XP x64 on client
    (6, 0): "Windows Vista",
    (6, 1): "Windows 7",
    (6, 2): "Windows 8",
    (6, 3): "Windows 8.1",
    (10, 0): "Windows 10/11",
}

# Windows NT version tuple -> server product
WINDOWS_NT_SERVER_MAP = {
    (4, 0): "Windows NT 4.0 Server",
    (5, 0): "Windows 2000 Server",
    (5, 1): "Windows XP/Server 2003",  # rarely used for server detection
    (5, 2): "Windows Server 2003",
    (6, 0): "Windows Server 2008",
    (6, 1): "Windows Server 2008 R2",
    (6, 2): "Windows Server 2012",
    (6, 3): "Windows Server 2012 R2",
    # NT 10.0: Server 2016/2019/2022 detected via explicit names, not NT mapping
}

# Human readable aliases (macOS codenames)
MACOS_ALIASES = {
    "sonoma": "macOS 14",
    "sequoia": "macOS 15",
    "ventura": "macOS 13",
    "monterey": "macOS 12",
    "big sur": "macOS 11",
    "bigsur": "macOS 11",
    "catalina": "macOS 10.15",
}

# macOS Darwin major version -> (product name, product version, codename)
MACOS_DARWIN_MAP = {
    19: ("macOS", "10.15", "Catalina"),
    20: ("macOS", "11", "Big Sur"),
    21: ("macOS", "12", "Monterey"),
    22: ("macOS", "13", "Ventura"),
    23: ("macOS", "14", "Sonoma"),
    24: ("macOS", "15", "Sequoia"),
}

# Cisco train names (used for codename detection)
CISCO_TRAIN_NAMES = {"Everest", "Fuji", "Gibraltar", "Amsterdam", "Denali"}

