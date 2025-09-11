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

import glob
import math
import tempfile
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, TextIO, Tuple

import torch
import transformers
from rich.progress import Console
from transformers import (
    BaseImageProcessor,
    Cache,
    DynamicCache,
    Pipeline,
    PreTrainedModel,
    PreTrainedTokenizer,
)

import gml.proto.src.api.corepb.v1.model_exec_pb2 as modelexecpb
from gml.asset_manager import AssetManager
from gml.model import GenerationConfig, Model, TorchModel
from gml.preprocessing import (
    ImagePreprocessingStep,
    ImageToFloatTensor,
    LetterboxImage,
    ResizeImage,
    StandardizeTensor,
)
from gml.tensor import (
    AttentionKeyValueCacheTensorSemantics,
    AttentionMaskDimension,
    BatchDimension,
    BoundingBoxFormat,
    DetectionNumCandidatesDimension,
    DetectionOutputDimension,
    DimensionSemantics,
    EmbeddingDimension,
    IgnoreDimension,
    ImageChannelDimension,
    ImageHeightDimension,
    ImageWidthDimension,
    PositionIDsDimension,
    SegmentationMaskChannel,
    TensorSemantics,
    TokensDimension,
    VocabLogitsDimension,
)

FALLBACK_RESIZE_SIZE = 512

# Set dynamic dimension max size to less than the int64 max, leaving leeway for the size to be ~4x by the model.
MAX_DYNAMIC_VAL = 2**61

console = Console()


class HuggingFaceTokenizer(Model):
    def __init__(self, tokenizer: PreTrainedTokenizer, name: Optional[str] = None):
        if name is None:
            name = tokenizer.name_or_path + ".tokenizer"
        super().__init__(
            name=name,
            kind=modelexecpb.ModelInfo.MODEL_KIND_HUGGINGFACE_TOKENIZER,
            storage_format=modelexecpb.ModelInfo.MODEL_STORAGE_FORMAT_OPAQUE,
            input_tensor_semantics=[],
            output_tensor_semantics=[],
        )
        self.tokenizer = tokenizer

    def _collect_assets(
        self, weight_manager: Optional[AssetManager] = None
    ) -> Dict[str, TextIO | BinaryIO | Path]:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.tokenizer.save_pretrained(tmpdir)
            paths = [Path(f) for f in glob.glob(tmpdir + "/*")]
            yield {p.name: p for p in paths}


class HuggingFaceGenerationConfig(GenerationConfig):
    def __init__(self, model: PreTrainedModel):
        config = model.generation_config
        eos_tokens = config.eos_token_id
        if eos_tokens is None:
            eos_tokens = []
        if not isinstance(eos_tokens, list):
            eos_tokens = [eos_tokens]
        super().__init__(eos_tokens)


def flatten(items):
    flattened = []
    if isinstance(items, torch.Tensor) or not isinstance(items, Iterable):
        flattened.append(items)
    else:
        for x in items:
            flattened.extend(flatten(x))
    return flattened


class WrapWithFunctionalCache(torch.nn.Module):
    def __init__(self, model: transformers.PreTrainedModel):
        super().__init__()
        self.model = model

    def forward(
        self,
        input_ids: torch.LongTensor,
        past_key_values: Cache,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
    ):
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            return_dict=True,
            use_cache=True,
        )

        return outputs.logits, outputs.past_key_values


