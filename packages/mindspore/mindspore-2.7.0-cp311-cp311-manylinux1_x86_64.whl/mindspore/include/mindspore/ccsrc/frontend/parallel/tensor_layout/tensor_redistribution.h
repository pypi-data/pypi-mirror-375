/**
 * Copyright 2019-2024 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_FRONTEND_PARALLEL_TENSOR_LAYOUT_TENSOR_REDISTRIBUTION_H_
#define MINDSPORE_CCSRC_FRONTEND_PARALLEL_TENSOR_LAYOUT_TENSOR_REDISTRIBUTION_H_

#include <map>
#include <set>
#include <vector>
#include <utility>
#include <string>
#include "ir/value.h"
#include "frontend/parallel/status.h"
#include "frontend/parallel/tensor_layout/construct_operator.h"
#include "frontend/parallel/tensor_layout/redistribution_operator_infer.h"
#include "frontend/parallel/tensor_layout/tensor_layout.h"

namespace mindspore {
namespace parallel {
constexpr double ALLTOALL_SCALE_FACTOR = 2.0;
constexpr double ALLGATHER_REDUCESCATTER_SCALE_FACTOR = 0.5;
using AssembledDynamicDimsMapping = std::map<int64_t, std::pair<size_t, AnfNodePtr>>;
using ReplacementMemo = std::map<size_t, int64_t>;

class TensorRedistribution {
 public:
  explicit TensorRedistribution(bool construct_op_flag = true, bool keep_reshape = false)
      : is_inited_(false),
        is_computed_(false),
        reshape_flag_(false),
        comm_cost_(0.0),
        forward_comm_cost_(0.0),
        backward_comm_cost_(0.0),
        computation_cost_(0.0),
        memory_cost_(0.0),
        construct_op_flag_(construct_op_flag),
        keep_reshape_(keep_reshape) {}
  ~TensorRedistribution() = default;

  void SetPreAndNextCNode(const AnfNodePtr &pre_cnode, const CNodePtr &next_cnode) {
    this->pre_cnode_ = pre_cnode;
    this->next_cnode_ = next_cnode;
  }

  std::string PrintRedistribution() {
    return this->pre_cnode_->fullname_with_scope() + "->" + this->next_cnode_->fullname_with_scope();
  }

  void set_original_reshape_shape(const AnfNodePtr &original_reshape_shape) {
    this->original_reshape_shape_ = original_reshape_shape;
  }

  const AnfNodePtr original_reshape_shape() { return this->original_reshape_shape_; }
  bool is_dynamic_shape() { return this->is_dynamic_shape_; }
  Status Init(const TensorLayout &from, const TensorLayout &to, const RankList &dev_list,
              bool is_multi_dynamic_axis_reshape = false);
  RedistributionOpListPtr InferTensorRedistributionOperatorList(bool is_cost_model = false);
  std::vector<RedistributionOpListPtr> InferTensorRedistributionOperatorVirtualGraphs();
  RedistributionOpListPtr InferTensorRedistributionOperatorListForMultiDynamicReshape(bool is_cost_model = false);
  OperatorList operator_list() const { return operator_list_; }
  bool reshape_flag() const { return reshape_flag_; }
  bool IsInited() const { return this->is_inited_; }
  bool IsComputed() const { return this->is_computed_; }
  Status ComputeCost();
  double comm_cost() const { return comm_cost_; }
  double computation_cost() const { return computation_cost_; }
  double forward_comm_cost() const { return forward_comm_cost_; }
  double backward_comm_cost() const { return backward_comm_cost_; }
  double memory_cost() const { return memory_cost_; }
  Shape input_shape() const { return from_origin_.base_slice_shape().array(); }
  Status ResetLayoutTransfer() { return this->RollbackToDynamicShape(); }
  Status RollbackToDynamicShape();
  TensorLayout from_origin_layout() const { return this->from_origin_; }
  TensorLayout from_layout() const { return this->from_; }
  TensorLayout assembled_static_origin_from() const { return this->assembled_static_origin_from_; }
  TensorLayout from_origin_no_assembled() const { return this->from_origin_no_assembled_; }
  TensorLayout to_origin_no_assembled() const { return this->to_origin_no_assembled_; }
  bool IsAssembledStaticShape() const { return this->is_assembled_static_shape_; }
  bool IsMultiDynamicAxisReshape() const { return this->is_multi_dynamic_axis_reshape_; }
  RedistributionLayoutTransfer layout_transfer() const { return this->layout_transfer_; }
  AssembledDynamicDimsMapping GetDynamicDimsMapping() const { return this->dynamic_dim_mapping_; }
  void CreateAssembledDynamicMapping(const CNodePtr &cur_cnode, const AnfNodePtr &pre_cnode,
                                     const FuncGraphPtr &func_graph, int64_t redistribution_index);
  void SetVirtualRank(const int64_t virtual_rank) { virtual_rank_ = virtual_rank; }
  std::vector<int64_t> GetVirtualRankList() { return virtual_rank_list_; }

 private:
  Status CalculateToTensorShapeUsingEnumeration(const Shape &from_tsr_shape, Shape *to_tsr_shape, const Array &factors);
  Status CalculateToTensorShape(const Shape &from_shape, const Shape &origin_to_shape, const Array &to_in_factors,
                                Shape *to_shape);
  Status CalculateFromTensorShape(Shape *from_shape, const Array &from_factors, const Shape &to_shape,
                                  const Array &to_factors);
  Status AssembleStaticTensorShape(const TensorLayout &from_in, const TensorLayout &to_in,
                                   TensorLayout *new_from_layout, TensorLayout *new_to_layout);
  void UnifyAssembledMappingWithSqueezedFromShape();
  void UnifyAssembledMappingWithSameSize(const std::set<int64_t> &index_mapping);
  void UnifyAssembledMappingWithDiffSize(const std::set<int64_t> &index_mapping);
  Status InferReshape(const TensorLayout &from_layout, const TensorLayout &to_layout,
                      OperatorVector *const operator_vector, OutPutInfoVector *const output_info_vector);
  Status InferRedistribution(const TensorLayout &from_layout, const TensorLayout &to_layout,
                             OperatorVector *const operator_vector, OutPutInfoVector *const output_info_vector,
                             bool is_cost_model);
  Status ComputeConcatCost(double input_size, const Shape &attrs);
  Status ComputePermuteCost(double input_size, const Shape &attrs);
  RedistributionOpListPtr InferTensorRedistributionOperatorListUnExpand(bool is_cost_model = false);
  Status MakeFromToLayout(const TensorLayout &from, const TensorLayout &to);
  Status OperatorListIsEmpty(ConstructOperator *constructor, OperatorVector *const operator_vector,
                             OutPutInfoVector *const output_info_vector);
  RedistributionLayoutTransfer layout_transfer_;
  AssembledDynamicDimsMapping dynamic_dim_mapping_;
  TensorLayout from_origin_no_assembled_;
  TensorLayout to_origin_no_assembled_;
  TensorLayout from_origin_;
  TensorLayout to_origin_;
  TensorLayout from_;
  TensorLayout to_;
  TensorLayout assembled_static_origin_from_;
  bool is_inited_;
  bool is_computed_;
  RankList dev_list_;
  OperatorList operator_list_;
  bool reshape_flag_;
  // communication cost, which is the sum of forward communication cost and backward communication cost
  double comm_cost_;
  // forward communication cost
  double forward_comm_cost_;
  // backward communication cost
  double backward_comm_cost_;
  // computation_cost models the time spending on computing in this tensor redistribution, which is calculated by the
  // inputs. This is calculated ONLY for forward phase.
  double computation_cost_;
  // memory_cost models the PEAK memory cost in a training iteration contributed by this tensor redistribution, which is
  // calculated by the outputs.
  double memory_cost_;
  bool construct_op_flag_;
  bool keep_reshape_;
  bool expand_able_ = true;
  bool is_assembled_static_shape_ = false;
  bool is_multi_dynamic_axis_reshape_ = false;
  bool is_dynamic_shape_ = false;
  ReplacementMemo from_dims_replace_memo_;
  ReplacementMemo to_dims_replace_memo_;
  AnfNodePtr pre_cnode_;
  CNodePtr next_cnode_;
  int64_t virtual_rank_ = -1;
  std::vector<int64_t> virtual_rank_list_;
  AnfNodePtr original_reshape_shape_ = nullptr;
};
}  // namespace parallel
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_FRONTEND_PARALLEL_TENSOR_LAYOUT_TENSOR_REDISTRIBUTION_H_
