# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

import utils.shell


def assertValidatorCliSucceeds(testCase, stagePath):
    return_code, output = utils.shell.run_shell_script("validate_usd", stagePath)
    testCase.assertEqual(return_code, 0, output)
    for line in output.splitlines():
        if line.lower().startswith(("warning", "error", "fatal")):
            testCase.fail(msg=line)