class HuggingFaceTextGenerationPipeline:
    def __init__(
        self,
        pipeline: Pipeline,
        name: Optional[str] = None,
        tokenizer_name: Optional[str] = None,
        trace_w_attn_mask_and_pos_ids: bool = False,
        dynamic_batch: bool = False,
        export_predispatch: bool = False,
    ):
        self.pipeline = pipeline
        self.tokenizer_model = HuggingFaceTokenizer(pipeline.tokenizer, tokenizer_name)
        self._cache_length_for_tracing = 32
        if name is None:
            name = pipeline.model.name_or_path

        self.model = pipeline.model
        self.model = self.model.to(torch.float16)
        self.model = WrapWithFunctionalCache(pipeline.model)

        self.dynamic_batch = dynamic_batch
        self.batch_size = 1
        if self.dynamic_batch:
            # dynamic tracing fails for dimensions of size 1.
            self.batch_size = 2

        self.language_model = TorchModel(
            name,
            torch_module=self.model,
            export_predispatch=export_predispatch,
            **self._guess_model_spec(trace_w_attn_mask_and_pos_ids),
        )

    def _initialize_key_value_cache(self) -> DynamicCache:
        cache = []
        config = self.pipeline.model.config
        head_dim = (
            config.head_dim
            if hasattr(config, "head_dim")
            else config.hidden_size // config.num_attention_heads
        )
        num_key_value_heads = (
            config.num_attention_heads
            if config.num_key_value_heads is None
            else config.num_key_value_heads
        )
        cache_shape = (
            self.batch_size,
            num_key_value_heads,
            self._cache_length_for_tracing,
            head_dim,
        )
        for _ in range(config.num_hidden_layers):
            cache.append(
                [
                    torch.zeros(cache_shape).to(torch.float16),
                    torch.zeros(cache_shape).to(torch.float16),
                ]
            )
        return DynamicCache.from_legacy_cache(cache)

    def _parse_transformer_config(
        self, model: transformers.PreTrainedModel
    ) -> modelexecpb.TransformerConfig:
        # Only non-default rope config set the rope_scaling parameter
        attention_head_size = getattr(
            model.config,
            "attention_head_size",
            model.config.hidden_size // model.config.num_attention_heads,
        )
        partial_rotary_factor = getattr(model.config, "partial_rotary_factor", 1.0)
        rotary_embedding_dim = getattr(
            model.config,
            "rotary_dim",
            int(attention_head_size * partial_rotary_factor),
        )
        if (
            hasattr(model.config, "rope_scaling")
            and model.config.rope_scaling is not None
        ):
            rope_scaling = model.config.rope_scaling
            rope_type = rope_scaling.get("rope_type", rope_scaling.get("type", None))
            if not rope_type == "llama3":
                raise NotImplementedError(
                    "rope scaling type {} is not supported".format(rope_type)
                )
            # LLAMA 3 example config: https://huggingface.co/meta-llama/Llama-3.2-1B/blob/main/config.json
            llama3_config = modelexecpb.Llama3RopeConfig()
            llama3_config.theta = model.config.rope_theta
            llama3_config.rotary_embedding_dim = rotary_embedding_dim
            llama3_config.max_position_embeddings = model.config.max_position_embeddings

            llama3_config.factor = rope_scaling["factor"]
            llama3_config.high_freq_factor = rope_scaling["high_freq_factor"]
            llama3_config.low_freq_factor = rope_scaling["low_freq_factor"]
            llama3_config.original_max_position_embeddings = rope_scaling[
                "original_max_position_embeddings"
            ]
            return modelexecpb.TransformerConfig(
                position_embedding_config=modelexecpb.PositionEmbeddingConfig(
                    kind=modelexecpb.PositionEmbeddingKind.POSITION_EMBEDDING_KIND_ROPE_LLAMA3,
                    llama3_rope_config=llama3_config,
                ),
            )
        # Default rope configs:
        # 1. Llama-2: https://huggingface.co/NousResearch/Llama-2-7b-hf/blob/main/config.json
        # 2. Qwen2.5: https://huggingface.co/Qwen/Qwen2.5-14B-Instruct-1M/blob/main/config.json
        # 3. Mixtral: https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1/blob/main/config.json
        default_rope_config = modelexecpb.DefaultRopeConfig()
        default_rope_config.theta = model.config.rope_theta
        default_rope_config.max_position_embeddings = (
            model.config.max_position_embeddings
        )
        default_rope_config.rotary_embedding_dim = rotary_embedding_dim
        return modelexecpb.TransformerConfig(
            position_embedding_config=modelexecpb.PositionEmbeddingConfig(
                kind=modelexecpb.PositionEmbeddingKind.POSITION_EMBEDDING_KIND_ROPE_DEFAULT,
                default_rope_config=default_rope_config,
            ),
        )

    def _guess_model_spec(self, trace_w_attn_mask_and_pos_ids: bool) -> Dict:
        num_experts_per_tok = (
            1
            if not hasattr(self.pipeline.model.config, "num_experts_per_tok")
            else self.pipeline.model.config.num_experts_per_tok
        )

        input_dict = self.pipeline.preprocess("this is a prompt! Test test test?")
        if "input_ids" not in input_dict:
            raise ValueError(
                'HuggingFaceTextGenerationPipeline expects preprocessed inputs to have an "input_ids" tensor'
            )

        inputs = []
        input_tensor_semantics = []
        dynamic_shapes = []

        # Set range to half of seq_length to account for # of tokens per expert.
        # pytorch export creates a constraint on the number of possible tokens
        # sent to each expert. That value is num_experts * seq_length. If we don't divide
        # by number of experts, the tracing creates an integer value that exceeds the valid int64
        # range and will throw a hard to decipher error message.
        seq_length = torch.export.Dim(
            "seq_length", min=2, max=MAX_DYNAMIC_VAL // num_experts_per_tok
        )
        batch_shape = {0: torch.export.Dim("batch_size")} if self.dynamic_batch else {}

        # This currently assumes that all HF language models have inputs that are [B, NUM_TOKENS].
        inputs.append(
            torch.tile(input_dict["input_ids"].to(torch.int32), [self.batch_size, 1])
        )
        input_tensor_semantics.append(
            TensorSemantics(
                dimensions=[
                    BatchDimension(),
                    TokensDimension(),
                ],
            )
        )
        dynamic_shapes.append({1: seq_length} | batch_shape)

        cache_length = torch.export.Dim("cache_length", min=2, max=MAX_DYNAMIC_VAL)

        # Assume that the model supports a KeyValue cache.
        cache_values = self._initialize_key_value_cache()
        cache_shapes = []
        inputs.append(cache_values)
        for _ in range(len(cache_values)):
            input_tensor_semantics.append(AttentionKeyValueCacheTensorSemantics())
            input_tensor_semantics.append(AttentionKeyValueCacheTensorSemantics())
            cache_shapes.append(
                [{2: cache_length} | batch_shape, {2: cache_length} | batch_shape]
            )
        dynamic_shapes.append(cache_shapes)

        if trace_w_attn_mask_and_pos_ids:
            input_len = input_dict["input_ids"].shape[1]
            # Assume that the model supports a 4D attention mask.
            # This is typically an optional input and not specifying it means we treat it as a causal mask,
            # however in scenarios where we have padded inputs or KV caches, this may be explicitly set.
            inputs.append(
                torch.triu(
                    torch.ones(
                        (input_len, input_len + self._cache_length_for_tracing),
                        dtype=torch.float16,
                    )
                    * (-float("inf")),
                    diagonal=1,
                ).expand(self.batch_size, 1, -1, -1)
            )
            input_tensor_semantics.append(
                TensorSemantics(
                    dimensions=[
                        BatchDimension(),
                        IgnoreDimension(),
                        AttentionMaskDimension(),
                        AttentionMaskDimension(),
                    ],
                )
            )
            seq_and_cache_length = torch.export.Dim(
                "seq_and_cache_length",
                min=4,
                max=MAX_DYNAMIC_VAL + MAX_DYNAMIC_VAL // num_experts_per_tok,
            )
            dynamic_shapes.append(
                {2: seq_length, 3: seq_and_cache_length} | batch_shape
            )

            # Assume that the model supports position ids.
            inputs.append(
                torch.arange(
                    self._cache_length_for_tracing,
                    self._cache_length_for_tracing + input_len,
                    dtype=torch.int32,
                ).expand(self.batch_size, -1)
            )
            input_tensor_semantics.append(
                TensorSemantics(
                    dimensions=[BatchDimension(), PositionIDsDimension()],
                )
            )
            dynamic_shapes.append({1: seq_length} | batch_shape)

        # Since we wrap the model with WrapWithFunctionalCache, the outputs are well defined.
        output_tensor_semantics = [
            TensorSemantics(
                dimensions=[
                    BatchDimension(),
                    TokensDimension(),
                    VocabLogitsDimension(),
                ],
            ),
        ] + [
            AttentionKeyValueCacheTensorSemantics()
            for _ in range(len(cache_values) * 2)
        ]

        return {
            "example_inputs": inputs,
            "dynamic_shapes": dynamic_shapes,
            "input_tensor_semantics": input_tensor_semantics,
            "output_tensor_semantics": output_tensor_semantics,
            "generation_config": HuggingFaceGenerationConfig(self.pipeline.model),
            "transformer_config": self._parse_transformer_config(self.pipeline.model),
        }

    def models(self) -> List[Model]:
        return [self.tokenizer_model, self.language_model]


