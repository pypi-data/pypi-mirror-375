"""Windows specific parsing logic.

Refactored for clarity: vendor/edition detection, NT mapping, and build
mapping are handled by focused helpers. Behavior is preserved while
avoiding ambiguous NT mappings when server signals are present.
"""

import re
from typing import Any, Optional

from os_normalizer.constants import (
    WINDOWS_BUILD_MAP,
    WINDOWS_NT_CLIENT_MAP,
    WINDOWS_NT_SERVER_MAP,
)
from os_normalizer.helpers import update_confidence
from os_normalizer.models import OSData

# Regex patterns used only by the Windows parser
WIN_EDITION_RE = re.compile(
    r"\b(professional|enterprise|home|education|ltsc|datacenter)\b",
    re.IGNORECASE,
)
WIN_SP_RE = re.compile(r"\bSP\s?([0-9]+)\b", re.IGNORECASE)
WIN_BUILD_RE = re.compile(r"\bbuild\s?(\d{4,6})\b", re.IGNORECASE)
WIN_NT_RE = re.compile(r"\bnt\s?(\d+)\.(\d+)\b", re.IGNORECASE)
WIN_FULL_NT_BUILD_RE = re.compile(r"\b(10)\.(0)\.(\d+)(?:\.(\d+))?\b")
WIN_CHANNEL_RE = re.compile(r"\b(20H2|21H2|22H2|23H2|24H2|19H2|18H2|17H2|2004|1909|1809|1709|1511|1507)\b", re.IGNORECASE)


def parse_windows(text: str, data: dict[str, Any], p: OSData) -> OSData:
    """Populate an OSData instance with Windows-specific details."""
    p.kernel_name = "nt"

    # 1) Product and edition from free text
    p.product = p.product or _detect_product_from_text(text.lower())
    p.edition = p.edition or _detect_edition(text)

    # 2) Service Pack
    _parse_service_pack(text, p)

    # 3) NT version mapping (client vs server)
    server_like = _is_server_like(text.lower())
    _apply_nt_mapping(text, p, server_like)

    # 4) Full kernel version (e.g., 10.0.22621.2715) + channel token if present
    _apply_full_kernel_and_channel(text, p)

    # 5) Build number + marketing channel (fallback when only 'build 22631' is present)
    _apply_build_mapping(text, p)

    # 6) Precision and version_major if applicable
    _finalize_precision_and_version(p)

    # 7) Vendor + confidence
    p.vendor = "Microsoft"
    update_confidence(p, p.precision)
    return p


def _detect_product_from_text(t: str) -> str:
    if "windows 11" in t or "win11" in t:
        return "Windows 11"
    if "windows 10" in t or "win10" in t:
        return "Windows 10"
    if "windows 8.1" in t or "win81" in t:
        return "Windows 8.1"
    if "windows 8" in t or "win8" in t:
        return "Windows 8"
    if "windows 7" in t or "win7" in t:
        return "Windows 7"
    if "windows me" in t or "windows millenium" in t:
        return "Windows ME"
    if "windows 98" in t or "win98" in t:
        return "Windows 98"

    # Server explicit names
    if "windows server 2022" in t or "win2k22" in t or "win2022" in t:
        return "Windows Server 2022"
    if "windows server 2019" in t or "win2k19" in t or "win2019" in t:
        return "Windows Server 2019"
    if "windows server 2016" in t or "win2k16" in t or "win2016" in t:
        return "Windows Server 2016"
    if "windows server 2012" in t or "win2k12" in t or "win2012" in t:
        return "Windows Server 2012"
    if "windows server 2008" in t or "win2k8" in t or "win2008" in t:
        return "Windows Server 2008"
    if "windows server 2003" in t or "win2k3" in t or "win2003" in t:
        return "Windows Server 2003"
    if "windows server 2000" in t or "win2k" in t or "win2000" in t:
        return "Windows Server 2000"

    if "windows" in t:
        return "Windows"
    return "Unknown"


def _detect_edition(text: str) -> str | None:
    m = WIN_EDITION_RE.search(text)
    return m.group(1).title() if m else None


def _parse_service_pack(text: str, p: OSData) -> None:
    sp = WIN_SP_RE.search(text)
    if sp:
        p.version_patch = int(sp.group(1))
        p.evidence["service_pack"] = sp.group(0)


def _is_server_like(t: str) -> bool:
    return any(
        kw in t
        for kw in (
            "server",
            "datacenter",
            "standard",
            "essentials",
            "foundation",
            "core",  # server core often appears
            "hyper-v",
        )
    )


def _apply_nt_mapping(text: str, p: OSData, server_like: bool) -> None:
    nt = WIN_NT_RE.search(text)
    if not nt:
        return
    major, minor = int(nt.group(1)), int(nt.group(2))
    p.evidence["nt_version"] = f"{major}.{minor}"

    # If product already explicitly set (e.g., "Windows Server 2019"), keep it
    if p.product and p.product not in ("Windows", "Windows 10/11"):
        return

    product = WINDOWS_NT_SERVER_MAP.get((major, minor)) if server_like else WINDOWS_NT_CLIENT_MAP.get((major, minor))
    if product:
        p.product = product


def _apply_build_mapping(text: str, p: OSData) -> None:
    m = WIN_BUILD_RE.search(text)
    if not m:
        return
    build_num = int(m.group(1))
    p.version_build = str(build_num)

    # Kernel version for recent Windows 10/11
    if (p.product == "Windows 10/11") or ("10.0" in text):
        p.kernel_version = f"{10}.{0}.{build_num}"
    else:
        p.kernel_version = None

    # Only apply client build mapping if current product isn't an explicit Server
    is_server_product = isinstance(p.product, str) and "server" in p.product.lower()
    if not is_server_product:
        for lo, hi, product_name, marketing in WINDOWS_BUILD_MAP:
            if lo <= build_num <= hi:
                p.product = product_name
                p.channel = marketing
                break


def _apply_full_kernel_and_channel(text: str, p: OSData) -> None:
    # Full NT kernel version, e.g., 10.0.22621.2715
    m = WIN_FULL_NT_BUILD_RE.search(text)
    if m:
        build = m.group(3)
        suffix = m.group(4)
        p.version_build = p.version_build or build
        p.kernel_version = f"10.0.{build}{('.' + suffix) if suffix else ''}"
        # Record evidence for NT 10.0 if not set via NT mapping
        p.evidence.setdefault("nt_version", "10.0")

    # Marketing channel token in free text, e.g., 22H2 (case-insensitive)
    ch = WIN_CHANNEL_RE.search(text)
    if ch and not p.channel:
        p.channel = ch.group(1).upper()


def _finalize_precision_and_version(p: OSData) -> None:
    if p.version_build:
        p.precision = "build"
        return
    if p.version_patch is not None:
        p.precision = "patch"
        return
    if p.product and any(x in p.product for x in ("7", "8", "10", "11")):
        digits = re.findall(r"\d+", p.product)
        if digits:
            p.version_major = int(digits[0])
        p.precision = "major"
        return
    if p.product:
        p.precision = "product"
    else:
        p.precision = "family"
