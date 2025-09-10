# Copyright 2023 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

from mindspore.ops._utils.arg_handler import *
from mindspore._c_expression import AdaptiveMaxPool2DPrim_
from mindspore._c_expression import ApplyRotaryPosEmbPrim_
from mindspore._c_expression import ArgMaxWithValuePrim_
from mindspore._c_expression import ArgMinWithValuePrim_
from mindspore._c_expression import BatchMatMulPrim_
from mindspore._c_expression import BatchNormGradExtPrim_
from mindspore._c_expression import BinaryCrossEntropyGradPrim_
from mindspore._c_expression import BinaryCrossEntropyPrim_
from mindspore._c_expression import BCEWithLogitsLossPrim_
from mindspore._c_expression import BroadcastToPrim_
from mindspore._c_expression import ConcatPrim_
from mindspore._c_expression import CrossPrim_
from mindspore._c_expression import CummaxPrim_
from mindspore._c_expression import DiagonalViewPrim_
from mindspore._c_expression import EluExtPrim_
from mindspore._c_expression import FFNExtPrim_
from mindspore._c_expression import FlashAttentionScoreGradPrim_
from mindspore._c_expression import FlashAttentionScorePrim_
from mindspore._c_expression import GluGradPrim_
from mindspore._c_expression import GLUPrim_
from mindspore._c_expression import GridSampler2DGradPrim_
from mindspore._c_expression import GridSampler2DPrim_
from mindspore._c_expression import GridSampler3DGradPrim_
from mindspore._c_expression import GridSampler3DPrim_
from mindspore._c_expression import HShrinkGradPrim_
from mindspore._c_expression import HShrinkPrim_
from mindspore._c_expression import IncreFlashAttentionPrim_
from mindspore._c_expression import IsClosePrim_
from mindspore._c_expression import LogSoftmaxGradPrim_
from mindspore._c_expression import LogSoftmaxPrim_
from mindspore._c_expression import MatMulPrim_
from mindspore._c_expression import MaxPoolGradWithIndicesPrim_
from mindspore._c_expression import MaxPoolGradWithMaskPrim_
from mindspore._c_expression import MaxPoolWithIndicesPrim_
from mindspore._c_expression import MaxPoolWithMaskPrim_
from mindspore._c_expression import MeshgridPrim_
from mindspore._c_expression import NanToNumPrim_
from mindspore._c_expression import NLLLossGradPrim_
from mindspore._c_expression import NLLLossPrim_
from mindspore._c_expression import OneHotExtPrim_
from mindspore._c_expression import PagedAttentionPrim_
from mindspore._c_expression import PromptFlashAttentionPrim_
from mindspore._c_expression import ReduceAllPrim_
from mindspore._c_expression import ReduceAnyPrim_
from mindspore._c_expression import ReduceMaxPrim_
from mindspore._c_expression import ReduceMinPrim_
from mindspore._c_expression import ReverseV2Prim_
from mindspore._c_expression import RmsNormPrim_
from mindspore._c_expression import RollPrim_
from mindspore._c_expression import SearchSortedPrim_
from mindspore._c_expression import SmoothL1LossGradPrim_
from mindspore._c_expression import SmoothL1LossPrim_
from mindspore._c_expression import SoftmaxPrim_
from mindspore._c_expression import SoftShrinkGradPrim_
from mindspore._c_expression import SoftShrinkPrim_
from mindspore._c_expression import SoftMarginLossGradPrim_
from mindspore._c_expression import SoftMarginLossPrim_
from mindspore._c_expression import SplitPrim_
from mindspore._c_expression import SqueezePrim_
from mindspore._c_expression import StackExtPrim_
from mindspore._c_expression import TriuPrim_
from mindspore._c_expression import UniqueConsecutivePrim_
from mindspore._c_expression import UpsampleTrilinear3DGradPrim_
from mindspore._c_expression import UpsampleTrilinear3DPrim_
from mindspore._c_expression import FusedInferAttentionScorePrim_
from mindspore._c_expression import GroupedMatmulPrim_
from mindspore._c_expression import QuantBatchMatmulPrim_
from mindspore._c_expression import WeightQuantBatchMatmulPrim_