class HuggingFaceImageProcessor:
    def __init__(
        self,
        model: PreTrainedModel,
        processor: BaseImageProcessor,
        image_size_override: Optional[Tuple[int, int]] = None,
    ):
        self.model = model
        self.processor = processor
        self.image_size_override = image_size_override

    def input_spec(self) -> Dict[str, Any]:
        target_size = None
        image_preprocessing_steps = []
        has_do_resize = (
            hasattr(self.processor, "do_resize") and self.processor.do_resize
        )
        has_do_pad = hasattr(self.processor, "do_pad") and self.processor.do_pad
        # NOTE: it is possible for both do_resize and do_pad to be set, in which case we only use do_resize.
        if has_do_resize:
            target_size, preprocessing_step = self._convert_resize()
            image_preprocessing_steps.append(preprocessing_step)
        elif has_do_pad:
            target_size, preprocessing_step = self._convert_pad()
            image_preprocessing_steps.append(preprocessing_step)
        else:
            raise ValueError(
                "could not determine target size for resize from model config"
            )

        if (
            hasattr(self.processor, "do_rescale")
            and self.processor.do_rescale
            and hasattr(self.processor, "rescale_factor")
        ):
            image_preprocessing_steps.append(
                ImageToFloatTensor(
                    scale=True, scale_factor=self.processor.rescale_factor
                )
            )
        else:
            image_preprocessing_steps.append(ImageToFloatTensor(scale=False))

        if hasattr(self.processor, "do_normalize") and self.processor.do_normalize:
            image_preprocessing_steps.append(
                StandardizeTensor(self.processor.image_mean, self.processor.image_std)
            )

        channels_first = True
        if (
            hasattr(self.processor, "input_data_format")
            and self.processor.input_data_format == "channels_last"
        ):
            channels_first = False

        # Assume RGB for now.
        # TODO(james): figure out if this is specified anywhere in the huggingface pipeline.
        channel_format = "rgb"

        dimensions: list[DimensionSemantics] = [
            BatchDimension(),
        ]
        input_shape = [1]
        if channels_first:
            dimensions.append(ImageChannelDimension(channel_format))
            input_shape.append(3)
        dimensions.append(ImageHeightDimension())
        input_shape.append(target_size[0])
        dimensions.append(ImageWidthDimension())
        input_shape.append(target_size[1])
        if not channels_first:
            dimensions.append(ImageChannelDimension(channel_format))
            input_shape.append(3)

        example_input = torch.rand(input_shape)
        input_tensor_semantics = [TensorSemantics(dimensions)]
        return {
            "example_inputs": [example_input],
            "input_tensor_semantics": input_tensor_semantics,
            "image_preprocessing_steps": image_preprocessing_steps,
        }

    def output_spec_segmentation(self) -> Dict[str, Any]:
        if not hasattr(self.processor, "post_process_semantic_segmentation"):
            raise NotImplementedError(
                "only semantic segmentation is currently supported"
            )
        # TODO(philkuz): Support panoptic segmentation models. Multiple outputs come from panoptic segmentation models.
        # We need to decide whether we should invest in converting the panoptic segmentation output to semantic segmentation
        # format or if we should directly support panoptic segmentation output.
        if hasattr(self.processor, "post_process_panoptic_segmentation"):
            raise NotImplementedError(
                "panoptic segmentation models are not supported yet"
            )

        dimensions = [
            BatchDimension(),
            # TODO(james): verify all semantic segmentation in hugging face output a logits mask.
            SegmentationMaskChannel("logits_mask"),
            ImageHeightDimension(),
            ImageWidthDimension(),
        ]
        output_tensor_semantics = [
            TensorSemantics(dimensions),
        ]
        id_to_label = self.model.config.id2label
        max_id = max(id_to_label)
        labels = []
        for i in range(max_id):
            if i not in id_to_label:
                labels.append("")
                continue
            labels.append(id_to_label[i])
        return {
            "output_tensor_semantics": output_tensor_semantics,
            "class_labels": labels,
        }

    def output_spec_depth(self) -> Dict[str, Any]:
        dimensions = [
            BatchDimension(),
            ImageHeightDimension(),
            ImageWidthDimension(),
        ]
        output_tensor_semantics = [
            TensorSemantics(dimensions),
        ]
        return {
            "output_tensor_semantics": output_tensor_semantics,
        }

    def output_spec_object_detection(self, zero_shot=False) -> Dict[str, Any]:
        if not hasattr(self.processor, "post_process_object_detection"):
            raise NotImplementedError(
                "processor must have post_process_object_detection set"
            )

        if zero_shot:
            num_classes = -1
            labels = []
        else:
            id_to_label = self.model.config.id2label
            max_id = max(id_to_label)
            labels = []
            for i in range(max_id):
                if i not in id_to_label:
                    labels.append("")
                    continue
                labels.append(id_to_label[i])
            num_classes = max_id + 1

        # TODO(james): verify assumptions made here apply broadly.
        output_tensor_semantics = []
        # We assume that ObjectDetectionWrapper is used to ensure that logits are the first tensor and boxes are the second.
        logits_dimensions = [
            BatchDimension(),
            DetectionNumCandidatesDimension(is_nms=False),
            DetectionOutputDimension(
                scores_range=(0, num_classes),
                scores_are_logits=not zero_shot,
            ),
        ]
        output_tensor_semantics.append(TensorSemantics(logits_dimensions))

        box_dimensions = [
            BatchDimension(),
            DetectionNumCandidatesDimension(is_nms=False),
            DetectionOutputDimension(
                coordinates_start_index=0,
                box_format=BoundingBoxFormat("cxcywh", is_normalized=True),
            ),
        ]
        output_tensor_semantics.append(TensorSemantics(box_dimensions))
        return {
            "output_tensor_semantics": output_tensor_semantics,
            "class_labels": labels,
        }

    def _get_size(self) -> Dict[str, int]:
        size = None
        if self.image_size_override:
            size = {
                "height": self.image_size_override[0],
                "width": self.image_size_override[1],
            }
        elif hasattr(self.processor, "size") and self.processor.size is not None:
            size = self.processor.size
        elif (
            hasattr(self.model.config, "image_size")
            and self.model.config.image_size is not None
        ):
            size = {
                "height": self.model.config.image_size,
                "width": self.model.config.image_size,
            }
        else:
            warnings.warn(
                f"using fallback resize size of {FALLBACK_RESIZE_SIZE} for model",
                stacklevel=1,
            )
            size = {
                "width": FALLBACK_RESIZE_SIZE,
                "height": FALLBACK_RESIZE_SIZE,
            }
        return size

    def _convert_resize(self) -> Tuple[Tuple[int, int], ImagePreprocessingStep]:
        size = self._get_size()
        size_divisor: int | None = None
        if hasattr(self.processor, "size_divisor"):
            size_divisor = self.processor.size_divisor

        target_size = None
        preprocess_step = None

        if "height" in size and "width" in size:
            target_size = (size["height"], size["width"])
            preprocess_step = ResizeImage()
        elif (
            "shortest_edge" in size
            or "longest_edge" in size
            or "max_height" in size
            or "max_width" in size
        ):
            shortest_edge = size.get("shortest_edge")
            longest_edge = size.get("longest_edge")
            max_height = size.get("max_height")
            max_width = size.get("max_width")

            min_size = None
            for edge_size in [shortest_edge, longest_edge, max_height, max_width]:
                if not edge_size:
                    continue
                if not min_size or edge_size < min_size:
                    min_size = edge_size

            if min_size is None:
                raise ValueError(
                    "could not determine target size for resize from model config"
                )
            target_size = (min_size, min_size)
            preprocess_step = LetterboxImage()
        else:
            raise ValueError(
                "could not determine target size for resize from model config"
            )
        if size_divisor:
            target_size = (
                math.ceil(target_size[0] / size_divisor) * size_divisor,
                math.ceil(target_size[1] / size_divisor) * size_divisor,
            )
        return target_size, preprocess_step

    def _convert_pad(self) -> Tuple[Tuple[int, int], ImagePreprocessingStep]:
        # NOTE: There is a wide variety of ways that huggingface pads images.
        # We found at least 3 different ways to pad images in the codebase:
        # 1. Center pad (pad top,left, bottom, right) to match target size
        # https://github.com/huggingface/transformers/blob/70b07d97cf2c5f61fff55700b65528a1b6845cd2/src/transformers/models/dpt/image_processing_dpt.py#L231
        # 2. Right/Top pad (pad top, and right) to match target size
        # https://github.com/huggingface/transformers/blob/174890280b340b89c5bfa092f6b4fb0e2dc2d7fc/src/transformers/models/conditional_detr/image_processing_conditional_detr.py#L846
        # 3. Pad to nearest multiple of size_divisor
        # https://github.com/huggingface/transformers/blob/70b07d97cf2c5f61fff55700b65528a1b6845cd2/src/transformers/models/llava_onevision/image_processing_llava_onevision.py#L177-179
        #
        # We decided to simply implement padding with LetterBoxImage(),
        # because we assume the models won't be that sensitive to the type of padding,
        # but this may need to be revisited in the future.
        size = self._get_size()
        size_divisor: int | None = None
        if hasattr(self.processor, "size_divisor"):
            size_divisor = self.processor.size_divisor

        target_size = None
        preprocess_step = None
        if "height" in size and "width" in size:
            target_size = (size["height"], size["width"])
            preprocess_step = LetterboxImage()
        else:
            raise ValueError(
                "could not determine target size for resize from model config"
            )
        if size_divisor:
            target_size = (
                math.ceil(target_size[0] / size_divisor) * size_divisor,
                math.ceil(target_size[1] / size_divisor) * size_divisor,
            )
        return target_size, preprocess_step


