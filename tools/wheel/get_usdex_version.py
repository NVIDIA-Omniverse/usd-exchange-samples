# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

"""
Script to extract usd-exchange version from target-deps.packman.xml
and format it for use in test scripts.
"""

import argparse
import os
import re
import sys

import packmanapi


def format_version(package_name, version, platform_target_abi):
    """
    Format the version string by extracting USD version from package name
    and incorporating it into the version when appropriate.

    Args:
        package_name (str): Package name like "usd-exchange_usd_25.05_py_3.10"
        version (str): Version string like "2.0.1+main.1061.15bda203.gl.${platform_target_abi}.release"

    Returns:
        str: Formatted version string
    """
    if not version or not package_name:
        return version

    # Extract USD version from package name (e.g., "usd-exchange_usd_25.05_py_3.10" -> "25.05")
    usd_version_match = re.search(r"usd_(\d+\.\d+)", package_name)
    usd_version = usd_version_match.group(1) if usd_version_match else None

    # Remove ".{platform_target_abi}.*" from the end of the version string
    cleaned_version = re.sub(rf"\.{platform_target_abi}.*$", "", version)
    # Remove "+{platform_target_abi}.*" from the end of the version string (for tagged releases)
    cleaned_version = re.sub(rf"\+{platform_target_abi}.*$", "", cleaned_version)
    # Remove any prerelease dash (e.g., "2.1.0-rc1" -> "2.1.0rc1")
    cleaned_version = cleaned_version.replace("-", "")

    # Check if the version has decoration beyond just platform/config variables
    # If it's just "X.Y.Z" after cleanup, don't add USD version
    if re.match(r"^\d+\.\d+\.\d+$", cleaned_version):
        # Simple version like "2.0.1" - don't add USD version
        return cleaned_version
    elif usd_version and "+" in cleaned_version:
        # Version has decoration, insert USD version
        # Convert "25.05" to "usd2505" format
        usd_formatted = f"usd{usd_version.replace('.', '')}"
        # Insert after the '+' sign
        parts = cleaned_version.split("+", 1)
        if len(parts) == 2:
            return f"{parts[0]}+{usd_formatted}.{parts[1]}"

    return cleaned_version


def get_usdex_version():
    """
    Extract usd-exchange version from target-deps.packman.xml and format it.

    Returns:
        str: Formatted version string without platform/config variables
    """
    # Get the script directory and construct path to packman XML
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.join(script_dir, "..", "..")
    packman_file = os.path.join(repo_root, "deps", "target-deps.packman.xml")
    if not os.path.exists(packman_file):
        raise FileNotFoundError(f"Could not find packman file: {packman_file}")

    # The platform and config are required by packmanapi but get stripped from the version below, so any currently
    # published abi works; the windows package is tagged windows_v143_x86_64
    platform_target_abi = "windows_v143_x86_64"

    try:
        # Resolve the usd-exchange dependency using packmanapi
        info = packmanapi.resolve_dependency(
            "usd-exchange",
            packman_file,
            tokens={"platform_target_abi": platform_target_abi, "config": "release"},
        )
    except packmanapi.PackmanError as e:
        print(f"Error resolving dependency: {e}")
        sys.exit(1)

    remote_filename = info["remote_filename"]
    package_name, version = remote_filename.split("@")
    if version and package_name:
        return format_version(package_name, version, platform_target_abi)

    raise ValueError("Could not resolve usd-exchange package version in packman file")


def __test_format_version():
    """Test the format_version function with the two specific cases."""
    print("Testing format_version function...")

    platform_target_abi = "windows-x86_64"

    # Test case 1: Version with decoration should include USD version
    package_name = "usd-exchange_usd_25.05_py_3.10"
    version = f"2.0.1+main.1061.15bda203.gl.{platform_target_abi}.release.7z"
    expected = "2.0.1+usd2505.main.1061.15bda203.gl"
    result = format_version(package_name, version, platform_target_abi)
    all_passed = result == expected

    print(f"Test 1:")
    print(f"  Package: {package_name}")
    print(f"  Version: {version}")
    print(f"  Expected: {expected}")
    print(f"  Result:   {result}")
    print(f"  Status:   {'PASS' if result == expected else 'FAIL'}\n")

    # Test case 2: Simple version should not include USD version
    package_name = "usd-exchange_usd_25.05_py_3.10"
    version = f"2.0.1+{platform_target_abi}.release.7z"
    expected = "2.0.1"
    result = format_version(package_name, version, platform_target_abi)
    all_passed &= result == expected

    print(f"Test 2:")
    print(f"  Package: {package_name}")
    print(f"  Version: {version}")
    print(f"  Expected: {expected}")
    print(f"  Result:   {result}")
    print(f"  Status:   {'PASS' if result == expected else 'FAIL'}\n")

    # Test case 3: Prerelease version should not include USD version and not have a dash
    package_name = "usd-exchange_usd_25.05_py_3.10"
    version = f"2.1.0-rc1+{platform_target_abi}.release.7z"
    expected = "2.1.0rc1"
    result = format_version(package_name, version, platform_target_abi)
    all_passed &= result == expected

    print(f"Test 3:")
    print(f"  Package: {package_name}")
    print(f"  Version: {version}")
    print(f"  Expected: {expected}")
    print(f"  Result:   {result}")
    print(f"  Status:   {'PASS' if result == expected else 'FAIL'}\n")

    # Summary
    print(f"Overall test result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    return all_passed


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract usd-exchange version from target-deps.packman.xml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python get_usdex_version.py                    # Output version string
  python get_usdex_version.py --test             # Run tests
        """,
    )

    parser.add_argument("--test", action="store_true", help="Run test cases to verify version formatting")

    args = parser.parse_args()

    try:
        # Check if we're running tests
        if args.test:
            success = __test_format_version()
            sys.exit(0 if success else 1)

        version = get_usdex_version()

        # Just output the version string
        print(version)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