class _PyboostAdaptiveMaxPool2DPrim(AdaptiveMaxPool2DPrim_):
    def __call__(self, input, output_size):

        return super().__call__([input, output_size])


adaptive_max_pool2d_impl = _PyboostAdaptiveMaxPool2DPrim()


class _PyboostApplyRotaryPosEmbPrim(ApplyRotaryPosEmbPrim_):
    def __call__(self, query, key, cos, sin, position_ids, cos_format):

        return super().__call__([query, key, cos, sin, position_ids, cos_format])


apply_rotary_pos_emb_impl = _PyboostApplyRotaryPosEmbPrim()


class _PyboostArgMaxWithValuePrim(ArgMaxWithValuePrim_):
    def __call__(self, input, axis, keep_dims):

        return super().__call__([input, axis, keep_dims])


argmax_with_value_impl = _PyboostArgMaxWithValuePrim()


class _PyboostArgMinWithValuePrim(ArgMinWithValuePrim_):
    def __call__(self, input, axis, keep_dims):

        return super().__call__([input, axis, keep_dims])


argmin_with_value_impl = _PyboostArgMinWithValuePrim()


class _PyboostBatchMatMulPrim(BatchMatMulPrim_):
    def __call__(self, x, y, transpose_a, transpose_b):

        return super().__call__([x, y, transpose_a, transpose_b])


batch_mat_mul_impl = _PyboostBatchMatMulPrim()


class _PyboostBatchNormGradExtPrim(BatchNormGradExtPrim_):
    def __call__(self, dout, input, weight, running_mean, running_var, saved_mean, saved_rstd, training, eps, output_mask):

        return super().__call__([dout, input, weight, running_mean, running_var, saved_mean, saved_rstd, training, eps, output_mask])


batch_norm_grad_ext_impl = _PyboostBatchNormGradExtPrim()


class _PyboostBinaryCrossEntropyGradPrim(BinaryCrossEntropyGradPrim_):
    def __call__(self, input, target, grad_output, weight, reduction):
        converted_reduction = str_to_enum('binary_cross_entropy_grad', 'reduction', reduction)
        return super().__call__([input, target, grad_output, weight, converted_reduction])


binary_cross_entropy_grad_impl = _PyboostBinaryCrossEntropyGradPrim()


class _PyboostBinaryCrossEntropyPrim(BinaryCrossEntropyPrim_):
    def __call__(self, input, target, weight, reduction):
        converted_reduction = str_to_enum('binary_cross_entropy', 'reduction', reduction)
        return super().__call__([input, target, weight, converted_reduction])


binary_cross_entropy_impl = _PyboostBinaryCrossEntropyPrim()


class _PyboostBCEWithLogitsLossPrim(BCEWithLogitsLossPrim_):
    def __call__(self, input, target, weight, posWeight, reduction):
        converted_reduction = str_to_enum('binary_cross_entropy_with_logits', 'reduction', reduction)
        return super().__call__([input, target, weight, posWeight, converted_reduction])


binary_cross_entropy_with_logits_impl = _PyboostBCEWithLogitsLossPrim()


class _PyboostBroadcastToPrim(BroadcastToPrim_):
    def __call__(self, input, shape):

        return super().__call__([input, shape])


broadcast_to_impl = _PyboostBroadcastToPrim()


class _PyboostConcatPrim(ConcatPrim_):
    def __call__(self, tensors, axis):

        return super().__call__([tensors, axis])


concat_impl = _PyboostConcatPrim()


class _PyboostCrossPrim(CrossPrim_):
    def __call__(self, input, other, dim):

        return super().__call__([input, other, dim])


cross_impl = _PyboostCrossPrim()


class _PyboostCummaxPrim(CummaxPrim_):
    def __call__(self, input, axis):

        return super().__call__([input, axis])


