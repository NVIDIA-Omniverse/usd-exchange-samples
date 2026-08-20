<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: MIT -->

# Agent Instructions

This file is intentionally limited to repository navigation and agent-specific guidance. Do not duplicate the canonical contributor documentation here.

## Read the canonical instructions first

- [README: build and run instructions](README.md#how-to-build-and-run-samples) covers setup and execution for both C++ and Python samples on Linux and Windows.
- [README: running all samples together](README.md#running-all-samples-together) explains the shared-stage workflow.
- [CONTRIBUTING: building](CONTRIBUTING.md#building), [testing](CONTRIBUTING.md#testing), and [adding a sample](CONTRIBUTING.md#adding-a-sample) define the project requirements and commands.
- [USD validation instructions](source/validateUsd/README.md) document the validator wrapper and its environment.

Before changing a sample, also read that sample's README, its C++ and Python implementations when present, and its tests.

## Agent-specific repository guidance

- This repository builds with CMake through `build.sh` or `build.bat`. Do not restore `premake5.lua` or use the obsolete `repo build` workflow. Repo Tools remain in use for dependency fetching, testing, formatting, and CI as described in the canonical docs.
- Treat `_build/`, `_install/`, `_repo/`, and other generated or fetched output as read-only. Change source files and build configuration instead.
- Preserve unrelated worktree changes and keep edits within the user's requested scope.
- Follow the paired C++/Python, test, README, and `allSamples.txt` requirements in CONTRIBUTING rather than restating them here.
- Do not commit, push, or modify external systems unless the user explicitly requests it.

## Sandbox, trust, and external dependencies

Outside-sandbox execution is host code execution. Request it only for the exact documented build, test, or validation command when:

1. A sandbox network restriction or the confirmed validation hang below blocks verification.
2. The user trusts the checked-out code. Never run external or otherwise untrusted contributions outside the sandbox; use disposable CI or report the verification as blocked.

Before requesting approval, inspect `git status` and relevant changes to executed code, test runners, dependency manifests, and package-index configuration. State the exact command, why escalation is required, and whether it may fetch dependencies.

Do not chain commands, run package managers directly, install system packages, modify host configuration, or substitute another test harness outside the sandbox. Prefer cached dependencies and documented reuse options. Do not request persistent approval for untrusted code. If approval is denied, report the command as blocked.

## Known Codex sandbox issue during validation

Some Codex Linux `workspace-write` sandboxes hang during shutdown after `asyncio.to_thread()`. This affects `validate_usd.sh` and validator-backed tests and is tracked by [openai/codex#7852](https://github.com/openai/codex/issues/7852).

Confirm it in the sandbox with:

```bash
timeout 5s python3 -u -c 'import asyncio; asyncio.run(asyncio.to_thread(print, "thread-ok"))'
echo $?
```

The defect is present when `thread-ok` prints and the exit status is `124`.

When confirmed:

1. Stop the hanging process.
2. Apply the trust requirements above.
3. Request one-time `sandbox_permissions: "require_escalated"` approval for only the exact validation or test command, citing the canary result.
4. Run no unrelated host-side commands.
5. Report both the canary and outside-sandbox results.

Do not change project code to accommodate this agent-environment defect.
