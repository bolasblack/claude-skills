#!/usr/bin/env python3
"""Black-box tests for the materialized Lefthook runner."""

import gzip
import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest


RUNNER_SOURCE = Path(__file__).with_name("lefthook")
OFFICIAL_LINUX_X86_64_CHECKSUM = (
    "0b14162a0bb2f0c64ae0759f6102f6e19c4d00981666a8ac73d4f5a6878ada4f"
)
FIXTURE_LINUX_X86_64_CHECKSUM = (
    "db26a6a31301ed5859a5c654f7d669072826f9557f264335efcae645ee48d895"
)
PLATFORM_CASES = (
    (
        "Linux",
        "x86_64",
        "linux-x86_64",
        "lefthook_2.1.10_Linux_x86_64.gz",
        OFFICIAL_LINUX_X86_64_CHECKSUM,
        "lefthook",
    ),
    (
        "Linux",
        "aarch64",
        "linux-arm64",
        "lefthook_2.1.10_Linux_aarch64.gz",
        "6380a6ad6dd484466fd69bd83f24491d6ec27dc0b84e837be025620f7c4e11e3",
        "lefthook",
    ),
    (
        "Darwin",
        "x86_64",
        "darwin-x86_64",
        "lefthook_2.1.10_MacOS_x86_64.gz",
        "49d905f28ca46442cb236060058b252da650b5f7b864bd275b61aa46945e8c4a",
        "lefthook",
    ),
    (
        "Darwin",
        "arm64",
        "darwin-arm64",
        "lefthook_2.1.10_MacOS_arm64.gz",
        "1dd4dc7b4c50efb1f9d9122cd6535c793738d6e59751c228d49f768ec9dbb604",
        "lefthook",
    ),
    (
        "MINGW64_NT-10.0",
        "x86_64",
        "windows-x86_64",
        "lefthook_2.1.10_Windows_x86_64.gz",
        "beabbce824641ae71229ed11dd8634f47148921cb649d25c90441b737481494a",
        "lefthook.exe",
    ),
    (
        "MSYS_NT-10.0",
        "aarch64",
        "windows-arm64",
        "lefthook_2.1.10_Windows_arm64.gz",
        "933b3c2aaa016d84cd2b3926ea9b99c3febdc6bb778bfd854640223a3a4c5e50",
        "lefthook.exe",
    ),
)


class LefthookRunnerTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="lefthook runner "
        )
        self.addCleanup(self.temporary_directory.cleanup)
        self.repo = Path(self.temporary_directory.name, "repo with spaces")
        self.repo.mkdir()
        subprocess.run(
            ["git", "init", "--quiet"], cwd=self.repo, check=True
        )
        self.runner = self.repo / "scripts" / "lefthook"
        self.runner.parent.mkdir()
        shutil.copyfile(RUNNER_SOURCE, self.runner)
        self.repo.joinpath("lefthook.yml").write_text(
            'min_version: "2.1.10"\n', encoding="utf-8"
        )

    def write_executable(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def test_runtime_forwards_the_process_contract_to_the_cached_binary(self):
        binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
            / "lefthook"
        )
        self.write_executable(
            binary,
            """#!/bin/sh
if [ "${1-}" = version ]; then
  printf '2.1.10\n'
  exit 0
fi
for argument do
  printf '%s\\0' "$argument"
done > "$FAKE_ARGV_LOG"
cat > "$FAKE_STDIN_LOG"
printf 'forwarded stdout'
printf 'forwarded stderr' >&2
exit 23
""",
        )

        sentinel_log = self.repo / "unexpected-command.log"
        shim_directory = self.repo / "shims"
        for command in ("curl", "lefthook", "mise"):
            self.write_executable(
                shim_directory / command,
                f"#!/bin/sh\nprintf '%s\\n' {command} >> '{sentinel_log}'\nexit 99\n",
            )

        argv_log = self.repo / "argv.log"
        stdin_log = self.repo / "stdin.log"
        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_ARGV_LOG": str(argv_log),
                "FAKE_STDIN_LOG": str(stdin_log),
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            [
                "sh",
                str(self.runner),
                "run",
                "pre-push",
                "origin",
                "url with spaces",
            ],
            cwd=self.repo,
            env=environment,
            input=b"pre-push stdin\n",
            capture_output=True,
        )

        self.assertEqual(23, result.returncode)
        self.assertEqual(b"forwarded stdout", result.stdout)
        self.assertEqual(b"forwarded stderr", result.stderr)
        self.assertEqual(
            [b"run", b"pre-push", b"origin", b"url with spaces", b""],
            argv_log.read_bytes().split(b"\0"),
        )
        self.assertEqual(b"pre-push stdin\n", stdin_log.read_bytes())
        self.assertFalse(sentinel_log.exists())

    def test_runtime_accepts_each_supported_yaml_config_name(self):
        self.repo.joinpath("lefthook.yml").unlink()
        binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
            / "lefthook"
        )
        self.write_executable(
            binary,
            "#!/bin/sh\nprintf '2.1.10\\n'\n",
        )

        for relative_path in (
            "lefthook.yml",
            "lefthook.yaml",
            ".lefthook.yml",
            ".lefthook.yaml",
            ".config/lefthook.yml",
            ".config/lefthook.yaml",
        ):
            with self.subTest(config=relative_path):
                config = self.repo / relative_path
                config.parent.mkdir(parents=True, exist_ok=True)
                config.write_text(
                    'min_version: "2.1.10"\n', encoding="utf-8"
                )

                result = subprocess.run(
                    ["sh", "./scripts/lefthook", "version"],
                    cwd=self.repo,
                    capture_output=True,
                )

                self.assertEqual(
                    0, result.returncode, result.stderr.decode()
                )
                config.unlink()

    def test_runtime_accepts_a_plain_exact_min_version(self):
        self.repo.joinpath("lefthook.yml").write_text(
            "min_version: 2.1.10\n", encoding="utf-8"
        )
        binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
            / "lefthook"
        )
        self.write_executable(
            binary,
            "#!/bin/sh\nprintf '2.1.10\\n'\n",
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "version"],
            cwd=self.repo,
            capture_output=True,
        )

        self.assertEqual(0, result.returncode, result.stderr.decode())

    def test_runner_pins_its_selected_config_for_setup_and_runtime(self):
        alternate_config = self.repo / "alternate.yml"
        alternate_config.write_text(
            'min_version: "2.1.10"\n', encoding="utf-8"
        )
        binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
            / "lefthook"
        )
        config_log = self.repo / "lefthook-config.log"
        self.write_executable(
            binary,
            """#!/bin/sh
if [ "${1-}" = version ]; then
  printf '2.1.10\\n'
  exit 0
fi
printf '%s|%s\\n' "${LEFTHOOK_CONFIG-}" "${1-}" >> "$FAKE_CONFIG_LOG"
exit 0
""",
        )
        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_CONFIG_LOG": str(config_log),
                "GIT_CONFIG_GLOBAL": os.devnull,
                "LEFTHOOK_CONFIG": str(alternate_config),
            }
        )

        setup = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )
        runtime = subprocess.run(
            ["sh", "./scripts/lefthook", "run", "pre-commit"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertEqual(0, setup.returncode, setup.stderr.decode())
        self.assertEqual(0, runtime.returncode, runtime.stderr.decode())
        expected_config = str(self.repo / "lefthook.yml")
        self.assertEqual(
            [
                f"{expected_config}|validate",
                f"{expected_config}|install",
                f"{expected_config}|check-install",
                f"{expected_config}|run",
            ],
            config_log.read_text(encoding="utf-8").splitlines(),
        )

    def test_install_uses_mise_for_a_mise_project_and_installs_hooks(self):
        self.repo.joinpath("mise.toml").write_text(
            '[tools]\npython = "3.12"\n', encoding="utf-8"
        )
        subprocess.run(
            ["git", "add", "mise.toml"], cwd=self.repo, check=True
        )

        lefthook_log = self.repo / "lefthook.log"
        fake_lefthook = self.repo / "fake-lefthook"
        self.write_executable(
            fake_lefthook,
            """#!/bin/sh
if [ "$1" = version ]; then
  printf '2.1.10\\n'
  exit 0
fi
printf '%s\\n' "$1" >> "$FAKE_LEFTHOOK_LOG"
exit 0
""",
        )

        mise_log = self.repo / "mise.log"
        shim_directory = self.repo / "install-shims"
        self.write_executable(
            shim_directory / "mise",
            """#!/bin/sh
printf '%s\\n' "$*" >> "$FAKE_MISE_LOG"
if [ "$1" = -C ] && [ "${3-}" = help ] && [ "${4-}" = install-into ]; then
  exit 0
fi
if [ "$1" = -C ] && [ "$3" = install-into ] && \
   [ "$4" = lefthook@2.1.10 ] && [ "$5" = "$2" ]; then
  cp "$FAKE_LEFTHOOK_SOURCE" "$5/lefthook"
  chmod +x "$5/lefthook"
  exit 0
fi
exit 91
""",
        )
        unexpected_download = self.repo / "unexpected-download.log"
        self.write_executable(
            shim_directory / "curl",
            f"#!/bin/sh\nprintf download > '{unexpected_download}'\nexit 92\n",
        )

        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_LEFTHOOK_LOG": str(lefthook_log),
                "FAKE_LEFTHOOK_SOURCE": str(fake_lefthook),
                "FAKE_MISE_LOG": str(mise_log),
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        installed_binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
            / "lefthook"
        )
        self.assertEqual(0, result.returncode, result.stderr.decode())
        self.assertTrue(os.access(installed_binary, os.X_OK))
        self.assertEqual(
            ["validate", "install", "check-install"],
            lefthook_log.read_text(encoding="utf-8").splitlines(),
        )
        self.assertIn(
            "help install-into", mise_log.read_text(encoding="utf-8")
        )
        self.assertIn(
            "lefthook@2.1.10", mise_log.read_text(encoding="utf-8")
        )
        self.assertFalse(unexpected_download.exists())
        self.assertIsNone(
            subprocess.run(
                ["git", "config", "--local", "--get", "core.hooksPath"],
                cwd=self.repo,
                capture_output=True,
                text=True,
            ).stdout.strip()
            or None
        )

    def test_install_downloads_and_verifies_when_the_project_does_not_use_mise(self):
        fake_lefthook_body = b"""#!/bin/sh
if [ "$1" = version ]; then
  printf '2.1.10\\n'
  exit 0
fi
printf '%s\\n' "$1" >> "$FAKE_LEFTHOOK_LOG"
exit 0
"""
        release_asset = self.repo / "release-asset.gz"
        release_asset.write_bytes(gzip.compress(fake_lefthook_body, mtime=0))
        self.assertEqual(
            FIXTURE_LINUX_X86_64_CHECKSUM,
            hashlib.sha256(release_asset.read_bytes()).hexdigest(),
        )

        runner_text = self.runner.read_text(encoding="utf-8")
        self.runner.write_text(
            runner_text.replace(
                OFFICIAL_LINUX_X86_64_CHECKSUM,
                FIXTURE_LINUX_X86_64_CHECKSUM,
            ),
            encoding="utf-8",
        )

        lefthook_log = self.repo / "downloaded-lefthook.log"
        curl_log = self.repo / "curl.log"
        shim_directory = self.repo / "download-shims"
        self.write_executable(
            shim_directory / "curl",
            """#!/bin/sh
output=
url=
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o) output=$2; shift 2 ;;
    https://*) url=$1; shift ;;
    *) shift ;;
  esac
done
cp "$FAKE_RELEASE_ASSET" "$output"
printf '%s\\n' "$url" > "$FAKE_CURL_LOG"
""",
        )

        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_CURL_LOG": str(curl_log),
                "FAKE_LEFTHOOK_LOG": str(lefthook_log),
                "FAKE_RELEASE_ASSET": str(release_asset),
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        installed_binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
            / "lefthook"
        )
        self.assertEqual(0, result.returncode, result.stderr.decode())
        self.assertTrue(os.access(installed_binary, os.X_OK))
        self.assertEqual(
            ["validate", "install", "check-install"],
            lefthook_log.read_text(encoding="utf-8").splitlines(),
        )
        self.assertEqual(
            "https://github.com/evilmartians/lefthook/releases/download/"
            "v2.1.10/lefthook_2.1.10_Linux_x86_64.gz",
            curl_log.read_text(encoding="utf-8").strip(),
        )

    def test_install_replaces_a_mismatched_cached_binary(self):
        installed_binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
            / "lefthook"
        )
        self.write_executable(
            installed_binary,
            "#!/bin/sh\nprintf '9.9.9\\n'\n",
        )
        fake_lefthook_body = b"""#!/bin/sh
if [ "$1" = version ]; then
  printf '2.1.10\\n'
  exit 0
fi
printf '%s\\n' "$1" >> "$FAKE_LEFTHOOK_LOG"
exit 0
"""
        release_asset = self.repo / "replacement-release-asset.gz"
        release_asset.write_bytes(gzip.compress(fake_lefthook_body, mtime=0))
        fixture_checksum = hashlib.sha256(
            release_asset.read_bytes()
        ).hexdigest()
        self.runner.write_text(
            RUNNER_SOURCE.read_text(encoding="utf-8").replace(
                OFFICIAL_LINUX_X86_64_CHECKSUM, fixture_checksum
            ),
            encoding="utf-8",
        )

        lefthook_log = self.repo / "replacement-lefthook.log"
        shim_directory = self.repo / "replacement-shims"
        self.write_executable(
            shim_directory / "curl",
            """#!/bin/sh
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o) output=$2; shift 2 ;;
    *) shift ;;
  esac
done
cp "$FAKE_RELEASE_ASSET" "$output"
""",
        )
        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_LEFTHOOK_LOG": str(lefthook_log),
                "FAKE_RELEASE_ASSET": str(release_asset),
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertEqual(0, result.returncode, result.stderr.decode())
        self.assertEqual(
            "2.1.10",
            subprocess.run(
                [installed_binary, "version"],
                cwd=self.repo,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip(),
        )
        self.assertEqual(
            ["validate", "install", "check-install"],
            lefthook_log.read_text(encoding="utf-8").splitlines(),
        )

    def test_direct_install_maps_each_supported_platform_to_its_release_asset(self):
        fake_lefthook_body = b"""#!/bin/sh
if [ "$1" = version ]; then
  printf '2.1.10\\n'
  exit 0
fi
exit 0
"""
        release_asset = self.repo / "platform-release-asset.gz"
        release_asset.write_bytes(gzip.compress(fake_lefthook_body, mtime=0))
        fixture_checksum = hashlib.sha256(
            release_asset.read_bytes()
        ).hexdigest()
        shim_directory = self.repo / "platform-shims"
        curl_log = self.repo / "platform-curl.log"
        self.write_executable(
            shim_directory / "uname",
            """#!/bin/sh
case "$1" in
  -s) printf '%s\\n' "$FAKE_UNAME_S" ;;
  -m) printf '%s\\n' "$FAKE_UNAME_M" ;;
  *) exit 2 ;;
esac
""",
        )
        self.write_executable(
            shim_directory / "curl",
            """#!/bin/sh
output=
url=
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o) output=$2; shift 2 ;;
    https://*) url=$1; shift ;;
    *) shift ;;
  esac
done
cp "$FAKE_RELEASE_ASSET" "$output"
printf '%s\\n' "$url" > "$FAKE_CURL_LOG"
""",
        )

        base_environment = os.environ.copy()
        base_environment.update(
            {
                "FAKE_CURL_LOG": str(curl_log),
                "FAKE_RELEASE_ASSET": str(release_asset),
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{base_environment['PATH']}",
            }
        )

        for (
            system,
            machine,
            platform,
            asset,
            official_checksum,
            binary_name,
        ) in PLATFORM_CASES:
            with self.subTest(system=system, machine=machine):
                runner_text = RUNNER_SOURCE.read_text(encoding="utf-8")
                self.runner.write_text(
                    runner_text.replace(official_checksum, fixture_checksum),
                    encoding="utf-8",
                )
                environment = base_environment | {
                    "FAKE_UNAME_S": system,
                    "FAKE_UNAME_M": machine,
                }

                result = subprocess.run(
                    ["sh", "./scripts/lefthook", "install"],
                    cwd=self.repo,
                    env=environment,
                    capture_output=True,
                )

                installed_binary = (
                    self.repo
                    / ".git"
                    / "lefthook"
                    / "2.1.10"
                    / platform
                    / binary_name
                )
                self.assertEqual(
                    0, result.returncode, result.stderr.decode()
                )
                self.assertTrue(os.access(installed_binary, os.X_OK))
                self.assertTrue(
                    curl_log.read_text(encoding="utf-8")
                    .strip()
                    .endswith(f"/{asset}")
                )
                shutil.rmtree(self.repo / ".git" / "lefthook")
                curl_log.unlink()

    def test_direct_install_uses_shasum_when_sha256sum_is_unavailable(self):
        fake_lefthook_body = b"""#!/bin/sh
if [ "$1" = version ]; then
  printf '2.1.10\\n'
  exit 0
fi
exit 0
"""
        release_asset = self.repo / "shasum-release-asset.gz"
        release_asset.write_bytes(gzip.compress(fake_lefthook_body, mtime=0))
        fixture_checksum = hashlib.sha256(
            release_asset.read_bytes()
        ).hexdigest()
        official_checksum = next(
            item[4]
            for item in PLATFORM_CASES
            if item[0:2] == ("Darwin", "x86_64")
        )
        self.runner.write_text(
            RUNNER_SOURCE.read_text(encoding="utf-8").replace(
                official_checksum, fixture_checksum
            ),
            encoding="utf-8",
        )

        isolated_path = self.repo / "isolated-path"
        isolated_path.mkdir()
        for command in (
            "awk",
            "chmod",
            "cp",
            "git",
            "grep",
            "gzip",
            "mkdir",
            "mktemp",
            "mv",
            "rm",
            "shasum",
        ):
            os.symlink(shutil.which(command), isolated_path / command)
        self.write_executable(
            isolated_path / "uname",
            """#!/bin/sh
case "$1" in
  -s) printf 'Darwin\\n' ;;
  -m) printf 'x86_64\\n' ;;
esac
""",
        )
        self.write_executable(
            isolated_path / "curl",
            """#!/bin/sh
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o) output=$2; shift 2 ;;
    *) shift ;;
  esac
done
cp "$FAKE_RELEASE_ASSET" "$output"
""",
        )

        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_RELEASE_ASSET": str(release_asset),
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": str(isolated_path),
            }
        )

        result = subprocess.run(
            ["/bin/sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertEqual(0, result.returncode, result.stderr.decode())

    def test_install_refuses_an_existing_core_hooks_path_before_provisioning(self):
        subprocess.run(
            ["git", "config", "--local", "core.hooksPath", "custom-hooks"],
            cwd=self.repo,
            check=True,
        )
        sentinel = self.repo / "custom-hooks" / "pre-commit"
        sentinel.parent.mkdir()
        sentinel.write_text("existing hook\n", encoding="utf-8")
        provisioning_log = self.repo / "unexpected-provisioning.log"
        shim_directory = self.repo / "conflict-shims"
        for command in ("curl", "mise"):
            self.write_executable(
                shim_directory / command,
                f"#!/bin/sh\nprintf '%s\\n' {command} >> '{provisioning_log}'\nexit 93\n",
            )

        environment = os.environ.copy()
        environment.update(
            {
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"core.hooksPath", result.stderr)
        self.assertFalse(provisioning_log.exists())
        self.assertEqual("existing hook\n", sentinel.read_text(encoding="utf-8"))
        self.assertEqual(
            "custom-hooks",
            subprocess.run(
                ["git", "config", "--local", "--get", "core.hooksPath"],
                cwd=self.repo,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip(),
        )
        self.assertFalse(self.repo.joinpath(".git", "lefthook").exists())

    def test_install_refuses_global_core_hooks_path_without_mutating_it(self):
        global_config = self.repo / "global.gitconfig"
        subprocess.run(
            [
                "git",
                "config",
                "--file",
                str(global_config),
                "core.hooksPath",
                "custom-global-hooks",
            ],
            cwd=self.repo,
            check=True,
        )
        original_config = global_config.read_bytes()
        sentinel = self.repo / "custom-global-hooks" / "pre-commit"
        sentinel.parent.mkdir()
        sentinel.write_text("global hook\n", encoding="utf-8")
        provisioning_log = self.repo / "unexpected-global-provisioning.log"
        shim_directory = self.repo / "global-conflict-shims"
        for command in ("curl", "mise"):
            self.write_executable(
                shim_directory / command,
                f"#!/bin/sh\nprintf '%s\\n' {command} >> '{provisioning_log}'\nexit 92\n",
            )
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_CONFIG_GLOBAL": str(global_config),
                "GIT_CONFIG_SYSTEM": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"core.hooksPath", result.stderr)
        self.assertFalse(provisioning_log.exists())
        self.assertEqual(original_config, global_config.read_bytes())
        self.assertEqual("global hook\n", sentinel.read_text(encoding="utf-8"))
        self.assertFalse(self.repo.joinpath(".git", "lefthook").exists())

    def test_install_rejects_an_untrusted_exact_version_before_provisioning(self):
        self.repo.joinpath("lefthook.yml").write_text(
            'min_version: "9.9.9"\n', encoding="utf-8"
        )
        self.repo.joinpath("mise.toml").write_text(
            '[tools]\npython = "3.12"\n', encoding="utf-8"
        )
        subprocess.run(
            ["git", "add", "mise.toml"], cwd=self.repo, check=True
        )
        provisioning_log = self.repo / "untrusted-version-provisioning.log"
        shim_directory = self.repo / "untrusted-version-shims"
        for command in ("curl", "mise"):
            self.write_executable(
                shim_directory / command,
                f"#!/bin/sh\nprintf '%s\\n' {command} >> '{provisioning_log}'\nexit 94\n",
            )
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"trusted release manifest", result.stderr)
        self.assertFalse(provisioning_log.exists())
        self.assertFalse(self.repo.joinpath(".git", "lefthook").exists())

    def test_version_parser_rejects_noncanonical_or_ambiguous_values(self):
        invalid_configs = {
            "missing": "pre-commit:\n  jobs: []\n",
            "duplicate": (
                'min_version: "2.1.10"\nmin_version: "2.1.10"\n'
            ),
            "range": 'min_version: ">=2.1.10"\n',
            "environment expression": 'min_version: "${LEFTHOOK_VERSION}"\n',
            "inline comment": 'min_version: "2.1.10" # pin\n',
        }
        provisioning_log = self.repo / "invalid-version-provisioning.log"
        shim_directory = self.repo / "invalid-version-shims"
        for command in ("curl", "lefthook", "mise"):
            self.write_executable(
                shim_directory / command,
                f"#!/bin/sh\nprintf '%s\\n' {command} >> '{provisioning_log}'\nexit 95\n",
            )
        environment = os.environ.copy()
        environment["PATH"] = (
            f"{shim_directory}{os.pathsep}{environment['PATH']}"
        )

        for name, config in invalid_configs.items():
            with self.subTest(config=name):
                self.repo.joinpath("lefthook.yml").write_text(
                    config, encoding="utf-8"
                )

                result = subprocess.run(
                    ["sh", "./scripts/lefthook", "run", "pre-commit"],
                    cwd=self.repo,
                    env=environment,
                    capture_output=True,
                )

                self.assertNotEqual(0, result.returncode)
                self.assertIn(b"min_version", result.stderr)
                self.assertFalse(provisioning_log.exists())
                self.assertFalse(
                    self.repo.joinpath(".git", "lefthook").exists()
                )

    def test_runtime_missing_binary_fails_without_installing_or_using_path(self):
        old_binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.9"
            / "linux-x86_64"
            / "lefthook"
        )
        old_binary_log = self.repo / "old-binary.log"
        self.write_executable(
            old_binary,
            f"#!/bin/sh\nprintf called > '{old_binary_log}'\nexit 0\n",
        )
        unexpected_log = self.repo / "missing-binary-unexpected.log"
        shim_directory = self.repo / "missing-binary-shims"
        for command in ("curl", "lefthook", "mise"):
            self.write_executable(
                shim_directory / command,
                f"#!/bin/sh\nprintf '%s\\n' {command} >> '{unexpected_log}'\nexit 96\n",
            )
        environment = os.environ.copy()
        environment["PATH"] = (
            f"{shim_directory}{os.pathsep}{environment['PATH']}"
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "run", "pre-commit"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            b"run: sh ./scripts/lefthook install", result.stderr
        )
        self.assertFalse(old_binary_log.exists())
        self.assertFalse(unexpected_log.exists())

    def test_runtime_rejects_a_mismatched_cached_binary(self):
        installed_binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
            / "lefthook"
        )
        invocation_log = self.repo / "mismatched-binary-invocation.log"
        self.write_executable(
            installed_binary,
            """#!/bin/sh
if [ "${1-}" = version ]; then
  printf '9.9.9\\n'
  exit 0
fi
printf '%s\\n' "$*" > "$WRONG_BINARY_LOG"
exit 0
""",
        )
        environment = os.environ.copy()
        environment["WRONG_BINARY_LOG"] = str(invocation_log)

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "run", "pre-commit"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"cached Lefthook does not match 2.1.10", result.stderr)
        self.assertFalse(invocation_log.exists())

    def test_runtime_refuses_to_guess_between_multiple_main_configs(self):
        self.repo.joinpath("lefthook.yaml").write_text(
            'min_version: "2.1.10"\n', encoding="utf-8"
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "run", "pre-commit"],
            cwd=self.repo,
            capture_output=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"multiple Lefthook config", result.stderr)

    def test_direct_install_rejects_a_checksum_mismatch_without_residue(self):
        shim_directory = self.repo / "checksum-mismatch-shims"
        self.write_executable(
            shim_directory / "curl",
            """#!/bin/sh
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o) output=$2; shift 2 ;;
    *) shift ;;
  esac
done
printf 'corrupt release asset' > "$output"
""",
        )
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"checksum mismatch", result.stderr)
        self.assertFalse(self.repo.joinpath(".git", "lefthook").exists())

    def test_failed_mise_install_does_not_fall_back_to_download(self):
        self.repo.joinpath("mise.toml").write_text(
            '[tools]\npython = "3.12"\n', encoding="utf-8"
        )
        subprocess.run(
            ["git", "add", "mise.toml"], cwd=self.repo, check=True
        )
        mise_log = self.repo / "failed-mise.log"
        unexpected_download = self.repo / "mise-fallback-download.log"
        shim_directory = self.repo / "failed-mise-shims"
        self.write_executable(
            shim_directory / "mise",
            """#!/bin/sh
printf '%s\\n' "$*" >> "$FAKE_MISE_LOG"
if [ "$1" = -C ] && [ "${3-}" = help ] && [ "${4-}" = install-into ]; then
  exit 0
fi
exit 97
""",
        )
        self.write_executable(
            shim_directory / "curl",
            f"#!/bin/sh\nprintf download > '{unexpected_download}'\nexit 98\n",
        )
        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_MISE_LOG": str(mise_log),
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"mise could not install", result.stderr)
        self.assertFalse(unexpected_download.exists())
        self.assertFalse(self.repo.joinpath(".git", "lefthook").exists())

    def test_install_uses_the_shared_git_directory_from_a_linked_worktree(self):
        fake_lefthook_body = b"""#!/bin/sh
if [ "$1" = version ]; then
  printf '2.1.10\\n'
fi
exit 0
"""
        release_asset = self.repo / "worktree-release-asset.gz"
        release_asset.write_bytes(gzip.compress(fake_lefthook_body, mtime=0))
        fixture_checksum = hashlib.sha256(
            release_asset.read_bytes()
        ).hexdigest()
        self.runner.write_text(
            RUNNER_SOURCE.read_text(encoding="utf-8").replace(
                OFFICIAL_LINUX_X86_64_CHECKSUM, fixture_checksum
            ),
            encoding="utf-8",
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.invalid"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Lefthook Test"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "add", "lefthook.yml", "scripts/lefthook"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "--quiet", "-m", "fixture"],
            cwd=self.repo,
            check=True,
        )
        linked_worktree = Path(
            self.temporary_directory.name, "linked worktree"
        )
        subprocess.run(
            [
                "git",
                "worktree",
                "add",
                "--quiet",
                "-b",
                "linked-test",
                str(linked_worktree),
            ],
            cwd=self.repo,
            check=True,
        )

        shim_directory = self.repo / "worktree-shims"
        git_log = self.repo / "worktree-git.log"
        self.write_executable(
            shim_directory / "git",
            """#!/bin/sh
printf '%s\n' "$*" >> "$FAKE_GIT_LOG"
exec "$REAL_GIT" "$@"
""",
        )
        self.write_executable(
            shim_directory / "curl",
            """#!/bin/sh
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o) output=$2; shift 2 ;;
    *) shift ;;
  esac
done
cp "$FAKE_RELEASE_ASSET" "$output"
""",
        )
        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_RELEASE_ASSET": str(release_asset),
                "FAKE_GIT_LOG": str(git_log),
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
                "REAL_GIT": shutil.which("git"),
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=linked_worktree,
            env=environment,
            capture_output=True,
        )

        shared_binary = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
            / "lefthook"
        )
        self.assertEqual(0, result.returncode, result.stderr.decode())
        self.assertTrue(shared_binary.is_file())
        self.assertTrue(linked_worktree.joinpath(".git").is_file())
        self.assertIn(
            "rev-parse --path-format=absolute --git-common-dir",
            git_log.read_text(encoding="utf-8").splitlines(),
        )
        for worktree in (self.repo, linked_worktree):
            result = subprocess.run(
                ["sh", "./scripts/lefthook", "version"],
                cwd=worktree,
                env=environment,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr.decode())

    def test_failed_final_move_removes_the_staged_binary(self):
        fake_lefthook_body = b"""#!/bin/sh
if [ "$1" = version ]; then
  printf '2.1.10\\n'
fi
exit 0
"""
        release_asset = self.repo / "failed-move-release-asset.gz"
        release_asset.write_bytes(gzip.compress(fake_lefthook_body, mtime=0))
        fixture_checksum = hashlib.sha256(
            release_asset.read_bytes()
        ).hexdigest()
        self.runner.write_text(
            RUNNER_SOURCE.read_text(encoding="utf-8").replace(
                OFFICIAL_LINUX_X86_64_CHECKSUM, fixture_checksum
            ),
            encoding="utf-8",
        )
        shim_directory = self.repo / "failed-move-shims"
        self.write_executable(
            shim_directory / "curl",
            """#!/bin/sh
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o) output=$2; shift 2 ;;
    *) shift ;;
  esac
done
cp "$FAKE_RELEASE_ASSET" "$output"
""",
        )
        self.write_executable(shim_directory / "mv", "#!/bin/sh\nexit 99\n")
        environment = os.environ.copy()
        environment.update(
            {
                "FAKE_RELEASE_ASSET": str(release_asset),
                "GIT_CONFIG_GLOBAL": os.devnull,
                "PATH": f"{shim_directory}{os.pathsep}{environment['PATH']}",
            }
        )

        result = subprocess.run(
            ["sh", "./scripts/lefthook", "install"],
            cwd=self.repo,
            env=environment,
            capture_output=True,
        )

        install_directory = (
            self.repo
            / ".git"
            / "lefthook"
            / "2.1.10"
            / "linux-x86_64"
        )
        self.assertNotEqual(0, result.returncode)
        self.assertEqual([], list(install_directory.glob(".lefthook.*")))


if __name__ == "__main__":
    unittest.main()