cummax_impl = _PyboostCummaxPrim()


class _PyboostDiagonalViewPrim(DiagonalViewPrim_):
    def __call__(self, input, offset, dim1, dim2):

        return super().__call__([input, offset, dim1, dim2])


diagonal_view_impl = _PyboostDiagonalViewPrim()


class _PyboostEluExtPrim(EluExtPrim_):
    def __call__(self, input, alpha):

        return super().__call__([input, alpha])


elu_ext_impl = _PyboostEluExtPrim()


class _PyboostFFNExtPrim(FFNExtPrim_):
    def __call__(self, x, weight1, weight2, expertTokens, bias1, bias2, scale, offset, deqScale1, deqScale2, antiquant_scale1, antiquant_scale2, antiquant_offset1, antiquant_offset2, activation, inner_precise):
        converted_activation = str_to_enum('ffn_ext', 'activation', activation)
        return super().__call__([x, weight1, weight2, expertTokens, bias1, bias2, scale, offset, deqScale1, deqScale2, antiquant_scale1, antiquant_scale2, antiquant_offset1, antiquant_offset2, converted_activation, inner_precise])


ffn_ext_impl = _PyboostFFNExtPrim()


class _PyboostFlashAttentionScoreGradPrim(FlashAttentionScoreGradPrim_):
    def __call__(self, query, key, value, dy, pse_shift, drop_mask, padding_mask, atten_mask, softmax_max, softmax_sum, softmax_in, attention_in, prefix, actual_seq_qlen, actual_seq_kvlen, head_num, keep_prob, scale_value, pre_tokens, next_tokens, inner_precise, input_layout, sparse_mode):
        converted_input_layout = str_to_enum('flash_attention_score_grad', 'input_layout', input_layout)
        return super().__call__([query, key, value, dy, pse_shift, drop_mask, padding_mask, atten_mask, softmax_max, softmax_sum, softmax_in, attention_in, prefix, actual_seq_qlen, actual_seq_kvlen, head_num, keep_prob, scale_value, pre_tokens, next_tokens, inner_precise, converted_input_layout, sparse_mode])


flash_attention_score_grad_impl = _PyboostFlashAttentionScoreGradPrim()


class _PyboostFlashAttentionScorePrim(FlashAttentionScorePrim_):
    def __call__(self, query, key, value, real_shift, drop_mask, padding_mask, attn_mask, prefix, actual_seq_qlen, actual_seq_kvlen, head_num, keep_prob, scale_value, pre_tokens, next_tokens, inner_precise, input_layout, sparse_mode):
        converted_input_layout = str_to_enum('flash_attention_score', 'input_layout', input_layout)
        return super().__call__([query, key, value, real_shift, drop_mask, padding_mask, attn_mask, prefix, actual_seq_qlen, actual_seq_kvlen, head_num, keep_prob, scale_value, pre_tokens, next_tokens, inner_precise, converted_input_layout, sparse_mode])


flash_attention_score_impl = _PyboostFlashAttentionScorePrim()


class _PyboostGluGradPrim(GluGradPrim_):
    def __call__(self, grads, x, axis):

        return super().__call__([grads, x, axis])


glu_grad_impl = _PyboostGluGradPrim()


class _PyboostGLUPrim(GLUPrim_):
    def __call__(self, x, axis):

        return super().__call__([x, axis])


glu_impl = _PyboostGLUPrim()


class _PyboostGridSampler2DGradPrim(GridSampler2DGradPrim_):
    def __call__(self, grad, input_x, grid, interpolation_mode, padding_mode, align_corners, output_mask):
        converted_interpolation_mode = str_to_enum('grid_sampler_2d_grad', 'interpolation_mode', interpolation_mode)
        converted_padding_mode = str_to_enum('grid_sampler_2d_grad', 'padding_mode', padding_mode)
        return super().__call__([grad, input_x, grid, converted_interpolation_mode, converted_padding_mode, align_corners, output_mask])


grid_sampler_2d_grad_impl = _PyboostGridSampler2DGradPrim()


