"""Fortinet FortiOS parsing."""

import re

from os_normalizer.helpers import update_confidence
from os_normalizer.models import OSData

FORTI_RE = re.compile(r"\bforti(os|gate)\b", re.IGNORECASE)
FORTI_VER_RE = re.compile(r"\bv?(\d+\.\d+(?:\.\d+)?)\b", re.IGNORECASE)
FORTI_BUILD_RE = re.compile(r"\bbuild\s?(\d{3,5})\b", re.IGNORECASE)
FORTI_IMG_RE = re.compile(r"\b(FGT_[0-9.]+-build\d{3,5})\b", re.IGNORECASE)
FORTI_MODEL_RE = re.compile(r"\b(FortiGate-?\d+[A-Z]?|FG-\d+[A-Z]?)\b", re.IGNORECASE)
FORTI_CHANNEL_RE = re.compile(r"\((GA|Patch|Beta)\)", re.IGNORECASE)


def parse_fortinet(text: str, p: OSData) -> OSData:
    p.vendor = "Fortinet"
    p.product = "FortiOS"
    p.family = p.family or "network-os"
    p.kernel_name = "fortios"

    ver = FORTI_VER_RE.search(text)
    if ver:
        v = ver.group(1)
        nums = re.findall(r"\d+", v)
        if nums:
            p.version_major = int(nums[0])
        if len(nums) >= 2:
            p.version_minor = int(nums[1])
        if len(nums) >= 3:
            p.version_patch = int(nums[2])
        p.version_build = v
        p.precision = (
            "patch" if p.version_patch is not None else ("minor" if p.version_minor is not None else "major")
        )

    bld = FORTI_BUILD_RE.search(text)
    if bld:
        p.version_build = (p.version_build or "") + f"+build.{bld.group(1)}"
        p.precision = "build"

    img = FORTI_IMG_RE.search(text)
    if img:
        p.build_id = img.group(1)
        p.precision = "build"

    mdl = FORTI_MODEL_RE.search(text)
    if mdl:
        p.hw_model = mdl.group(1).replace("FortiGate-", "FG-")

    ch = FORTI_CHANNEL_RE.search(text)
    if ch:
        p.channel = ch.group(1).upper()

    update_confidence(p, p.precision if p.precision in ("build", "patch") else "minor")
    return p