class HuggingFaceImageSegmentationPipeline:
    def __init__(
        self,
        pipeline: Pipeline,
        name: Optional[str] = None,
        image_size_override: Optional[Tuple[int, int]] = None,
    ):
        self.pipeline = pipeline
        if name is None:
            name = pipeline.model.name_or_path

        self.image_size_override = image_size_override
        self.model = TorchModel(
            name,
            torch_module=self.pipeline.model,
            **self._guess_model_spec(),
        )

    def _guess_model_spec(self) -> Dict:
        if self.pipeline.image_processor is None:
            raise ValueError(
                "Could not determine image preprocessing for pipeline with image_processor=None"
            )
        if self.pipeline.tokenizer is not None:
            raise NotImplementedError(
                "HuggingFaceImageSegmentationPipeline does not yet support token inputs"
            )

        image_processor = HuggingFaceImageProcessor(
            self.pipeline.model,
            self.pipeline.image_processor,
            image_size_override=self.image_size_override,
        )
        spec = image_processor.input_spec()
        spec.update(image_processor.output_spec_segmentation())
        return spec

    def models(self) -> List[Model]:
        return [self.model]


class ObjectDetectionWrapper(torch.nn.Module):
    def __init__(self, model: PreTrainedModel):
        super().__init__()
        self.model = model

    def forward(self, *args, **kwargs):
        outputs = self.model(*args, **kwargs)
        return outputs.logits, outputs.pred_boxes