class _PyboostGridSampler2DPrim(GridSampler2DPrim_):
    def __call__(self, input_x, grid, interpolation_mode, padding_mode, align_corners):
        converted_interpolation_mode = str_to_enum('grid_sampler_2d', 'interpolation_mode', interpolation_mode)
        converted_padding_mode = str_to_enum('grid_sampler_2d', 'padding_mode', padding_mode)
        return super().__call__([input_x, grid, converted_interpolation_mode, converted_padding_mode, align_corners])


grid_sampler_2d_impl = _PyboostGridSampler2DPrim()


class _PyboostGridSampler3DGradPrim(GridSampler3DGradPrim_):
    def __call__(self, grad, input_x, grid, interpolation_mode, padding_mode, align_corners, output_mask):
        converted_interpolation_mode = str_to_enum('grid_sampler_3d_grad', 'interpolation_mode', interpolation_mode)
        converted_padding_mode = str_to_enum('grid_sampler_3d_grad', 'padding_mode', padding_mode)
        return super().__call__([grad, input_x, grid, converted_interpolation_mode, converted_padding_mode, align_corners, output_mask])


grid_sampler_3d_grad_impl = _PyboostGridSampler3DGradPrim()


class _PyboostGridSampler3DPrim(GridSampler3DPrim_):
    def __call__(self, input_x, grid, interpolation_mode, padding_mode, align_corners):
        converted_interpolation_mode = str_to_enum('grid_sampler_3d', 'interpolation_mode', interpolation_mode)
        converted_padding_mode = str_to_enum('grid_sampler_3d', 'padding_mode', padding_mode)
        return super().__call__([input_x, grid, converted_interpolation_mode, converted_padding_mode, align_corners])


grid_sampler_3d_impl = _PyboostGridSampler3DPrim()


class _PyboostHShrinkGradPrim(HShrinkGradPrim_):
    def __call__(self, gradients, features, lambd):

        return super().__call__([gradients, features, lambd])


hshrink_grad_impl = _PyboostHShrinkGradPrim()


class _PyboostHShrinkPrim(HShrinkPrim_):
    def __call__(self, input, lambd):

        return super().__call__([input, lambd])


hshrink_impl = _PyboostHShrinkPrim()


class _PyboostIncreFlashAttentionPrim(IncreFlashAttentionPrim_):
    def __call__(self, query, key, value, attn_mask, actual_seq_lengths, pse_shift, dequant_scale1, quant_scale1, dequant_scale2, quant_scale2, quant_offset2, antiquant_scale, antiquant_offset, block_table, kv_padding_size, num_heads, input_layout, scale_value, num_key_value_heads, block_size, inner_precise):
        converted_input_layout = str_to_enum('incre_flash_attention', 'input_layout', input_layout)
        return super().__call__([query, key, value, attn_mask, actual_seq_lengths, pse_shift, dequant_scale1, quant_scale1, dequant_scale2, quant_scale2, quant_offset2, antiquant_scale, antiquant_offset, block_table, kv_padding_size, num_heads, converted_input_layout, scale_value, num_key_value_heads, block_size, inner_precise])


incre_flash_attention_impl = _PyboostIncreFlashAttentionPrim()


class _PyboostIsClosePrim(IsClosePrim_):
    def __call__(self, input, other, rtol, atol, equal_nan):

        return super().__call__([input, other, rtol, atol, equal_nan])


isclose_impl = _PyboostIsClosePrim()


class _PyboostLogSoftmaxGradPrim(LogSoftmaxGradPrim_):
    def __call__(self, logits, grad, axis):

        return super().__call__([logits, grad, axis])


log_softmax_grad_impl = _PyboostLogSoftmaxGradPrim()


class _PyboostLogSoftmaxPrim(LogSoftmaxPrim_):
    def __call__(self, logits, axis):

        return super().__call__([logits, axis])


log_softmax_impl = _PyboostLogSoftmaxPrim()


