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

import abc
from typing import List, Optional

import yaml

import gml.proto.src.api.corepb.v1.model_exec_pb2 as modelexecpb
from gml.model import Model


class Pipeline:
    @abc.abstractmethod
    def to_yaml(self, models: List[Model], org_name: str) -> str:
        pass


class SingleModelPipeline(Pipeline):
    def to_yaml(self, models: List[Model], org_name: str) -> str:
        if len(models) != 1:
            raise ValueError(
                "{} only supports a single model".format(type(self).__qualname__)
            )
        return self._to_yaml(models[0].name, org_name)

    @abc.abstractmethod
    def _to_yaml(self, model_name: str, org_name: str) -> str:
        pass


class SimpleDetectionPipeline(SingleModelPipeline):
    def __init__(
        self,
        track_objects: Optional[bool] = None,
        add_tracking_id: Optional[bool] = None,
    ):
        self.track_objects = False
        if add_tracking_id is not None:
            import warnings

            warnings.warn(
                "The 'add_tracking_id' parameter is deprecated and will be removed in a future version.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.track_objects = add_tracking_id

        if track_objects is not None:
            self.track_objects = track_objects

        if track_objects is not None and add_tracking_id is not None:
            raise ValueError(
                "'track_objects' and 'add_tracking_id' cannot be set simultaneously."
            )

    def _to_yaml(self, model_name: str, org_name: str):
        # editorconfig-checker-disable
        video_stream_detections = ".detect.detections"
        track_node = ""
        if self.track_objects:
            track_node = """
- name: track
  kind: Track
  inputs:
    detections: .detect.detections
  outputs:
  - tracked_detections
"""
            video_stream_detections = ".track.tracked_detections"
        return f"""---
nodes:
- name: camera_source
  kind: CameraSource
  outputs:
  - frame
- name: detect
  kind: Detect
  attributes:
    model:
      model:
        name: {model_name}
        org: {org_name}
    frame_rate_limit: 30
  inputs:
    frame: .camera_source.frame
  outputs:
  - detections
{track_node}
- name: scale_video
  kind: ScaleVideo
  attributes:
    target_width: 640
    target_height: 480
    preserve_aspect_ratio: true
  inputs:
    frame: .camera_source.frame
  outputs:
  - scaled_frame
- name: video_stream_sink
  kind: EndpointSink
  attributes:
    response_output_info:
      - name: frame
        type: SEMANTIC_TYPE_VIDEO
      - name: detections
        type: SEMANTIC_TYPE_DETECTIONS
  inputs:
    frame: .scale_video.scaled_frame
    detections: {video_stream_detections}
"""


# editorconfig-checker-enable


class SimpleSegmentationPipeline(SingleModelPipeline):
    def _to_yaml(self, model_name: str, org_name: str):
        # editorconfig-checker-disable
        return f"""---
nodes:
- name: camera_source
  kind: CameraSource
  outputs:
  - frame
- name: segment
  kind: Segment
  attributes:
    model:
      model:
        name: {model_name}
        org: {org_name}
    frame_rate_limit: 30
  inputs:
    frame: .camera_source.frame
  outputs:
  - segmentation
- name: scale_video
  kind: ScaleVideo
  attributes:
    target_width: 640
    target_height: 480
    preserve_aspect_ratio: true
  inputs:
    frame: .camera_source.frame
  outputs:
  - scaled_frame
- name: video_stream_sink
  kind: EndpointSink
  attributes:
    response_output_info:
      - name: frame
        type: SEMANTIC_TYPE_VIDEO
      - name: segmentation
        type: SEMANTIC_TYPE_SEGMENTATION
  inputs:
    frame: .scale_video.scaled_frame
    segmentation: .segment.segmentation
"""


class SimpleDepthEstimationPipeline(SingleModelPipeline):
    def _to_yaml(self, model_name: str, org_name: str):
        # editorconfig-checker-disable
        return f"""---
nodes:
- name: camera_source
  kind: CameraSource
  outputs:
  - frame
- name: estimate_depth
  kind: EstimateDepth
  attributes:
    model:
      model:
        name: {model_name}
        org: {org_name}
    frame_rate_limit: 30
  inputs:
    frame: .camera_source.frame
  outputs:
  - depth
- name: scale_video
  kind: ScaleVideo
  attributes:
    target_width: 640
    target_height: 480
    preserve_aspect_ratio: true
  inputs:
    frame: .estimate_depth.depth
  outputs:
  - scaled_frame
- name: video_stream_sink
  kind: EndpointSink
  attributes:
    response_output_info:
      - name: frame
        type: SEMANTIC_TYPE_VIDEO
  inputs:
    frame: .scale_video.scaled_frame
"""


def escape_prompt(s: str) -> str:
    """Properly escape a string for YAML using the yaml library."""
    return yaml.dump(s, default_style='"').rstrip("\n")


class LiveChatPipeline(Pipeline):
    def __init__(
        self,
        system_prompt: str = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant<|eot_id|>",
        add_generation_prompt: bool = True,
        message_template_override: str = "",
    ):
        self.add_generation_prompt = add_generation_prompt
        self.message_template_override = message_template_override
        self.system_prompt = system_prompt

    def to_yaml(self, models: List[Model], org_name: str) -> str:
        if len(models) != 2:
            raise ValueError(
                "LiveChatPipeline expects two models (a tokenizer and a language model)"
            )
        tokenizer = None
        lm = None
        for m in models:
            if m.storage_format == modelexecpb.ModelInfo.MODEL_STORAGE_FORMAT_OPAQUE:
                tokenizer = m
            if m.generation_config is not None:
                lm = m
        if tokenizer is None or lm is None:
            raise ValueError(
                "LiveChatPipeline expects both a tokenizer model and a language model)"
            )
        message_template = None
        if self.message_template_override:
            message_template = self.message_template_override
        elif hasattr(tokenizer.tokenizer, "chat_template"):
            message_template = tokenizer.tokenizer.chat_template
        if message_template is None:
            raise ValueError(
                "Tokenizer model does not have a chat template defined. Please provide a message_template_override."
            )
        return f"""---
nodes:
- name: endpoint_source
  kind: EndpointSource
  attributes:
    request_input_info:
      - name: prompt
        type: SEMANTIC_TYPE_TEXT
  outputs:
  - prompt
- name: query_template
  kind: TemplateChatMessage
  attributes:
    add_generation_prompt: {self.add_generation_prompt}
    message_template: {escape_prompt(message_template)}
    preset_system_prompt: {escape_prompt(self.system_prompt)}
  inputs:
    query: .endpoint_source.prompt
  outputs:
  - chat_message
- name: tokenize
  kind: Tokenize
  attributes:
    tokenizer:
      model:
        name: {tokenizer.name}
        org: {org_name}
  inputs:
    text: .query_template.chat_message
  outputs:
  - tokens
- name: generate
  kind: GenerateTokens
  attributes:
    model:
      model:
        name: {lm.name}
        org: {org_name}
  inputs:
    prompt: .tokenize.tokens
  outputs:
  - generated_tokens
- name: detokenize
  kind: Detokenize
  attributes:
    tokenizer:
      model:
        name: {tokenizer.name}
        org: {org_name}
  inputs:
    tokens: .generate.generated_tokens
  outputs:
  - text
- name: endpoint_sink
  kind: EndpointSink
  attributes:
    response_output_info:
      - name: text_batch
        type: SEMANTIC_TYPE_TEXT
  inputs:
    text_batch: .detokenize.text
"""


class ZeroShotObjectDetectionPipeline(Pipeline):
    def __init__(self, conf_threshold=0.1):
        self.conf_threshold = conf_threshold

    def to_yaml(self, models: List[Model], org_name: str) -> str:
        if len(models) != 2:
            raise ValueError(
                "ZeroShotObjectDetectionPipeline expects two models (a detection model and a tokenizer)"
            )
        tokenizer = None
        detect = None
        for m in models:
            if m.storage_format == modelexecpb.ModelInfo.MODEL_STORAGE_FORMAT_OPAQUE:
                tokenizer = m
            else:
                detect = m
        if tokenizer is None or detect is None:
            raise ValueError(
                "ZeroShotObjectDetectionPipeline expects both a tokenizer model and a detection model)"
            )
        return f"""---
nodes:
- name: camera_source
  kind: CameraSource
  outputs:
  - frame
- name: endpoint_source
  kind: EndpointSource
  attributes:
    request_input_info:
      - name: prompt
        type: SEMANTIC_TYPE_TEXT
  outputs:
  - prompt
- name: detect
  kind: Detect
  attributes:
    model:
      model:
        name: {detect.name}
        org: {org_name}
    tokenizer:
      model:
        name: {tokenizer.name}
        org: {org_name}
    conf_threshold: {self.conf_threshold}
  inputs:
    frame: .camera_source.frame
    prompt: .endpoint_source.prompt
  outputs:
  - detections
- name: scale_video
  kind: ScaleVideo
  attributes:
    target_width: 640
    target_height: 480
    preserve_aspect_ratio: true
  inputs:
    frame: .camera_source.frame
  outputs:
  - scaled_frame
- name: video_stream_sink
  kind: EndpointSink
  attributes:
    response_output_info:
      - name: frame
        type: SEMANTIC_TYPE_VIDEO
      - name: detections
        type: SEMANTIC_TYPE_DETECTIONS
  inputs:
    frame: .scale_video.scaled_frame
    detections: .detect.detections
"""


# editorconfig-checker-enable
