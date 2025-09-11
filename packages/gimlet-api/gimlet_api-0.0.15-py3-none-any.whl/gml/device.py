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

from typing import List

import gml.proto.src.api.corepb.v1.cp_edge_pb2 as cpedgepb
import gml.proto.src.api.corepb.v1.device_info_pb2 as deviceinfopb


class DeviceCapabilities:
    def __init__(self, runtimes: List[str], cameras: List[str]):
        self.runtimes = runtimes
        self.cameras = cameras

    def to_proto(self) -> cpedgepb.DeviceCapabilities:
        return cpedgepb.DeviceCapabilities(
            model_runtimes=[
                deviceinfopb.ModelRuntimeInfo(
                    type=_runtime_str_to_runtime_protos(runtime)
                )
                for runtime in self.runtimes
            ],
            cameras=[
                deviceinfopb.CameraInfo(
                    driver=_camera_driver_str_to_camera_driver_protos(camera),
                    camera_id=str(idx),
                )
                for idx, camera in enumerate(self.cameras)
            ],
            camera_drivers=[
                deviceinfopb.CameraDriverInfo(
                    driver=_camera_driver_str_to_camera_driver_protos(camera)
                )
                for camera in self.cameras
            ],
        )


def _runtime_str_to_runtime_protos(
    runtime: str,
) -> deviceinfopb.ModelRuntimeType:
    match runtime.lower():
        case "tensorrt":
            return deviceinfopb.ModelRuntimeType.MODEL_RUNTIME_TYPE_TENSORRT
        case "openvino":
            return deviceinfopb.ModelRuntimeType.MODEL_RUNTIME_TYPE_OPENVINO
        case "habana":
            return deviceinfopb.ModelRuntimeType.MODEL_RUNTIME_TYPE_HABANA
        case _:
            raise ValueError("invalid runtime: {}".format(runtime))


def _camera_driver_str_to_camera_driver_protos(
    driver: str,
) -> deviceinfopb.CameraDriver:
    match driver.lower():
        case "argus":
            return deviceinfopb.CameraDriver.CAMERA_DRIVER_ARGUS
        case "v4l2":
            return deviceinfopb.CameraDriver.CAMERA_DRIVER_V4L2
        case _:
            raise ValueError("invalid driver: {}".format(driver))
