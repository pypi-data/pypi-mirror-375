"""Juniper Junos parsing."""

import re

from os_normalizer.helpers import update_confidence
from os_normalizer.models import OSData

JUNOS_RE = re.compile(r"\bjunos\b", re.IGNORECASE)
JUNOS_VER_RE = re.compile(r"\b(\d{1,2}\.\d{1,2}R\d+(?:-\w+\d+)?)\b", re.IGNORECASE)
JUNOS_PKG_RE = re.compile(r"\b(jinstall-[a-z0-9_.-]+\.tgz)\b", re.IGNORECASE)
JUNOS_MODEL_RE = re.compile(r"\b(EX\d{3,4}-\d{2}[A-Z]?|QFX\d{3,4}\w*|SRX\d{3,4}\w*|MX\d{2,3}\w*)\b", re.IGNORECASE)


def parse_juniper(text: str, p: OSData) -> OSData:
    p.vendor = "Juniper"
    p.product = "Junos"
    p.family = p.family or "network-os"
    p.kernel_name = "junos"

    vm = JUNOS_VER_RE.search(text)
    if vm:
        ver = vm.group(1)
        p.evidence["version_raw"] = ver
        nums = re.findall(r"\d+", ver)
        if nums:
            p.version_major = int(nums[0])
        if len(nums) >= 2:
            p.version_minor = int(nums[1])
        p.version_build = ver
        p.precision = "minor"

    pkg = JUNOS_PKG_RE.search(text)
    if pkg:
        p.build_id = pkg.group(1)
        p.precision = "build"

    mdl = JUNOS_MODEL_RE.search(text)
    if mdl:
        p.hw_model = mdl.group(1)

    update_confidence(p, p.precision if p.precision in ("build", "minor") else "major")
    return p