class HuggingFaceObjectDetectionPipeline:
    def __init__(
        self,
        pipeline: Pipeline,
        name: Optional[str] = None,
        image_size_override: Optional[Tuple[int, int]] = None,
    ):
        self.pipeline = pipeline
        if name is None:
            name = pipeline.model.name_or_path

        self.image_size_override = image_size_override
        self.model = TorchModel(
            name,
            torch_module=ObjectDetectionWrapper(self.pipeline.model),
            **self._guess_model_spec(),
        )

    def _guess_model_spec(self) -> Dict:
        if self.pipeline.image_processor is None:
            raise ValueError(
                "Could not determine image preprocessing for pipeline with image_processor=None"
            )
        if self.pipeline.tokenizer is not None:
            raise NotImplementedError(
                "HuggingFaceObjectDetectionPipeline does not yet support token inputs"
            )

        image_processor = HuggingFaceImageProcessor(
            self.pipeline.model,
            self.pipeline.image_processor,
            image_size_override=self.image_size_override,
        )
        spec = image_processor.input_spec()
        spec.update(image_processor.output_spec_object_detection())
        return spec

    def models(self) -> List[Model]:
        return [self.model]


class ZeroShotObjectDetectionWrapper(torch.nn.Module):
    def __init__(self, model: PreTrainedModel):
        super().__init__()
        self.model = model

    def forward(self, image, tokens, attention_mask):
        outputs = self.model(
            input_ids=tokens, pixel_values=image, attention_mask=attention_mask
        )
        return torch.sigmoid(outputs.logits), outputs.pred_boxes


