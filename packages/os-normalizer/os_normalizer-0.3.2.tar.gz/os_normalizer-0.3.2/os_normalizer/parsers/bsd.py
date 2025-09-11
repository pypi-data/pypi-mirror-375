"""BSD specific parsing logic (refactored, variant + channel handling)."""

import re
from typing import Any

from os_normalizer.helpers import (
    parse_semver_like,
    precision_from_parts,
    update_confidence,
)
from os_normalizer.models import OSData

FREEBSD_RE = re.compile(r"\bfreebsd\b", re.IGNORECASE)
OPENBSD_RE = re.compile(r"\bopenbsd\b", re.IGNORECASE)
NETBSD_RE = re.compile(r"\bnetbsd\b", re.IGNORECASE)

VARIANT_VERSION_RE = re.compile(
    r"\b(?:freebsd|openbsd|netbsd)\b\s+(\d+)(?:\.(\d+))?(?:\.(\d+))?",
    re.IGNORECASE,
)
BSD_CHANNEL_RE = re.compile(
    r"(?:[-_\s])(RELEASE|STABLE|CURRENT|RC\d*|BETA\d*|RC|BETA)\b",
    re.IGNORECASE,
)


def parse_bsd(text: str, data: dict[str, Any], p: OSData) -> OSData:
    """Populate an OSData instance with BSD-specific details.

    Detects FreeBSD, OpenBSD, or NetBSD and extracts version numbers.
    """
    tl = text.lower()

    # Explicitly set product/vendor/kernel by scanning tokens
    if FREEBSD_RE.search(tl):
        name = "FreeBSD"
    elif OPENBSD_RE.search(tl):
        name = "OpenBSD"
    elif NETBSD_RE.search(tl):
        name = "NetBSD"
    else:
        name = "BSD"

    p.product = name
    p.vendor = name
    p.kernel_name = name.lower()

    # Prefer variant-anchored version pattern; fall back to generic semver
    x, y, z = _extract_version(text)
    p.version_major, p.version_minor, p.version_patch = x, y, z
    p.precision = precision_from_parts(x, y, z, None) if x else "product"

    # Channel from explicit markers/suffixes
    ch = BSD_CHANNEL_RE.search(text)
    if ch:
        p.channel = ch.group(1).upper()

    update_confidence(p, p.precision)
    return p


def _extract_version(text: str) -> tuple[int | None, int | None, int | None]:
    m = VARIANT_VERSION_RE.search(text)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2)) if m.group(2) else None
        patch = int(m.group(3)) if m.group(3) else None
        return major, minor, patch
    return parse_semver_like(text)