class _PyboostMatMulPrim(MatMulPrim_):
    def __call__(self, input, mat2, transpose_a, transpose_b):

        return super().__call__([input, mat2, transpose_a, transpose_b])


matmul_impl = _PyboostMatMulPrim()


class _PyboostMaxPoolGradWithIndicesPrim(MaxPoolGradWithIndicesPrim_):
    def __call__(self, x, grad, argmax, kernel_size, strides, pads, dilation, ceil_mode, argmax_type):
        converted_kernel_size = to_kernel_size('max_pool_grad_with_indices', 'kernel_size', kernel_size)
        converted_strides = to_strides('max_pool_grad_with_indices', 'strides', strides)
        converted_pads = to_output_padding('max_pool_grad_with_indices', 'pads', pads)
        converted_dilation = to_dilations('max_pool_grad_with_indices', 'dilation', dilation)
        return super().__call__([x, grad, argmax, converted_kernel_size, converted_strides, converted_pads, converted_dilation, ceil_mode, argmax_type])


max_pool_grad_with_indices_impl = _PyboostMaxPoolGradWithIndicesPrim()


class _PyboostMaxPoolGradWithMaskPrim(MaxPoolGradWithMaskPrim_):
    def __call__(self, x, grad, mask, kernel_size, strides, pads, dilation, ceil_mode, argmax_type):
        converted_kernel_size = to_kernel_size('max_pool_grad_with_mask', 'kernel_size', kernel_size)
        converted_strides = to_strides('max_pool_grad_with_mask', 'strides', strides)
        converted_pads = to_output_padding('max_pool_grad_with_mask', 'pads', pads)
        converted_dilation = to_dilations('max_pool_grad_with_mask', 'dilation', dilation)
        return super().__call__([x, grad, mask, converted_kernel_size, converted_strides, converted_pads, converted_dilation, ceil_mode, argmax_type])


max_pool_grad_with_mask_impl = _PyboostMaxPoolGradWithMaskPrim()


class _PyboostMaxPoolWithIndicesPrim(MaxPoolWithIndicesPrim_):
    def __call__(self, x, kernel_size, strides, pads, dilation, ceil_mode, argmax_type):
        converted_kernel_size = to_kernel_size('max_pool_with_indices', 'kernel_size', kernel_size)
        converted_strides = to_strides('max_pool_with_indices', 'strides', strides)
        converted_pads = to_output_padding('max_pool_with_indices', 'pads', pads)
        converted_dilation = to_dilations('max_pool_with_indices', 'dilation', dilation)
        return super().__call__([x, converted_kernel_size, converted_strides, converted_pads, converted_dilation, ceil_mode, argmax_type])


max_pool_with_indices_impl = _PyboostMaxPoolWithIndicesPrim()


class _PyboostMaxPoolWithMaskPrim(MaxPoolWithMaskPrim_):
    def __call__(self, x, kernel_size, strides, pads, dilation, ceil_mode, argmax_type):
        converted_kernel_size = to_kernel_size('max_pool_with_mask', 'kernel_size', kernel_size)
        converted_strides = to_strides('max_pool_with_mask', 'strides', strides)
        converted_pads = to_output_padding('max_pool_with_mask', 'pads', pads)
        converted_dilation = to_dilations('max_pool_with_mask', 'dilation', dilation)
        return super().__call__([x, converted_kernel_size, converted_strides, converted_pads, converted_dilation, ceil_mode, argmax_type])


max_pool_with_mask_impl = _PyboostMaxPoolWithMaskPrim()


class _PyboostMeshgridPrim(MeshgridPrim_):
    def __call__(self, inputs, indexing):
        converted_indexing = str_to_enum('meshgrid', 'indexing', indexing)
        return super().__call__([inputs, converted_indexing])


meshgrid_impl = _PyboostMeshgridPrim()


class _PyboostNanToNumPrim(NanToNumPrim_):
    def __call__(self, input, nan, posinf, neginf):

        return super().__call__([input, nan, posinf, neginf])