class HuggingFaceZeroShotObjectDetectionPipeline:
    def __init__(
        self,
        pipeline: Pipeline,
        name: Optional[str] = None,
        tokenizer_name: Optional[str] = None,
        image_size_override: Optional[Tuple[int, int]] = None,
    ):
        self.pipeline = pipeline
        if name is None:
            name = pipeline.model.name_or_path

        self.tokenizer_model = HuggingFaceTokenizer(
            self.pipeline.tokenizer, tokenizer_name
        )

        self.image_size_override = image_size_override
        self.detection_model = TorchModel(
            name,
            torch_module=ZeroShotObjectDetectionWrapper(self.pipeline.model),
            **self._guess_model_spec(),
        )

    def _add_zero_shot_inputs(self, spec: Dict):
        example_inputs = spec["example_inputs"]
        if "dynamic_shapes" not in spec:
            spec["dynamic_shapes"] = [{} for _ in example_inputs]

        max_length = self.pipeline.model.config.text_config.max_length
        example_inputs.extend(
            [
                torch.randint(200, [2, max_length]).to(torch.int32),
                torch.ones([2, max_length]).to(torch.int32),
            ]
        )

        input_tensor_semantics = spec["input_tensor_semantics"]
        input_tensor_semantics.extend(
            [
                TensorSemantics(
                    [
                        BatchDimension(),
                        TokensDimension(),
                    ]
                ),
                TensorSemantics(
                    [
                        BatchDimension(),
                        AttentionMaskDimension(),
                    ]
                ),
            ]
        )

        spec["dynamic_shapes"].extend(
            [
                {0: torch.export.Dim("num_labels", max=MAX_DYNAMIC_VAL)},
                {0: torch.export.Dim("num_labels", max=MAX_DYNAMIC_VAL)},
            ]
        )

    def _guess_model_spec(self) -> Dict:
        if self.pipeline.image_processor is None:
            raise ValueError(
                "Could not determine image preprocessing for pipeline with image_processor=None"
            )

        image_processor = HuggingFaceImageProcessor(
            self.pipeline.model,
            self.pipeline.image_processor,
            image_size_override=self.image_size_override,
        )
        spec = image_processor.input_spec()
        self._add_zero_shot_inputs(spec)
        spec.update(image_processor.output_spec_object_detection(zero_shot=True))
        return spec

    def models(self) -> List[Model]:
        return [self.detection_model, self.tokenizer_model]


