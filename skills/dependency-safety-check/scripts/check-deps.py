#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dependency security checker. Queries multiple sources to verify package safety.
Compatible with Python 2.7+ and Python 3.6+. No external dependencies.

Usage:
    python check-deps.py gray-matter@4.0.3 glob@11.0.0
    python check-deps.py --ecosystem pypi requests@2.31.0
"""

from __future__ import print_function, unicode_literals

import json
import sys
import time
import ssl
import os
import re

try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
    from urllib.parse import quote
except ImportError:
    from urllib2 import urlopen, Request, URLError, HTTPError
    from urllib import quote

# --- Config ---

DEFAULT_ECOSYSTEM = "npm"
THIRTY_DAYS = 30 * 24 * 3600
REQUEST_TIMEOUT = 15

# Disable SSL verification warnings for older Python versions
try:
    SSL_CONTEXT = ssl.create_default_context()
except AttributeError:
    SSL_CONTEXT = None


def fetch_json(url, method="GET", data=None, headers=None):
    """Fetch JSON from a URL. Returns parsed JSON or None on failure."""
    default_headers = {
        "User-Agent": "llm-wiki-dep-checker/1.0",
        "Accept": "application/json",
    }
    if headers:
        default_headers.update(headers)
    headers = default_headers

    try:
        if data is not None:
            if isinstance(data, dict):
                data = json.dumps(data).encode("utf-8")
                headers["Content-Type"] = "application/json"
            elif isinstance(data, str):
                data = data.encode("utf-8")

        req = Request(url, data=data, headers=headers)
        if method != "GET" and data is None:
            req.get_method = lambda: method

        kwargs = {"timeout": REQUEST_TIMEOUT}
        if SSL_CONTEXT:
            kwargs["context"] = SSL_CONTEXT

        resp = urlopen(req, **kwargs)
        body = resp.read().decode("utf-8")
        return json.loads(body)
    except (URLError, HTTPError, ValueError, IOError) as e:
        return {"_error": str(e)}


def fetch_text(url):
    """Fetch raw text from a URL. Returns string or None."""
    try:
        headers = {"User-Agent": "llm-wiki-dep-checker/1.0"}
        req = Request(url, headers=headers)
        kwargs = {"timeout": REQUEST_TIMEOUT}
        if SSL_CONTEXT:
            kwargs["context"] = SSL_CONTEXT
        resp = urlopen(req, **kwargs)
        return resp.read().decode("utf-8")
    except (URLError, HTTPError, IOError):
        return None


# --- Checkers ---


def check_npm_registry(name, version):
    """Check npm registry for package metadata and publish date."""
    result = {"source": "npm-registry", "findings": []}

    # Full package metadata
    pkg = fetch_json("https://registry.npmjs.org/%s" % quote(name, safe=""))
    if not pkg or "_error" in pkg:
        result["findings"].append({
            "severity": "error",
            "message": "Failed to fetch npm registry data: %s" % pkg.get("_error", "unknown"),
        })
        return result

    # Check if package exists
    if "name" not in pkg:
        result["findings"].append({
            "severity": "error",
            "message": "Package '%s' not found on npm" % name,
        })
        return result

    # Maintainers
    maintainers = pkg.get("maintainers", [])
    maintainer_names = [m.get("name", "?") for m in maintainers]
    result["maintainers"] = maintainer_names

    # Check version exists
    versions = pkg.get("versions", {})
    if version and version not in versions:
        result["findings"].append({
            "severity": "error",
            "message": "Version %s not found. Available: %s" % (
                version,
                ", ".join(sorted(versions.keys())[-5:]),
            ),
        })
        return result

    # Publish time
    time_map = pkg.get("time", {})
    if version and version in time_map:
        pub_time_str = time_map[version]
        # Parse ISO date
        try:
            # Handle both formats: 2019-06-28T... and 2019-06-28
            pub_date = pub_time_str[:10]
            pub_ts = time.mktime(time.strptime(pub_date, "%Y-%m-%d"))
            age_days = int((time.time() - pub_ts) / 86400)
            result["publish_date"] = pub_date
            result["age_days"] = age_days

            if age_days < 30:
                result["findings"].append({
                    "severity": "error",
                    "message": "Version %s was published %d days ago (< 30 days). REJECT." % (version, age_days),
                })
            else:
                result["findings"].append({
                    "severity": "ok",
                    "message": "Version %s published %d days ago (%s). Age OK." % (version, age_days, pub_date),
                })
        except (ValueError, OverflowError):
            result["findings"].append({
                "severity": "warning",
                "message": "Could not parse publish date: %s" % pub_time_str,
            })

    # Check for install scripts (postinstall, preinstall)
    ver_data = versions.get(version, {}) if version else {}
    scripts = ver_data.get("scripts", {})
    suspicious_scripts = [k for k in scripts if k in ("preinstall", "postinstall", "install")]
    if suspicious_scripts:
        result["findings"].append({
            "severity": "warning",
            "message": "Has install scripts: %s. Inspect before installing." % ", ".join(suspicious_scripts),
        })
    else:
        result["findings"].append({
            "severity": "ok",
            "message": "No preinstall/postinstall scripts.",
        })

    # Dependencies count
    deps = ver_data.get("dependencies", {})
    result["dependency_count"] = len(deps)
    result["dependencies"] = list(deps.keys())

    # Download count (last week)
    dl = fetch_json("https://api.npmjs.org/downloads/point/last-week/%s" % quote(name, safe=""))
    if dl and "downloads" in dl:
        result["weekly_downloads"] = dl["downloads"]
        if dl["downloads"] < 100:
            result["findings"].append({
                "severity": "warning",
                "message": "Very low weekly downloads: %d. Potential typosquat risk." % dl["downloads"],
            })

    # Repository info
    repo = pkg.get("repository", {})
    if isinstance(repo, dict):
        result["repository"] = repo.get("url", "")
    elif isinstance(repo, str):
        result["repository"] = repo

    return result


def check_osv(name, version, ecosystem="npm"):
    """Query OSV.dev for known vulnerabilities."""
    result = {"source": "osv.dev", "findings": []}

    query = {"package": {"name": name, "ecosystem": ecosystem}}
    if version:
        query["version"] = version

    resp = fetch_json("https://api.osv.dev/v1/query", data=query)
    if resp is None or (isinstance(resp, dict) and "_error" in resp):
        result["findings"].append({
            "severity": "warning",
            "message": "Failed to query OSV.dev: %s" % (resp.get("_error", "unknown") if resp else "no response"),
        })
        return result

    vulns = resp.get("vulns", [])
    if not vulns:
        result["findings"].append({
            "severity": "ok",
            "message": "No known vulnerabilities in OSV.dev.",
        })
    else:
        for v in vulns:
            vid = v.get("id", "?")
            summary = v.get("summary", "No summary")
            severity_list = v.get("severity", [])
            sev_str = ""
            for s in severity_list:
                if s.get("type") == "CVSS_V3":
                    sev_str = s.get("score", "")
            result["findings"].append({
                "severity": "error",
                "message": "[%s] %s (CVSS: %s)" % (vid, summary, sev_str or "N/A"),
            })

    result["vulnerability_count"] = len(vulns)
    return result


def check_github_advisory(name, ecosystem="npm"):
    """Search GitHub Advisory Database via API."""
    result = {"source": "github-advisory", "findings": []}

    # GitHub advisory search (public, no auth needed for basic search)
    url = "https://api.github.com/advisories?ecosystem=%s&affects=%s&per_page=10" % (
        quote(ecosystem, safe=""),
        quote(name, safe=""),
    )
    resp = fetch_json(url, headers={"Accept": "application/vnd.github+json"})

    if resp is None or (isinstance(resp, dict) and "_error" in resp):
        result["findings"].append({
            "severity": "info",
            "message": "GitHub Advisory API failed. Check manually at https://github.com/advisories?query=%s" % (
                quote(name, safe=""),
            ),
        })
        return result

    if isinstance(resp, list):
        if not resp:
            result["findings"].append({
                "severity": "ok",
                "message": "No advisories found in GitHub Advisory Database.",
            })
        else:
            for adv in resp[:5]:
                ghsa_id = adv.get("ghsa_id", "?")
                summary = adv.get("summary", "No summary")
                sev = adv.get("severity", "unknown")
                result["findings"].append({
                    "severity": "error" if sev in ("critical", "high") else "warning",
                    "message": "[%s] [%s] %s" % (ghsa_id, sev, summary),
                })
    else:
        # Might be an error object
        msg = resp.get("message", "unexpected response")
        result["findings"].append({
            "severity": "info",
            "message": "GitHub API: %s. Check manually at https://github.com/advisories?query=%s" % (
                msg[:80], quote(name, safe="")
            ),
        })

    return result


def parse_semver(version):
    """Parse a npm semver-ish version into comparable parts."""
    if not version:
        return None
    version = version.strip()
    if version.startswith("v"):
        version = version[1:]
    version = version.split("+", 1)[0]
    main_and_pre = version.split("-", 1)
    main = main_and_pre[0]
    pre = main_and_pre[1] if len(main_and_pre) > 1 else ""
    parts = main.split(".")
    if len(parts) < 1 or len(parts) > 3:
        return None

    nums = []
    for part in parts:
        if part in ("", "x", "X", "*"):
            nums.append(0)
        elif part.isdigit():
            nums.append(int(part))
        else:
            return None
    while len(nums) < 3:
        nums.append(0)

    return (nums[0], nums[1], nums[2], pre)


def compare_semver(a, b):
    """Compare parsed semver tuples; stable versions sort after prereleases."""
    for index in range(3):
        if a[index] < b[index]:
            return -1
        if a[index] > b[index]:
            return 1

    a_pre = a[3]
    b_pre = b[3]
    if a_pre == b_pre:
        return 0
    if not a_pre:
        return 1
    if not b_pre:
        return -1
    if a_pre < b_pre:
        return -1
    if a_pre > b_pre:
        return 1
    return 0


def semver_lt(a, b):
    return compare_semver(a, b) < 0


def semver_lte(a, b):
    return compare_semver(a, b) <= 0


def semver_gt(a, b):
    return compare_semver(a, b) > 0


def semver_gte(a, b):
    return compare_semver(a, b) >= 0


def version_bound_from_partial(version):
    """Return parsed lower bound and count of explicit numeric components."""
    version = version.strip()
    if version.startswith("v"):
        version = version[1:]
    version = version.split("+", 1)[0].split("-", 1)[0]
    parts = version.split(".")
    explicit = 0
    nums = []
    for part in parts[:3]:
        if part in ("", "x", "X", "*"):
            nums.append(0)
        elif part.isdigit():
            explicit += 1
            nums.append(int(part))
        else:
            return None, 0
    while len(nums) < 3:
        nums.append(0)
    return (nums[0], nums[1], nums[2], ""), explicit


def satisfies_comparator(parsed, comparator, version):
    bound = parse_semver(version)
    if not bound:
        return False
    if comparator in ("", "="):
        return compare_semver(parsed, bound) == 0
    if comparator == ">":
        return semver_gt(parsed, bound)
    if comparator == ">=":
        return semver_gte(parsed, bound)
    if comparator == "<":
        return semver_lt(parsed, bound)
    if comparator == "<=":
        return semver_lte(parsed, bound)
    return False


def satisfies_simple_range(parsed, range_part):
    """Support common npm ranges without pulling in a semver dependency."""
    range_part = range_part.strip()
    if not range_part or range_part in ("*", "latest"):
        return True
    range_part = range_part.replace(",", " ")
    tokens = [token for token in range_part.split() if token]
    index = 0

    while index < len(tokens):
        token = tokens[index]
        if token in ("-", "||"):
            return False

        if token in (">", ">=", "<", "<=", "="):
            if index + 1 >= len(tokens):
                return False
            comparator = token
            version = tokens[index + 1]
            index += 2
        else:
            match = re.match(r"^(>=|<=|>|<|=)?(.+)$", token)
            if not match:
                return False
            comparator = match.group(1) or ""
            version = match.group(2)
            index += 1

        if version in ("*", "x", "X"):
            continue

        if version.startswith("^"):
            lower, explicit = version_bound_from_partial(version[1:])
            if not lower or not semver_gte(parsed, lower):
                return False
            major, minor, patch = lower[0], lower[1], lower[2]
            if major > 0:
                upper = (major + 1, 0, 0, "")
            elif minor > 0:
                upper = (0, minor + 1, 0, "")
            else:
                upper = (0, 0, patch + 1, "")
            if not semver_lt(parsed, upper):
                return False
            continue

        if version.startswith("~"):
            lower, explicit = version_bound_from_partial(version[1:])
            if not lower or not semver_gte(parsed, lower):
                return False
            major, minor = lower[0], lower[1]
            if explicit <= 1:
                upper = (major + 1, 0, 0, "")
            else:
                upper = (major, minor + 1, 0, "")
            if not semver_lt(parsed, upper):
                return False
            continue

        if any(wildcard in version for wildcard in ("x", "X", "*")):
            lower, explicit = version_bound_from_partial(version)
            if not lower or not semver_gte(parsed, lower):
                return False
            if explicit == 0:
                continue
            if explicit == 1:
                upper = (lower[0] + 1, 0, 0, "")
            elif explicit == 2:
                upper = (lower[0], lower[1] + 1, 0, "")
            else:
                upper = (lower[0], lower[1], lower[2] + 1, "")
            if not semver_lt(parsed, upper):
                return False
            continue

        if comparator:
            if not satisfies_comparator(parsed, comparator, version):
                return False
            continue

        lower, explicit = version_bound_from_partial(version)
        if not lower:
            return False
        if explicit < 3:
            if not semver_gte(parsed, lower):
                return False
            if explicit == 1:
                upper = (lower[0] + 1, 0, 0, "")
            else:
                upper = (lower[0], lower[1] + 1, 0, "")
            if not semver_lt(parsed, upper):
                return False
        elif not satisfies_comparator(parsed, "=", version):
            return False

    return True


def satisfies_npm_range(version, range_spec):
    parsed = parse_semver(version)
    if not parsed:
        return False

    for part in (range_spec or "latest").split("||"):
        if satisfies_simple_range(parsed, part):
            return True
    return False


def resolve_npm_dependency_version(pkg, range_spec):
    """Resolve a dependency range to the highest published satisfying version."""
    versions = pkg.get("versions", {})
    candidates = []
    for version in versions:
        parsed = parse_semver(version)
        if not parsed:
            continue
        if parsed[3] and "-" not in (range_spec or ""):
            continue
        if satisfies_npm_range(version, range_spec):
            candidates.append((parsed, version))

    if not candidates:
        dist_tags = pkg.get("dist-tags", {})
        latest = dist_tags.get("latest", "")
        if latest and satisfies_npm_range(latest, range_spec):
            return latest
        return None

    candidates.sort(key=lambda item: item[0])
    return candidates[-1][1]


def check_socket_dev(name, version, ecosystem="npm"):
    """Check Socket.dev for package risk signals (public page scrape)."""
    result = {"source": "socket.dev", "findings": []}

    # Socket.dev has a public package page we can reference
    url = "https://socket.dev/%s/package/%s/overview/%s" % (ecosystem, quote(name, safe=""), version or "")
    result["findings"].append({
        "severity": "info",
        "message": "Manual check: %s" % url,
    })
    return result


def check_snyk(name, ecosystem="npm"):
    """Reference Snyk vulnerability DB."""
    result = {"source": "snyk", "findings": []}

    if ecosystem == "npm":
        url = "https://security.snyk.io/package/npm/%s" % quote(name, safe="")
    elif ecosystem == "pypi":
        url = "https://security.snyk.io/package/pip/%s" % quote(name, safe="")
    else:
        url = "https://security.snyk.io/search?q=%s" % quote(name, safe="")

    result["findings"].append({
        "severity": "info",
        "message": "Manual check: %s" % url,
    })
    return result


def check_transitive_deps(name, version, ecosystem="npm"):
    """Check transitive dependencies for recent publish dates and vulnerabilities."""
    result = {"source": "transitive-deps", "findings": []}

    if ecosystem != "npm":
        result["findings"].append({
            "severity": "info",
            "message": "Transitive dependency check only supported for npm currently.",
        })
        return result

    pkg = fetch_json("https://registry.npmjs.org/%s/%s" % (quote(name, safe=""), quote(version or "latest", safe="")))
    if not pkg or "_error" in pkg:
        result["findings"].append({
            "severity": "warning",
            "message": "Failed to fetch version metadata for transitive check.",
        })
        return result

    deps = pkg.get("dependencies", {})
    if not deps:
        result["findings"].append({
            "severity": "ok",
            "message": "No runtime dependencies.",
        })
        return result

    issues = []
    checked = []

    for dep_name, dep_range in deps.items():
        dep_pkg = fetch_json("https://registry.npmjs.org/%s" % quote(dep_name, safe=""))
        if not dep_pkg or "_error" in dep_pkg:
            issues.append("%s: failed to fetch" % dep_name)
            continue

        resolved = resolve_npm_dependency_version(dep_pkg, dep_range)
        if not resolved:
            issues.append("%s@%s: failed to resolve satisfying version" % (dep_name, dep_range))
            continue

        time_map = dep_pkg.get("time", {})
        if resolved and resolved in time_map:
            pub_date = time_map[resolved][:10]
            try:
                pub_ts = time.mktime(time.strptime(pub_date, "%Y-%m-%d"))
                age_days = int((time.time() - pub_ts) / 86400)
                checked.append("%s@%s from %s (%dd)" % (dep_name, resolved, dep_range, age_days))
                if age_days < 7:
                    issues.append("%s@%s published %d days ago — VERY RECENT" % (dep_name, resolved, age_days))
                elif age_days < 30:
                    issues.append("%s@%s published %d days ago — recent transitive dependency" % (dep_name, resolved, age_days))
            except (ValueError, OverflowError):
                pass

        # Quick OSV check for each resolved dep version.
        osv_resp = fetch_json("https://api.osv.dev/v1/query", data={
            "package": {"name": dep_name, "ecosystem": "npm"},
            "version": resolved,
        })
        if osv_resp and "vulns" in osv_resp and osv_resp["vulns"]:
            vuln_count = len(osv_resp["vulns"])
            issues.append("%s@%s: %d known vulnerability(ies) in OSV.dev" % (dep_name, resolved, vuln_count))

        # Rate limit courtesy
        time.sleep(0.2)

    if issues:
        for issue in issues:
            result["findings"].append({"severity": "warning", "message": issue})
    else:
        result["findings"].append({
            "severity": "ok",
            "message": "All %d direct dependencies checked. No issues." % len(deps),
        })

    result["checked_deps"] = checked
    return result


# --- Main ---

def check_package(name, version, ecosystem):
    """Run all checks on a single package."""
    print("=" * 60)
    print("Package: %s@%s (%s)" % (name, version or "latest", ecosystem))
    print("=" * 60)

    checks = []

    if ecosystem == "npm":
        checks.append(check_npm_registry(name, version))
    checks.append(check_osv(name, version, ecosystem))
    checks.append(check_github_advisory(name, ecosystem))
    checks.append(check_socket_dev(name, version, ecosystem))
    checks.append(check_snyk(name, ecosystem))

    if ecosystem == "npm":
        checks.append(check_transitive_deps(name, version, ecosystem))

    has_error = False
    has_warning = False

    for check in checks:
        print("\n[%s]" % check["source"])

        # Print extra metadata if available
        for key in ("maintainers", "publish_date", "age_days", "weekly_downloads",
                     "dependency_count", "dependencies", "repository",
                     "vulnerability_count", "checked_deps"):
            if key in check:
                val = check[key]
                if isinstance(val, list) and len(val) > 10:
                    val = val[:10] + ["... (%d total)" % len(val)]
                print("  %s: %s" % (key, val))

        for f in check.get("findings", []):
            sev = f["severity"]
            icon = {"ok": "OK", "info": "INFO", "warning": "WARN", "error": "FAIL"}.get(sev, sev.upper())
            print("  [%s] %s" % (icon, f["message"]))
            if sev == "error":
                has_error = True
            if sev == "warning":
                has_warning = True

    print("\n" + "-" * 60)
    if has_error:
        print("VERDICT: REJECT — critical issues found.")
    elif has_warning:
        print("VERDICT: REVIEW — warnings found, manual verification recommended.")
    else:
        print("VERDICT: PASS — no issues detected.")
    print("-" * 60 + "\n")

    return not has_error


def main():
    args = sys.argv[1:]
    ecosystem = DEFAULT_ECOSYSTEM

    # Parse --ecosystem flag
    filtered_args = []
    i = 0
    while i < len(args):
        if args[i] == "--ecosystem" and i + 1 < len(args):
            ecosystem = args[i + 1]
            i += 2
        elif args[i].startswith("--ecosystem="):
            ecosystem = args[i].split("=", 1)[1]
            i += 1
        elif args[i] in ("-h", "--help"):
            print("Usage: python check-deps.py [--ecosystem npm|pypi|cargo] pkg@version [pkg@version ...]")
            print("")
            print("Checks multiple security databases for known vulnerabilities,")
            print("supply chain risks, and publish date compliance (30-day rule).")
            print("")
            print("Examples:")
            print("  python check-deps.py gray-matter@4.0.3 glob@11.0.0")
            print("  python check-deps.py --ecosystem pypi requests@2.31.0")
            sys.exit(0)
        else:
            filtered_args.append(args[i])
            i += 1

    if not filtered_args:
        print("Error: No packages specified.", file=sys.stderr)
        print("Usage: python check-deps.py [--ecosystem npm|pypi|cargo] pkg@version [pkg@version ...]", file=sys.stderr)
        sys.exit(1)

    packages = []
    for arg in filtered_args:
        if "@" in arg and not arg.startswith("@"):
            name, version = arg.rsplit("@", 1)
        elif arg.startswith("@") and "@" in arg[1:]:
            # Scoped npm package like @scope/name@version
            rest = arg[1:]
            parts = rest.rsplit("@", 1)
            if len(parts) == 2:
                name = "@" + parts[0]
                version = parts[1]
            else:
                name = arg
                version = None
        else:
            name = arg
            version = None
        packages.append((name, version))

    all_pass = True
    for name, version in packages:
        if not check_package(name, version, ecosystem):
            all_pass = False

    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
