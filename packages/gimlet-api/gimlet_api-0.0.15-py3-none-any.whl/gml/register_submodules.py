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


import copy

import torch


def _to_module_list(val):
    if isinstance(val, torch.nn.Module):
        return val

    converted = []
    for item in val:
        c = _to_module_container(item)
        if c is None:
            return None
        converted.append(c)
    if not converted:
        return None
    return torch.nn.ModuleList(converted)


def _to_module_dict(val):
    if isinstance(val, torch.nn.Module):
        return val

    converted = dict()
    for k, v in val.items():
        c = _to_module_container(v)
        if c is None:
            return None
        converted[k] = v
    if not converted:
        return None
    return torch.nn.ModuleDict(converted)


def _to_module_container(val, root=False):
    if isinstance(val, torch.nn.Module) and not root:
        # We deepcopy the module here because in some situations, torch export()
        # will overwrite the tensor values with FakeTensors due to a bug in a tracing step.
        #
        # This happens for models written in the following way:
        #
        # ```
        # self.layers = [module1, module2, module3]
        # for i, module in enumerate(self.layers):
        #     self.add_module(f"layer_{i}", module)
        # ```
        # such as here:
        # https://github.com/huggingface/transformers/blob/f51ac9e059a78049362803c1d606a2c6a8160ee4/src/transformers/models/maskformer/modeling_maskformer.py#L1142
        #
        # The _replace_containers_with_torch_containers function will replace the list
        # with a ModuleList, but the layers will point to the same Modules.
        #
        # During tracing, there is a reparameterization step where
        # 1. real tensors are replaced with FakeTensors,
        # 2. some tracing work is done, and then
        # 3. the FakeTensors get replaced with the original tensors.
        #
        # However, when you have a double-registered module like the above, the dictionary holding the original tensors
        # gets overwritten during the 1. real tensor -> FakeTensor conversion which means during the 3.
        # FakeTensor -> original_tensor replacement, FakeTensors are incorrectly returned, causing downstream errors
        # when trying to use FakeTensors as real tensors.
        #
        # Note that this entire codepath is not hit for many models because models tend to use the ModuleList/ModuleDict
        # pattern.
        return copy.deepcopy(val)
    if isinstance(val, dict):
        return _to_module_dict(val)
    if isinstance(val, list) or isinstance(val, tuple):
        return _to_module_list(val)

    return None


def _replace_containers_with_torch_containers(mod: torch.nn.Module):
    """Replaces any lists, dict, or nested combinations of lists/dicts that are attributes of `mod` with torch.nn.ModuleList/torch.nn.ModuleDict

    This fixes some `module is not installed as a submodule` errors.
    ."""
    _excludes = set(["_modules"])
    replacements = dict()
    for name, val in mod.__dict__.items():
        if name in _excludes:
            continue
        c = _to_module_container(val, root=True)
        if c is None:
            continue
        replacements[name] = c

    for name, repl in replacements.items():
        setattr(mod, name, repl)


def _ensure_submodules_accessed_through_getattr(mod: torch.nn.Module):
    """This removes any registered modules from `mod.__dict__`.

    This ensures that all accesses of submodules go through torch's __getattr__ infra,
    preventing certain cases of `module is not installed as a submodule` errors.
    """
    if not hasattr(mod, "_modules"):
        return
    for name in mod._modules:
        if name in mod.__dict__:
            del mod.__dict__[name]


def submodule_registration_workarounds(mod: torch.nn.Module):
    """Apply submodule registration workarounds recursively to all submodules of `mod`."""
    _ensure_submodules_accessed_through_getattr(mod)
    _replace_containers_with_torch_containers(mod)
    # We intentionally don't use `mod.modules()` (which returns all recursive submodules) here because we want only
    # the direct dependencies of `mod`. So that we get a pre-order traversal, ensuring the workarounds are applied
    # before we check for submodules.
    for submod in mod._modules.values():
        if submod is None or submod is mod:
            continue
        submodule_registration_workarounds(submod)