nan_to_num_impl = _PyboostNanToNumPrim()


class _PyboostNLLLossGradPrim(NLLLossGradPrim_):
    def __call__(self, logits, loss_grad, labels, weight, total_weight, reduction, ignore_index):
        converted_reduction = str_to_enum('nllloss_grad', 'reduction', reduction)
        return super().__call__([logits, loss_grad, labels, weight, total_weight, converted_reduction, ignore_index])


nllloss_grad_impl = _PyboostNLLLossGradPrim()


class _PyboostNLLLossPrim(NLLLossPrim_):
    def __call__(self, logits, labels, weight, reduction, ignore_index):
        converted_reduction = str_to_enum('nllloss', 'reduction', reduction)
        return super().__call__([logits, labels, weight, converted_reduction, ignore_index])


nllloss_impl = _PyboostNLLLossPrim()


class _PyboostOneHotExtPrim(OneHotExtPrim_):
    def __call__(self, tensor, num_classes, on_value, off_value, axis):

        return super().__call__([tensor, num_classes, on_value, off_value, axis])


one_hot_ext_impl = _PyboostOneHotExtPrim()


class _PyboostPagedAttentionPrim(PagedAttentionPrim_):
    def __call__(self, query, key_cache, value_cache, block_tables, context_lens, antiquant_scale, antiquant_offset, attn_mask, q_seq_lens, alibi_mask, head_num, scale_value, kv_head_num, kv_cache_quant_mode, mask_mode, mla_v_dim):
        converted_kv_cache_quant_mode = str_to_enum('paged_attention', 'kv_cache_quant_mode', kv_cache_quant_mode)
        converted_mask_mode = str_to_enum('paged_attention', 'mask_mode', mask_mode)
        return super().__call__([query, key_cache, value_cache, block_tables, context_lens, antiquant_scale, antiquant_offset, attn_mask, q_seq_lens, alibi_mask, head_num, scale_value, kv_head_num, converted_kv_cache_quant_mode, converted_mask_mode, mla_v_dim])


paged_attention_impl = _PyboostPagedAttentionPrim()


class _PyboostPromptFlashAttentionPrim(PromptFlashAttentionPrim_):
    def __call__(self, query, key, value, attn_mask, actual_seq_lengths, actual_seq_lengths_kv, pse_shift, deq_scale1, quant_scale1, deq_scale2, quant_scale2, quant_offset2, num_heads, scale_value, pre_tokens, next_tokens, input_layout, num_key_value_heads, sparse_mode, inner_precise):
        converted_input_layout = str_to_enum('prompt_flash_attention', 'input_layout', input_layout)
        return super().__call__([query, key, value, attn_mask, actual_seq_lengths, actual_seq_lengths_kv, pse_shift, deq_scale1, quant_scale1, deq_scale2, quant_scale2, quant_offset2, num_heads, scale_value, pre_tokens, next_tokens, converted_input_layout, num_key_value_heads, sparse_mode, inner_precise])


prompt_flash_attention_impl = _PyboostPromptFlashAttentionPrim()


class _PyboostReduceAllPrim(ReduceAllPrim_):
    def __call__(self, input, axis, keep_dims):

        return super().__call__([input, axis, keep_dims])


reduce_all_impl = _PyboostReduceAllPrim()


class _PyboostReduceAnyPrim(ReduceAnyPrim_):
    def __call__(self, x, axis, keep_dims):

        return super().__call__([x, axis, keep_dims])


reduce_any_impl = _PyboostReduceAnyPrim()


class _PyboostReduceMaxPrim(ReduceMaxPrim_):
    def __call__(self, x, axis, keep_dims):

        return super().__call__([x, axis, keep_dims])


reduce_max_impl = _PyboostReduceMaxPrim()


class _PyboostReduceMinPrim(ReduceMinPrim_):
    def __call__(self, x, axis, keep_dims):

        return super().__call__([x, axis, keep_dims])


reduce_min_impl = _PyboostReduceMinPrim()


