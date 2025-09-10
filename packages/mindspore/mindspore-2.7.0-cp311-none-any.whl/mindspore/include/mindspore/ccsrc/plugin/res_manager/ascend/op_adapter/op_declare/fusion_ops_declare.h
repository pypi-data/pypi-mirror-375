/**
 * Copyright 2023-2024 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MINDSPORE_CCSRC_TRANSFORM_GRAPH_IR_OP_DECLARE_FUSION_OPS_DECLARE_H_
#define MINDSPORE_CCSRC_TRANSFORM_GRAPH_IR_OP_DECLARE_FUSION_OPS_DECLARE_H_

#include "plugin/res_manager/ascend/op_adapter/op_declare/op_declare_macro.h"

// PromptFlashAttention
DECLARE_OP_ADAPTER(PromptFlashAttention)
DECLARE_OP_USE_OUTPUT(PromptFlashAttention)

// IncreFlashAttention
DECLARE_OP_ADAPTER(IncreFlashAttention)
DECLARE_OP_USE_OUTPUT(IncreFlashAttention)

DECLARE_OP_ADAPTER(FlashAttentionScore)
DECLARE_OP_USE_OUTPUT(FlashAttentionScore)

DECLARE_OP_ADAPTER(FlashAttentionScoreGrad)
DECLARE_OP_USE_OUTPUT(FlashAttentionScoreGrad)

// FusedInferAttentionScore
DECLARE_OP_ADAPTER(FusedInferAttentionScore)
DECLARE_OP_USE_DYN_INPUT(FusedInferAttentionScore)
DECLARE_OP_USE_OUTPUT(FusedInferAttentionScore)

DECLARE_OP_ADAPTER(MatmulReduceScatter)
DECLARE_OP_USE_OUTPUT(MatmulReduceScatter)

DECLARE_OP_ADAPTER(AllGatherMatmul)
DECLARE_OP_USE_OUTPUT(AllGatherMatmul)

// MoeGroupedMatmul
DECLARE_OP_ADAPTER(GroupedMatmul)
DECLARE_OP_USE_DYN_OUTPUT(GroupedMatmul)

// MoeInitRouting
DECLARE_OP_ADAPTER(MoeInitRouting)
DECLARE_OP_USE_INPUT_ATTR(MoeInitRouting)
DECLARE_OP_USE_OUTPUT(MoeInitRouting)

// MoeFinalizeRouting
DECLARE_OP_ADAPTER(MoeFinalizeRouting)
DECLARE_OP_USE_OUTPUT(MoeFinalizeRouting)

// MoeComputeExpertTokens
DECLARE_OP_ADAPTER(MoeComputeExpertTokens)
DECLARE_OP_USE_INPUT_ATTR(MoeComputeExpertTokens)
DECLARE_OP_USE_OUTPUT(MoeComputeExpertTokens)

DECLARE_OP_ADAPTER(GeGluV2)
DECLARE_OP_USE_OUTPUT(GeGluV2)

// MoeGatingTopKSoftmax
DECLARE_OP_ADAPTER(MoeGatingTopKSoftmax)
DECLARE_OP_USE_OUTPUT(MoeGatingTopKSoftmax)

#endif  // MINDSPORE_CCSRC_TRANSFORM_GRAPH_IR_OP_DECLARE_FUSION_OPS_DECLARE_H_