class HuggingFaceDepthEstimationPipeline:
    def __init__(
        self,
        pipeline: Pipeline,
        name: Optional[str] = None,
        image_size_override: Optional[Tuple[int, int]] = None,
    ):
        self.pipeline = pipeline
        if name is None:
            name = pipeline.model.name_or_path

        self.image_size_override = image_size_override

        self.model = TorchModel(
            name,
            torch_module=self.pipeline.model,
            **self._guess_model_spec(),
        )

    def _guess_model_spec(self) -> Dict:
        if self.pipeline.image_processor is None:
            raise ValueError(
                "Could not determine image preprocessing for pipeline with image_processor=None"
            )
        if self.pipeline.tokenizer is not None:
            raise NotImplementedError(
                "HuggingFaceDepthEstimationPipeline does not yet support token inputs"
            )

        image_processor = HuggingFaceImageProcessor(
            self.pipeline.model,
            self.pipeline.image_processor,
            image_size_override=self.image_size_override,
        )
        spec = image_processor.input_spec()
        spec.update(image_processor.output_spec_depth())
        return spec

    def models(self) -> List[Model]:
        return [self.model]


class HuggingFaceFeatureExtractionPipeline:
    def __init__(self, pipeline: Pipeline, name: Optional[str] = None):
        self.pipeline = pipeline
        if name is None:
            name = pipeline.model.name_or_path

        self.tokenizer_model = HuggingFaceTokenizer(self.pipeline.tokenizer)

        self.model = TorchModel(
            name=name,
            torch_module=self.pipeline.model,
            **self._guess_model_spec(),
        )

    def _guess_model_spec(self) -> Dict:
        spec = {
            "example_inputs": [],
            "input_tensor_semantics": [],
            "output_tensor_semantics": [],
            "dynamic_shapes": [],
        }

        input_dict = self.pipeline.preprocess("this is a prompt! Test test test?")
        if "input_ids" not in input_dict:
            raise ValueError(
                'HuggingFaceFeatureExtractionPipeline expects preprocessed inputs to have an "input_ids" tensor'
            )

        spec["example_inputs"].append(input_dict["input_ids"])
        spec["input_tensor_semantics"].extend(
            [
                TensorSemantics(
                    dimensions=[
                        BatchDimension(),
                        TokensDimension(),
                    ]
                ),
            ]
        )

        spec["output_tensor_semantics"].extend(
            [
                TensorSemantics(
                    dimensions=[
                        BatchDimension(),
                        TokensDimension(),
                        EmbeddingDimension(),
                    ],
                ),
                TensorSemantics(
                    dimensions=[
                        BatchDimension(),
                        EmbeddingDimension(),
                    ],
                ),
            ]
        )

        max_seqlen = (
            getattr(self.pipeline.model.config, "max_position_embeddings", 500) - 1
        )
        spec["dynamic_shapes"].extend(
            [
                {
                    1: torch.export.Dim(
                        "seqlen",
                        max=max_seqlen,
                    )
                },
            ]
        )
        return spec

    def models(self) -> List[Model]:
        return [self.model, self.tokenizer_model]