class _PyboostReverseV2Prim(ReverseV2Prim_):
    def __call__(self, input, axis):

        return super().__call__([input, axis])


reverse_v2_impl = _PyboostReverseV2Prim()


class _PyboostRmsNormPrim(RmsNormPrim_):
    def __call__(self, x, gamma, epsilon):

        return super().__call__([x, gamma, epsilon])


rms_norm_impl = _PyboostRmsNormPrim()


class _PyboostRollPrim(RollPrim_):
    def __call__(self, input, shifts, dims):

        return super().__call__([input, shifts, dims])


roll_impl = _PyboostRollPrim()


class _PyboostSearchSortedPrim(SearchSortedPrim_):
    def __call__(self, sorted_sequence, values, sorter, dtype, right):

        return super().__call__([sorted_sequence, values, sorter, dtype, right])


searchsorted_impl = _PyboostSearchSortedPrim()


class _PyboostSmoothL1LossGradPrim(SmoothL1LossGradPrim_):
    def __call__(self, prediction, target, dout, beta, reduction):
        converted_reduction = str_to_enum('smooth_l1_loss_grad', 'reduction', reduction)
        return super().__call__([prediction, target, dout, beta, converted_reduction])


smooth_l1_loss_grad_impl = _PyboostSmoothL1LossGradPrim()


class _PyboostSmoothL1LossPrim(SmoothL1LossPrim_):
    def __call__(self, prediction, target, beta, reduction):
        converted_reduction = str_to_enum('smooth_l1_loss', 'reduction', reduction)
        return super().__call__([prediction, target, beta, converted_reduction])


smooth_l1_loss_impl = _PyboostSmoothL1LossPrim()


class _PyboostSoftmaxPrim(SoftmaxPrim_):
    def __call__(self, input, axis):

        return super().__call__([input, axis])


softmax_impl = _PyboostSoftmaxPrim()


class _PyboostSoftShrinkGradPrim(SoftShrinkGradPrim_):
    def __call__(self, input_grad, input_x, lambd):

        return super().__call__([input_grad, input_x, lambd])


softshrink_grad_impl = _PyboostSoftShrinkGradPrim()


class _PyboostSoftShrinkPrim(SoftShrinkPrim_):
    def __call__(self, input, lambd):

        return super().__call__([input, lambd])


softshrink_impl = _PyboostSoftShrinkPrim()


class _PyboostSoftMarginLossGradPrim(SoftMarginLossGradPrim_):
    def __call__(self, predict, label, dout, reduction):
        converted_reduction = str_to_enum('soft_margin_loss_grad', 'reduction', reduction)
        return super().__call__([predict, label, dout, converted_reduction])


soft_margin_loss_grad_impl = _PyboostSoftMarginLossGradPrim()


class _PyboostSoftMarginLossPrim(SoftMarginLossPrim_):
    def __call__(self, input, target, reduction):
        converted_reduction = str_to_enum('soft_margin_loss', 'reduction', reduction)
        return super().__call__([input, target, converted_reduction])


soft_margin_loss_impl = _PyboostSoftMarginLossPrim()


class _PyboostSplitPrim(SplitPrim_):
    def __call__(self, input_x, axis, output_num):

        return super().__call__([input_x, axis, output_num])


split_impl = _PyboostSplitPrim()


class _PyboostSqueezePrim(SqueezePrim_):
    def __call__(self, input, axis):

        return super().__call__([input, axis])


squeeze_impl = _PyboostSqueezePrim()


class _PyboostStackExtPrim(StackExtPrim_):
    def __call__(self, tensors, dim):

        return super().__call__([tensors, dim])


stack_ext_impl = _PyboostStackExtPrim()


class _PyboostTriuPrim(TriuPrim_):
    def __call__(self, input, diagonal):

        return super().__call__([input, diagonal])


triu_impl = _PyboostTriuPrim()


class _PyboostUniqueConsecutivePrim(UniqueConsecutivePrim_):
    def __call__(self, input, return_inverse, return_counts, dim):

        return super().__call__([input, return_inverse, return_counts, dim])


