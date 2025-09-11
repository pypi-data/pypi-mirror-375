# Copyright 2023- Gimlet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import functools
import importlib.metadata

from packaging import version


def _is_version_greater_or_equal(pkg: str, target_version: str) -> bool:
    """
    Check if the installed package version is greater than or equal to the specified version.
    Args:
        pkg (str): The package name to check, e.g., 'torch', 'transformers'.
        target_version (str): The version to compare against, in the format 'major.minor.patch'.
    Returns:
        bool: True if the installed package version is greater than or equal to `target_version`, False otherwise.
    """
    pkg_version_w_dev = importlib.metadata.version(pkg)
    # ignore dev suffixes.
    pkg_version = version.parse(version.parse(pkg_version_w_dev).base_version)
    return pkg_version >= version.parse(target_version)


is_torch_version_greater_or_equal = functools.partial(
    _is_version_greater_or_equal, "torch"
)
is_transformers_version_greater_or_equal = functools.partial(
    _is_version_greater_or_equal, "transformers"
)
