# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#

# Python built-in
import os
import platform


class ScopedEnvVar:
    """
    This class sets and restores an environment variable
    """

    def __init__(self, envVar: str, value: str, platforms: list[str]) -> None:
        """
        Constructs scoped environment variable class

        Args:
            envVar (str): The environment variable to set
            value (str): The value for the environment variable
            platforms (list[str]): A list of platforms from platform.system() where the env var will be set and restored ("Linux", "Windows")
        """
        self.platforms = platforms
        if platform.system() in self.platforms:
            self.envVar = envVar
            self.newValue = value
            self.prevValue = os.getenv(self.envVar)

    def __enter__(self):
        if platform.system() in self.platforms:
            os.environ[self.envVar] = self.newValue

    def __exit__(self, exc_type, exc_val, exc_tb):
        if platform.system() in self.platforms:
            if self.prevValue:
                os.environ[self.envVar] = self.prevValue
            else:
                del os.environ[self.envVar]
        pass
