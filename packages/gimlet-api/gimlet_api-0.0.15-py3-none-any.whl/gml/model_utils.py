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


def prepare_ultralytics_yolo(model, example_inputs, num_iters=2):
    """Prepares an ultralytics YOLO model for export.

    Ultralytics YOLO models requires setting `export=True` on some of the torch modules for exporting to work properly.
    This function handles setting that value on the necessary modules.

    This also runs forward passes on the model to stabilize the exported weights.
    """
    if not hasattr(model, "model"):
        raise ValueError(
            "input to `prepare_ultralytics_yolo` is not a supported ultralytics yolo model"
        )
    if hasattr(model.model, "fuse") and callable(model.model.fuse):
        model.model.fuse()

    for _, m in model.named_modules():
        if hasattr(m, "export"):
            m.export = True
            # YOLOv8 requires setting `format` when `export = True`
            m.format = "custom"

    # Run a couple of forward passes as a warmup since the exported weights seem to change
    # after a forward run.
    # See https://github.com/ultralytics/yolov5/blob/2540fd4c1c2d9186126a71b3eb681d3a0a11861e/models/yolo.py#L118
    model.model.eval().to("cpu")
    for _ in range(num_iters):
        model.model(*example_inputs)