unique_consecutive_impl = _PyboostUniqueConsecutivePrim()


class _PyboostUpsampleTrilinear3DGradPrim(UpsampleTrilinear3DGradPrim_):
    def __call__(self, dy, input_size, output_size, scales, align_corners):

        return super().__call__([dy, input_size, output_size, scales, align_corners])


upsample_trilinear3d_grad_impl = _PyboostUpsampleTrilinear3DGradPrim()


class _PyboostUpsampleTrilinear3DPrim(UpsampleTrilinear3DPrim_):
    def __call__(self, x, output_size, scales, align_corners):

        return super().__call__([x, output_size, scales, align_corners])


upsample_trilinear3d_impl = _PyboostUpsampleTrilinear3DPrim()


class _PyboostFusedInferAttentionScorePrim(FusedInferAttentionScorePrim_):
    def __call__(self, query, key, value, pse_shift, attn_mask, actual_seq_lengths, actual_seq_lengths_kv, dequant_scale1, quant_scale1, dequant_scale2, quant_scale2, quant_offset2, antiquant_scale, antiquant_offset, block_table, query_padding_size, kv_padding_size, key_antiquant_scale, key_antiquant_offset, value_antiquant_scale, value_antiquant_offset, key_shared_prefix, value_shared_prefix, actual_shared_prefix_len, num_heads, scale_value, pre_tokens, next_tokens, input_layout, num_key_value_heads, sparse_mode, inner_precise, block_size, antiquant_mode, softmax_lse_flag, key_antiquant_mode, value_antiquant_mode):
        converted_input_layout = str_to_enum('fused_infer_attention_score', 'input_layout', input_layout)
        return super().__call__([query, key, value, pse_shift, attn_mask, actual_seq_lengths, actual_seq_lengths_kv, dequant_scale1, quant_scale1, dequant_scale2, quant_scale2, quant_offset2, antiquant_scale, antiquant_offset, block_table, query_padding_size, kv_padding_size, key_antiquant_scale, key_antiquant_offset, value_antiquant_scale, value_antiquant_offset, key_shared_prefix, value_shared_prefix, actual_shared_prefix_len, num_heads, scale_value, pre_tokens, next_tokens, converted_input_layout, num_key_value_heads, sparse_mode, inner_precise, block_size, antiquant_mode, softmax_lse_flag, key_antiquant_mode, value_antiquant_mode])


fused_infer_attention_score_impl = _PyboostFusedInferAttentionScorePrim()


class _PyboostGroupedMatmulPrim(GroupedMatmulPrim_):
    def __call__(self, x, weight, bias, scale, offset, antiquant_scale, antiquant_offset, group_list, split_item, group_type, transpose_a, transpose_b):

        return super().__call__([x, weight, bias, scale, offset, antiquant_scale, antiquant_offset, group_list, split_item, group_type, transpose_a, transpose_b])


grouped_matmul_impl = _PyboostGroupedMatmulPrim()


class _PyboostQuantBatchMatmulPrim(QuantBatchMatmulPrim_):
    def __call__(self, x1, x2, scale, offset, bias, pertokenScaleOptional, transpose_x1, transpose_x2, dtype):

        return super().__call__([x1, x2, scale, offset, bias, pertokenScaleOptional, transpose_x1, transpose_x2, dtype])


quant_batch_matmul_impl = _PyboostQuantBatchMatmulPrim()


class _PyboostWeightQuantBatchMatmulPrim(WeightQuantBatchMatmulPrim_):
    def __call__(self, x, weight, antiquant_scale, antiquant_offset, quant_scale, quant_offset, bias, transpose_x, transpose_weight, antiquant_group_size):

        return super().__call__([x, weight, antiquant_scale, antiquant_offset, quant_scale, quant_offset, bias, transpose_x, transpose_weight, antiquant_group_size])


weight_quant_batch_matmul_impl = _PyboostWeightQuantBatchMatmulPrim()