def import_huggingface_pipeline(pipeline: Pipeline, **kwargs) -> List[Model]:
    with console.status(
        f'Importing HuggingFace pipeline: "{pipeline.model.name_or_path}"'
    ):
        if pipeline.framework != "pt":
            raise ValueError(
                "unimplemented: hugging face pipeline framework: {}".format(
                    pipeline.framework
                )
            )

        if pipeline.task == "text-generation":
            result = HuggingFaceTextGenerationPipeline(pipeline, **kwargs).models()
        elif pipeline.task == "image-segmentation":
            result = HuggingFaceImageSegmentationPipeline(pipeline, **kwargs).models()
        elif pipeline.task == "object-detection":
            result = HuggingFaceObjectDetectionPipeline(pipeline, **kwargs).models()
        elif pipeline.task == "zero-shot-object-detection":
            result = HuggingFaceZeroShotObjectDetectionPipeline(
                pipeline, **kwargs
            ).models()
        elif pipeline.task == "depth-estimation":
            result = HuggingFaceDepthEstimationPipeline(pipeline, **kwargs).models()
        elif pipeline.task == "feature-extraction":
            result = HuggingFaceFeatureExtractionPipeline(pipeline, **kwargs).models()
        else:
            raise ValueError(
                "unimplemented: hugging face pipeline task: {} (supported tasks: [{}])".format(
                    pipeline.task,
                    [
                        "text-generation",
                        "image-segmentation",
                        "object-detection",
                        "zero-shot-object-detection",
                        "depth-estimation",
                        "feature-extraction",
                    ],
                )
            )
    console.print(f'Imported HuggingFace pipeline: "{pipeline.model.name_or_path}".')
    return result
