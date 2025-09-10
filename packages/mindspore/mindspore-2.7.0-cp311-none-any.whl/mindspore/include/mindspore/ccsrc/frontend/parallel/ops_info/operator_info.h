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

#ifndef MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_OPERATOR_INFO_H_
#define MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_OPERATOR_INFO_H_

#include <cstdint>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <utility>
#include <vector>
#include "ir/anf.h"
#include "utils/hash_map.h"
#include "utils/ms_utils.h"
#include "base/base.h"
#include "frontend/parallel/auto_parallel/costmodel.h"
#include "frontend/parallel/auto_parallel/operator_costmodel.h"
#include "frontend/parallel/device_manager.h"
#include "frontend/parallel/device_matrix.h"
#include "frontend/parallel/group_manager.h"
#include "frontend/parallel/ops_info/ops_utils.h"
#include "frontend/parallel/strategy.h"
#include "frontend/parallel/tensor_layout/tensor_info.h"
#include "frontend/parallel/tensor_layout/tensor_redistribution.h"
#include "utils/log_adapter.h"
#include "ops_utils/op_utils.h"
#include "utils/anf_utils.h"

namespace mindspore {
namespace parallel {
using ForwardOp = OperatorVector;
using ForwardOpList = std::vector<ForwardOp>;
using MirrorOps = std::vector<OperatorVector>;
using Ops = std::vector<OperatorVector>;
using VirtualDivOp = OperatorVector;
using TensorMaps = std::vector<Shape>;
using TensorMapBefores = std::vector<std::vector<Shape>>;
using TensorLayouts = std::vector<TensorLayout>;
using different_type = std::vector<int64_t>::difference_type;
using PrimitiveAttrs = mindspore::HashMap<std::string, ValuePtr>;
using ReplaceGraphPtr = std::shared_ptr<std::pair<std::vector<std::pair<AnfNodePtr, int64_t>>, AnfNodePtr>>;
using TensorRedistributionPtr = std::shared_ptr<TensorRedistribution>;

#define FILTER_LOG(x) (x) ? void(0) : MS_LOG(ERROR)

enum InferStrategyMode {
  SAME_MODE = 0,
  BROADCAST_MODE = 1,
  INDEPENDENT_MODE = 2,
  INDIVIDUAL_MODE = 3,
  INVALID_MODE = 4,
};

class TensorLayoutBase {
 public:
  explicit TensorLayoutBase(bool is_list) : is_list_(is_list) {}
  virtual ~TensorLayoutBase() = default;
  bool is_list() const { return is_list_; }
  bool no_shape_layout() const { return no_shape_layout_; }
  void set_no_shape_layout(bool no_shape_layout) { no_shape_layout_ = no_shape_layout; }
  virtual std::shared_ptr<TensorLayoutBase> GetElement(int64_t idx) = 0;
  virtual std::shared_ptr<TensorLayout> GetValue() = 0;
  virtual size_t size() = 0;
  virtual std::vector<std::shared_ptr<TensorLayout>> GetAllElements() = 0;

 private:
  bool is_list_;
  bool no_shape_layout_ = false;
};

using TensorLayoutBasePtr = std::shared_ptr<TensorLayoutBase>;

class TensorLayoutValue : public TensorLayoutBase {
 public:
  explicit TensorLayoutValue(std::shared_ptr<TensorLayout> l) : TensorLayoutBase(false), _l(std::move(l)) {}
  TensorLayoutValue() : TensorLayoutBase(false) { set_no_shape_layout(true); }
  ~TensorLayoutValue() override = default;
  std::shared_ptr<TensorLayoutBase> GetElement(int64_t idx) override {
    MS_LOG(WARNING) << "Can not get element from TensorLayoutValue, please use GetValue";
    return std::make_shared<TensorLayoutValue>(_l);
  }
  std::vector<std::shared_ptr<TensorLayout>> GetAllElements() override { return {_l}; }
  std::shared_ptr<TensorLayout> GetValue() override { return _l; }
  size_t size() override { return 1; }

 private:
  std::shared_ptr<TensorLayout> _l;
};

class TensorLayoutList : public TensorLayoutBase {
 public:
  explicit TensorLayoutList(std::vector<TensorLayoutBasePtr> l_list)
      : TensorLayoutBase(true), _l_list(std::move(l_list)) {}
  explicit TensorLayoutList(size_t n) : TensorLayoutBase(true) {
    set_no_shape_layout(true);
    for (size_t i = 0; i < n; ++i) {
      _l_list.emplace_back(std::make_shared<TensorLayoutValue>());
    }
  }
  ~TensorLayoutList() override = default;
  TensorLayoutBasePtr GetElement(int64_t idx) override {
    if (idx < 0 || static_cast<size_t>(idx) >= _l_list.size()) {
      MS_LOG(EXCEPTION) << "Index " << idx << " is out of range";
    }
    return _l_list[LongToSize(idx)];
  }
  std::vector<std::shared_ptr<TensorLayout>> GetAllElements() override {
    std::vector<std::shared_ptr<TensorLayout>> all_elements;
    for (auto &l : _l_list) {
      auto elements = l->GetAllElements();
      all_elements.insert(all_elements.end(), elements.begin(), elements.end());
    }
    return all_elements;
  }
  std::shared_ptr<TensorLayout> GetValue() override { MS_LOG(EXCEPTION) << "Can not get value from TensorLayoutList"; }
  size_t size() override { return _l_list.size(); }

 private:
  std::vector<TensorLayoutBasePtr> _l_list;
};

class TensorInfoBase {
 public:
  explicit TensorInfoBase(bool is_list) { is_list_ = is_list; }
  virtual ~TensorInfoBase() = default;
  bool is_list() const { return is_list_; }
  virtual std::shared_ptr<TensorInfoBase> GetElement(int64_t idx) = 0;
  virtual TensorInfo GetValue() = 0;
  virtual size_t size() = 0;
  virtual std::vector<TensorInfo> GetAllElements() = 0;

 private:
  bool is_list_;
};

using TensorInfoBasePtr = std::shared_ptr<TensorInfoBase>;

class TensorInfoValue : public TensorInfoBase {
 public:
  explicit TensorInfoValue(TensorInfo l) : TensorInfoBase(false), _l(std::move(l)) {}
  explicit TensorInfoValue(TensorLayoutBasePtr l) : TensorInfoBase(false) {
    if (l->is_list()) {
      MS_LOG(EXCEPTION) << "Input TensorLayoutBasePTr l is a list. Please use TensorInfoList to create instance";
    }
    auto l_value = std::dynamic_pointer_cast<TensorLayoutValue>(l);
    if (l_value == nullptr) {
      MS_LOG(EXCEPTION) << "Input TensorLayoutBasePtr l is not a TensorLayoutValue";
    }
    TensorInfo tensor_info(*(l_value->GetValue()));
    _l = tensor_info;
  }
  ~TensorInfoValue() override = default;
  std::shared_ptr<TensorInfoBase> GetElement(int64_t idx) override {
    MS_LOG(WARNING) << "Can not get element from TensorInfoValue, please use GetValue";
    return std::make_shared<TensorInfoValue>(_l);
  }
  std::vector<TensorInfo> GetAllElements() override { return {_l}; }
  TensorInfo GetValue() override { return _l; }
  size_t size() override { return 1; }

 private:
  TensorInfo _l;
};

class TensorInfoList : public TensorInfoBase {
 public:
  explicit TensorInfoList(std::vector<TensorInfoBasePtr> l_list) : TensorInfoBase(true), _l_list(std::move(l_list)) {}
  explicit TensorInfoList(TensorLayoutBasePtr l) : TensorInfoBase(true) {
    if (!l->is_list()) {
      MS_LOG(EXCEPTION) << "Input TensorLayoutBasePTr l is not a list. Please use TensorInfoValue to create instance";
    }
    auto l_list = std::dynamic_pointer_cast<TensorLayoutList>(l);
    if (l_list == nullptr) {
      MS_LOG(EXCEPTION) << "Input TensorLayoutBasePtr l is not a TensorLayoutList";
    }
    for (size_t i = 0; i < l_list->size(); ++i) {
      auto l_value = l_list->GetElement(SizeToLong(i));
      if (l_value->is_list()) {
        _l_list.emplace_back(std::make_shared<TensorInfoList>(l_value));
      } else {
        _l_list.emplace_back(std::make_shared<TensorInfoValue>(l_value));
      }
    }
  }
  ~TensorInfoList() override = default;
  TensorInfoBasePtr GetElement(int64_t idx) override {
    if (idx < 0 || static_cast<size_t>(idx) >= _l_list.size()) {
      MS_LOG(EXCEPTION) << "Index " << idx << " is out of range";
    }
    return _l_list[LongToSize(idx)];
  }
  std::vector<TensorInfo> GetAllElements() override {
    std::vector<TensorInfo> all_elements;
    for (auto &l : _l_list) {
      auto elements = l->GetAllElements();
      all_elements.insert(all_elements.end(), elements.begin(), elements.end());
    }
    return all_elements;
  }
  TensorInfo GetValue() override { MS_LOG(EXCEPTION) << "Can not get value from TensorInfoList"; }
  size_t size() override { return _l_list.size(); }

 private:
  std::vector<TensorInfoBasePtr> _l_list;
};

class OperatorVectorBase {
 public:
  explicit OperatorVectorBase(bool is_list) { is_list_ = is_list; }
  virtual ~OperatorVectorBase() = default;
  virtual std::vector<OperatorVector> GetAllElements() = 0;

 private:
  bool is_list_;
};

using OperatorVectorBasePtr = std::shared_ptr<OperatorVectorBase>;

class OperatorVectorValue : public OperatorVectorBase {
 public:
  explicit OperatorVectorValue(OperatorVector m_op) : OperatorVectorBase(false), _m_op(std::move(m_op)) {}
  ~OperatorVectorValue() override = default;
  std::vector<OperatorVector> GetAllElements() override { return {_m_op}; }

 private:
  OperatorVector _m_op;
};

class OperatorVectorList : public OperatorVectorBase {
 public:
  explicit OperatorVectorList(std::vector<OperatorVectorBasePtr> m_ops)
      : OperatorVectorBase(true), _m_ops(std::move(m_ops)) {}
  ~OperatorVectorList() override = default;
  std::vector<OperatorVector> GetAllElements() override {
    std::vector<OperatorVector> all_elements;
    for (auto &op : _m_ops) {
      auto elements = op->GetAllElements();
      all_elements.insert(all_elements.end(), elements.begin(), elements.end());
    }
    return all_elements;
  }

 private:
  std::vector<OperatorVectorBasePtr> _m_ops;
};

class Edge;

inline std::string GetPrimNameFromInfoName(const std::string &info_name);

class OperatorInfo {
 public:
  OperatorInfo(std::string name, Shapes inputs_shape, Shapes outputs_shape, PrimitiveAttrs attrs,
               const OperatorCostPtr &cost)
      : name_(std::move(name)),
        inputs_shape_(std::move(inputs_shape)),
        outputs_shape_(std::move(outputs_shape)),
        attrs_(std::move(attrs)),
        is_alive_(true),
        operator_cost_(cost),
        outputs_type_() {
    std::vector<bool> not_parameteter(inputs_shape_.size(), false);
    is_parameter_ = not_parameteter;
    refkey_parameter_name_ = "";
    stage_device_list_ = g_device_manager->GetDeviceListInThisStage();
    stage_device_size_ = SizeToLong(stage_device_list_.size());
    cnode_ = nullptr;
    prim_name_ = GetPrimNameFromInfoName(this->name_);
  }

  virtual ~OperatorInfo() = default;

  void set_involved_param_name(std::string name) { involved_param_name_ = name; }
  std::string get_involved_param_name() { return involved_param_name_; }
  Status set_is_parameter(const std::vector<bool> &is_parameter);
  Status SetInputAndOutputTypeLength(const std::vector<size_t> &input_lengths,
                                     const std::vector<size_t> &output_lengths);
  double GetOutputsTotalSize();
  // Set outputs dtype.
  // If only one output, outputs_type.size() is 1.
  // If output is tuple, outputs_type.size() is greater than 1.
  Status set_outputs_type(const std::vector<TypePtr> &outputs_type);
  const std::vector<TypePtr> &outputs_type() const { return outputs_type_; }
  virtual Status Init(const StrategyPtr &in_strategy, const StrategyPtr &out_strategy,
                      const std::vector<std::shared_ptr<TensorLayout>> &in_tensor_layouts = {},
                      const std::vector<std::shared_ptr<TensorLayout>> &out_tensor_layouts = {});
  virtual Status Init(const StrategyPtr &in_strategy, const StrategyPtr &out_strategy,
                      const std::vector<TensorLayoutBasePtr> &in_tensor_layouts,
                      const std::vector<TensorLayoutBasePtr> &out_tensor_layouts);
  // only init the necessary parts
  virtual Status InitForCostModel(const StrategyPtr &in_strategy, const StrategyPtr &out_strategy);

  // Given the stage_id (which indicates the number of devices),
  // generate all strategies for this operator
  Status GenerateStrategies(int64_t stage_id);
  virtual std::vector<StrategyPtr> GenerateOpStrategies(int64_t stage_id) = 0;
  const OperatorCostPtr &operator_cost() const { return operator_cost_; }
  void set_cost(const OperatorCostPtr &cost) { operator_cost_ = cost; }
  virtual Status SetCostUnderStrategy(const StrategyPtr &strategy) = 0;

  virtual std::shared_ptr<Strategies> GenerateBatchStrategies();
  virtual void ReComputeBatchSplitFlagList();
  std::shared_ptr<Strategies> GenerateBatchStrategiesWithCheck();
  void ComputeBatchSplitFlagList();
  Shapes inputs_shape() const { return inputs_shape_; }
  NewShapes inputs_shape_new() const { return inputs_shape_new_; }
  Shapes outputs_shape() const { return outputs_shape_; }
  NewShapes outputs_shape_new() const { return outputs_shape_new_; }
  void set_inputs_divisor(const Shapes &in_divisor) { inputs_divisor_ = in_divisor; }
  void set_outputs_divisor(const Shapes &out_divisor) { outputs_divisor_ = out_divisor; }
  void set_dynamic_shape_flag(bool flag) { dynamic_shape_flag_ = flag; }
  Shapes inputs_divisor() { return inputs_divisor_; }
  Shapes outputs_divisor() { return outputs_divisor_; }
  bool dynamic_shape_flag() { return dynamic_shape_flag_; }
  bool use_shape_base() const { return use_shape_base_; }

  double GetForwardMemoryCostFromCNode();
  // This is a common method for setting operator cost for a given strategy, in which the validity of this strategy
  // is checked
  Status SetCostUnderStrategyBase(const StrategyPtr &strategy);
  Status SetCostUnderLayout(const StrategyPtr &in_strategy, const StrategyPtr &out_strategy,
                            const std::vector<std::shared_ptr<TensorLayout>> &in_tensor_layouts,
                            const std::vector<std::shared_ptr<TensorLayout>> &out_tensor_layouts);
  Status SetCostUnderStrategyWithCost(const std::shared_ptr<StrategyWithCost> &swc);
  void SetDefaultLayoutInfo();
  std::vector<std::shared_ptr<StrategyWithCost>> GetStrategyCost() { return strategy_cost_; }
  void SetStrategyCost(const std::vector<std::shared_ptr<StrategyWithCost>> &stra_cost);
  // In the training phase, when the input of a operator contains WEIGHT or a output from other operators involving
  // WEIGHT, then these input should stay in memory until it is used in the backward phase, which is kept in memory
  // at the end of forward phase.
  Status CalculateMemoryCost();
  // In the inference phase, the memory cost is incurred only when the operator is critical. The size is calculated
  // by the output
  Status CalculateMemoryCostForInference();
  virtual int64_t ComputeOpAndPrevEdgeParameterInvolved();

  ForwardOp forward_op() const { return forward_op_; }
  ForwardOpList forward_op_list() const { return forward_op_list_; }
  ForwardOp replace_op() const { return replace_op_; }
  OutPutInfoVector replace_op_info() const { return replace_op_info_; }
  virtual ReplaceGraphPtr replace_graph(const CNodePtr &) { return replace_graph_; }
  MirrorOps mirror_ops() const { return mirror_ops_; }
  std::vector<OperatorVectorBasePtr> mirror_ops_new() const { return mirror_ops_new_; }
  Ops sub_ops() const { return sub_ops_; }
  VirtualDivOp virtual_div_op() const { return virtual_div_op_; }
  Shape dev_matrix_shape() const { return dev_matrix_shape_; }
  Shape out_dev_matrix_shape() const { return out_dev_matrix_shape_; }
  std::vector<TensorInfo> inputs_tensor_info() const { return inputs_tensor_info_; }
  std::vector<TensorInfoBasePtr> inputs_tensor_info_new() const { return inputs_tensor_info_new_; }
  void set_inputs_tensor_info(const std::vector<TensorInfo> &tensor_info) { inputs_tensor_info_ = tensor_info; }
  void set_inputs_tensor_info_new(const std::vector<TensorInfoBasePtr> &tensor_info) {
    inputs_tensor_info_new_ = tensor_info;
  }
  std::vector<TensorInfo> outputs_tensor_info() const { return outputs_tensor_info_; }
  std::vector<TensorInfoBasePtr> outputs_tensor_info_new() const { return outputs_tensor_info_new_; }
  const std::string &name() const { return name_; }
  void set_name(const std::string &name) { name_ = name; }
  void set_mirror_ops(const MirrorOps &mirror_ops) { mirror_ops_ = mirror_ops; }
  RankList stage_device_list() const { return stage_device_list_; }

  void AddSuccEdge(const std::shared_ptr<Edge> &e) { succ_edges_.push_back(e); }
  void AddPrevEdge(const std::shared_ptr<Edge> &e) { prev_edges_.push_back(e); }
  std::vector<std::shared_ptr<Edge>> succ_edges() const { return succ_edges_; }
  std::vector<std::shared_ptr<Edge>> prev_edges() const { return prev_edges_; }
  std::vector<std::shared_ptr<Edge>> GetAliveSuccEdges();
  std::vector<std::shared_ptr<Edge>> GetAlivePrevEdges();
  void ReplacePreEdge(const std::shared_ptr<OperatorInfo> &op, const std::shared_ptr<Edge> &new_edge);
  void ReplaceSuccEdge(const std::shared_ptr<OperatorInfo> &op, const std::shared_ptr<Edge> &new_edge);
  void ReplacePreEdges(const std::shared_ptr<OperatorInfo> &op, const std::shared_ptr<Edge> &new_edge);
  void ReplaceSuccEdges(const std::shared_ptr<OperatorInfo> &op, const std::shared_ptr<Edge> &new_edge);
  std::vector<size_t> GetOutputTypeLengths() const { return operator_cost()->outputs_type_lengths(); }
  void SetSelectedStrategyAndCost(const StrategyPtr &s_strategy, const CostPtr &cost) {
    selected_strategy_ = s_strategy;
    selected_cost_ = cost;
  }
  void SetSelectedStrategy(const StrategyPtr &s_strategy, size_t curr_depth);
  StrategyPtr selected_strategy() const { return selected_strategy_; }
  CostPtr selected_cost() const { return selected_cost_; }

  TensorLayout GetInputLayoutFromSWCByStrategy(const StrategyPtr &stra, size_t input_index);
  TensorLayout GetOutputLayoutFromSWCByStrategy(const StrategyPtr &stra, size_t output_index);
  StrategyPtr GetStrategyFromSWCByInputLayout(const TensorLayout &input_layout, size_t input_index);
  StrategyPtr GetStrategyFromSWCByOutputLayout(const TensorLayout &output_layout, size_t output_index);

  std::vector<std::shared_ptr<StrategyWithCost>> GetSwcByInputLayout(const TensorLayout &input_layout,
                                                                     size_t input_index);
  std::vector<std::shared_ptr<StrategyWithCost>> GetSwcByOutputLayout(const TensorLayout &output_layout,
                                                                      size_t output_index);
  bool IsReshape() const;
  bool IsVirtualOutput() const;
  bool IsConcat() const;
  bool IsStandAlone() const;
  bool IsTmpIdentity() const;
  bool IsMultiInput() const;
  bool AllInputsVisited() const;
  void AddVisitedEdge(const std::shared_ptr<Edge> &e) { visited_edges_.push_back(e); }
  void ClearVisitedEdges() { visited_edges_.clear(); }
  std::shared_ptr<StrategyWithCost> GetStrategyByVisitedEdges();

  void set_swc_index(int64_t swc, int64_t depth);
  int64_t swc_index() const { return swc_index_; }
  void set_topo_index(int64_t index) { topo_index_ = index; }
  int64_t get_topo_index() { return topo_index_; }
  // Approximate the list of available strategies
  void ApproximateStrategies();
  // Make the list of available strategies exact and re-init the related edges incident to this operator
  void ExactStrategiesAndRelatedEdges();
  bool is_strategy_cost_exact() const { return is_strategy_cost_exact_; }
  void SetIsStrategyCostExactTrue() { is_strategy_cost_exact_ = true; }
  void ClearStrategyCost() { strategy_cost_.clear(); }
  void CheckSelectedStrategy(const StrategyPtr &s_strategy);
  Status InitSelectedStrategy(const StrategyPtr &in_strategy, const StrategyPtr &out_strategy) {
    set_auto_parallel(false);
    return Init(in_strategy, out_strategy);
  }
  void set_input_value(const std::vector<ValuePtr> &input_value) { input_value_ = input_value; }
  const std::vector<ValuePtr> &input_value() const { return input_value_; }
  void set_outputs_dtype(const TypePtr &dtype) { outputs_dtype_ = dtype; }
  void set_cnode(const CNodePtr &cnode) {
    cnode_ = cnode;
    cnodes_.push_back(cnode);
  }
  void clear_cnodes() { cnodes_.clear(); }
  void set_new_shape(const std::vector<NewShapes> &shape) {
    inputs_shape_new_ = shape[0];
    outputs_shape_new_ = shape[1];
  }
  std::vector<CNodePtr> cnodes();
  CNodePtr cnode() const { return cnode_; }
  bool is_alive() const { return is_alive_; }
  void SetNotAlive() { is_alive_ = false; }
  std::vector<bool> split_flag_list() const { return split_flag_list_; }
  std::vector<std::shared_ptr<Edge>> &get_visited_edges() { return visited_edges_; }
  StrategyPtr strategy() const { return strategy_; }
  StrategyPtr out_strategy() const { return out_strategy_; }
  void set_out_strategy(const StrategyPtr &strategy) { out_strategy_ = strategy; }
  void set_strategy(const StrategyPtr &strategy) { strategy_ = strategy; }
  void clear_strategy() { strategy_ = nullptr; }
  void clear_out_strategy() { out_strategy_ = nullptr; }
  void set_config_by_layout(bool is_config_by_layout) { is_config_by_layout_ = is_config_by_layout; }
  bool is_config_by_layout() { return is_config_by_layout_; }
  void set_is_new_shape_node(bool is_new_shape_node) { is_new_shape_node_ = is_new_shape_node; }
  bool is_new_shape_node() { return is_new_shape_node_; }
  void set_refkey_parameter_name(std::string p_name) { refkey_parameter_name_ = std::move(p_name); }
  const std::string &refkey_parameter_name() const { return refkey_parameter_name_; }
  // When the output of a Parameter (require_grad) being used by multiple operators, the Parameter's cost is calculated
  // multiple times. This method is to correct this, and makes the cost is calculated only once.
  Status CorrectMemoryCost(size_t input_index);
  int64_t is_output_parameter_involve() const { return is_output_parameter_involve_; }
  int64_t is_output_critical() const { return is_output_critical_; }
  void mark_output_critical() { is_output_critical_ = 1; }
  void mark_output_not_critical() { is_output_critical_ = 0; }
  int64_t used_devices() const { return used_devices_; }
  // needed by rec_parser
  void set_type(const std::string &type) { type_ = type; }
  const std::string &type() const { return type_; }
  void set_last_node_flag(const bool &is_last_node) { is_last_node_ = is_last_node; }
  const bool &is_last_node() const { return is_last_node_; }
  const mindspore::HashMap<std::string, ValuePtr> &attrs() const { return attrs_; }
  void addAttr(const std::string &name, const ValuePtr &val) { attrs_[name] = val; }
  void set_stage_id(int32_t stage_id) { stage_id_ = stage_id; }
  int32_t stage_id() const { return stage_id_; }
  Status CreateGroupByTensorMap(const Shape &tensor_map, std::vector<Group> *group);
  Status CreateGroupForOptShard(TensorLayout *tensor_layout, std::vector<Group> *groups);
  virtual void ReplaceNodeInputOrAttrs() {}
  void set_auto_parallel(bool is_auto_parallel) { is_auto_parallel_ = is_auto_parallel; }
  void set_assigned_parallel(bool is_assigned_parallel) { is_assigned_parallel_ = is_assigned_parallel; }
  bool repeated_num_in_dev_matrix_right() const { return repeated_num_in_dev_matrix_right_; }
  void set_repeated_num_in_dev_matrix_right(bool is_right) { repeated_num_in_dev_matrix_right_ = is_right; }

  void LayoutPropagationBegin() { is_in_layout_propagation_ = true; }
  void LayoutPropagationEnd() { is_in_layout_propagation_ = false; }

  Status AddSwcUnderPrevOpDevMatrixSingle(const Shape &prev_op_dev_matrix, const std::vector<Shape> &prev_op_tensor_map,
                                          size_t layout_index);
  Status AddSwcUnderNextOpDevMatrixSingle(const std::shared_ptr<OperatorInfo> &next_op,
                                          const std::shared_ptr<Edge> &edge);
  std::vector<std::shared_ptr<TensorLayout>> InferLayoutsByStrategy(const StrategyPtr &strategy_ptr,
                                                                    const std::vector<Shape> &prev_op_tensor_map,
                                                                    size_t layout_index);

  bool StrategyMatchTensorMap(const StrategyPtr &strategy_ptr,
                              const std::vector<std::vector<Shape>> &prev_op_tensor_maps);
  Status AddSwcUnderPrevOpDevMatrixMulti();
  bool CheckPrevOpStatus(const Shape &prev_op_dev_matrix, const std::vector<Shape> &prev_op_tensor_map,
                         size_t layout_index);
  std::vector<std::shared_ptr<TensorLayout>> InferLayoutsByStrategy(
    const StrategyPtr &strategy_ptr, const std::vector<std::vector<Shape>> &prev_op_tensor_maps);
  void InitVisitedEdges();

  TensorRedistributionPtr CreateTensorRedistribution(bool construct_op_flag = true, bool keep_reshape = false) {
    if (this->tensor_redistribution_ != nullptr) {
      MS_LOG(DEBUG) << "TensorRedistribution re-created.";
    }
    this->tensor_redistribution_ = std::make_shared<TensorRedistribution>(construct_op_flag, keep_reshape);
    return this->tensor_redistribution_;
  }

  TensorRedistributionPtr CreateReshapeTensorRedistribution(bool construct_op_flag = true, bool keep_reshape = false) {
    if (this->reshape_tensor_redistribution_ != nullptr) {
      MS_LOG(DEBUG) << "TensorRedistribution re-created.";
    }
    this->reshape_tensor_redistribution_ = std::make_shared<TensorRedistribution>(construct_op_flag, keep_reshape);
    return this->reshape_tensor_redistribution_;
  }

  void SetTensorRedistribution(const TensorRedistributionPtr &tensor_redistribution) {
    this->tensor_redistribution_ = tensor_redistribution;
  }

  void SetReshapeTensorRedistribution(const TensorRedistributionPtr &tensor_redistribution) {
    this->reshape_tensor_redistribution_ = tensor_redistribution;
  }

  TensorRedistributionPtr tensor_redistribution() { return this->tensor_redistribution_; }

  TensorRedistributionPtr reshape_tensor_redistribution() { return this->reshape_tensor_redistribution_; }

  // Key for user data.
  constexpr static char key[] = "OpInfo";

  // return Dump IR parallel detail
  int64_t as_loss_divisor() const { return as_loss_divisor_; }
  TensorMaps inputs_tensor_map() const { return inputs_tensor_map_; }
  TensorMaps outputs_tensor_map() const { return outputs_tensor_map_; }
  NewTensorMaps inputs_tensor_map_new() const { return inputs_tensor_map_new_; }
  NewTensorMaps outputs_tensor_map_new() const { return outputs_tensor_map_new_; }
  TensorMapBefores inputs_tensor_map_before() const { return inputs_tensor_map_before_; }
  TensorMapBefores outputs_tensor_map_before() const { return outputs_tensor_map_before_; }

 protected:
  // needed by rec_parser
  std::string type_;
  TensorRedistributionPtr tensor_redistribution_;
  TensorRedistributionPtr reshape_tensor_redistribution_;
  bool is_last_node_ = false;
  virtual Status CheckStrategy(const StrategyPtr &strategy) = 0;
  virtual Status InferTensorMap() = 0;
  virtual Status InferOutputTensorMap() { return SUCCESS; }
  virtual Status InferOutputTensorInfo() { return SUCCESS; }
  virtual Status CheckLayoutConfig() { return SUCCESS; }
  virtual Status CheckInputLayout();
  virtual Status CheckOutputLayout() { return SUCCESS; }
  virtual Status InferForwardCommunicationByLayout() { return SUCCESS; }
  virtual Status InferMirrorOpsByLayout();
  virtual Status InferForwardCommunication() = 0;
  virtual Status GetAttrs() = 0;
  virtual Status InferDevMatrixShape() = 0;
  virtual Status InferMirrorOps();
  virtual Status InferTensorInfo();
  virtual Status InferTensorInfoNew();
  virtual void InferReplaceOps() {}
  virtual void UpdateOutputTensorInfoForInterleaved();
  virtual Status CheckOutputStrategy(const StrategyPtr &out_strategy);
  virtual Status CheckStrategyForDynamicShape(const StrategyPtr &strategy) { return SUCCESS; }
  Status CheckStrategyByVector(const Shapes &strategy, const Shapes &inputs_shape);
  Status CheckStrategyValue(const StrategyPtr &strategy, const Shapes &inputs_shape);
  void DivisorsReplaceShapes();  // in dynamic shape, using divisors replace to shapes before CheckStrategy and so on
  void ResumeShapes();           // in dynamic shape, resume shapes after CheckStrategy and so on
  void DynamicShapeCheckStrategyLog();
  virtual void SetRepeatedCalcDevMatrix();
  void ResetTensorMapIfRepeatedCalc();
  void ResetTupleTensorMapIfRepeatedCalc(NewTensorMaps *tensor_map_new);
  void ChangeMakeTupleConstant(const CNodePtr &cnode, size_t make_tuple_index);
  Status CreateGroupByDim(size_t axis, std::vector<Group> *group);
  Status CreateGroupByDimWithDevMatrix(DeviceMatrix *dev_matrix, size_t axis, std::vector<Group> *group);
  Status InferAttrs();
  void ResetQueueMember();
  Status InitWithAutoRepeatCalc(const StrategyPtr &in_strategy, const StrategyPtr &out_strategy);
  Status InitWithTensorLayout(const std::vector<std::shared_ptr<TensorLayout>> &in_tensor_layouts,
                              const std::vector<std::shared_ptr<TensorLayout>> &out_tensor_layouts);
  Status InitWithTensorLayoutForNewShape(const std::vector<TensorLayoutBasePtr> &in_tensor_layouts,
                                         const std::vector<TensorLayoutBasePtr> &out_tensor_layouts);
  Status InitWithTensorLayoutPostProcess();
  Status InitForCostModelWithAutoRepeatCalc(const StrategyPtr &in_strategy, const StrategyPtr &out_strategy);
  Status InferRepeatedCalcInfo();
  Status InferVirtualDivOps();
  Status InferVirtualDivOpsByLayout();
  bool IsDynamicShape();
  bool IsDynamicRank();
  bool IsSelfDefineShard();
  CostPtr ComputeCost(const StrategyPtr &strategy);

  // Calculate the number of repeated calculations for the output by the number of devices and the output tensor map.
  // The tensor map of Outputs[0] is used by default. If there are multiple outputs, need to identify which output
  // is used for grad and overload the function. If the output is a scalar, need to override the function too.
  virtual Status InferAsLossDivisor();
  virtual Status InferAsLossDivisorByLayout();
  void BreakingTiesForPreferringDataParallel(const StrategyPtr &stra, const CostPtr &cost) const;
  int64_t GetIntAttr(const std::string &attr_name);
  bool GetBoolAttr(const std::string &attr_name);
  float GetFloatAttr(const std::string &attr_name);
  std::string GetStringAttr(const std::string &attr_name);
  std::vector<int64_t> GetTupleIntAttr(const std::string &attr_name);
  void ReportError(const std::string &error_msg) const {
    if (is_auto_parallel_) {
      MS_LOG(DEBUG) << error_msg;
    } else {
      MS_LOG(ERROR) << error_msg;
    }
  }
  Status InferByStrategy(const StrategyPtr &in_strategy, const StrategyPtr &out_strategy);

  std::string name_;
  std::string prim_name_;
  Shapes inputs_shape_;
  Shapes outputs_shape_;
  NewShapes inputs_shape_new_;
  NewShapes outputs_shape_new_;
  Shapes inputs_divisor_;   // using for dynamic shape, the size is equal to inputs_shape_
  Shapes outputs_divisor_;  // using for dynamic shape, the size is equal to outputs_shape_
  Shapes inputs_shape_clone_;
  Shapes outputs_shape_clone_;
  bool dynamic_shape_flag_ = False;  // means this op in the dynamic shape graph
  mindspore::HashMap<std::string, ValuePtr> attrs_;
  std::vector<ValuePtr> input_value_;
  TypePtr outputs_dtype_;

  int32_t stage_id_ = 0;
  StrategyPtr strategy_;
  StrategyPtr out_strategy_;
  std::vector<TensorInfo> inputs_tensor_info_;
  std::vector<TensorInfo> outputs_tensor_info_;
  std::vector<TensorInfoBasePtr> inputs_tensor_info_new_;
  std::vector<TensorInfoBasePtr> outputs_tensor_info_new_;
  Shape dev_matrix_shape_;  // if repeated calculation, it contains the repeated_calc_num_
  Shape out_dev_matrix_shape_;
  int64_t repeated_calc_num_ = 1;
  int64_t as_loss_divisor_ = 1;
  TensorMaps inputs_tensor_map_;
  TensorMaps outputs_tensor_map_;
  TensorMapBefores inputs_tensor_map_before_;
  TensorMapBefores outputs_tensor_map_before_;
  NewTensorMaps inputs_tensor_map_new_;
  NewTensorMaps outputs_tensor_map_new_;
  ForwardOp forward_op_;
  ForwardOpList forward_op_list_;
  ForwardOp forward_op_interleaved_;
  Ops sub_ops_;
  ForwardOp replace_op_;
  OutPutInfoVector replace_op_info_;
  ReplaceGraphPtr replace_graph_;
  MirrorOps mirror_ops_;
  std::vector<OperatorVectorBasePtr> mirror_ops_new_;
  VirtualDivOp virtual_div_op_;
  RankList stage_device_list_;  // the device list in this stage
  int64_t stage_device_size_ = 0;
  bool infer_attrs_completed_ = false;
  bool is_layout_config_ = false;
  bool is_config_by_layout_ = false;
  bool is_new_shape_node_ = false;
  bool is_dynamic_shape_ = false;
  bool is_dynamic_rank_ = false;
  Shapes strategy_from_layout_;

  bool is_auto_parallel_ = false;      // false: semi_auto_parallel; true: auto_parallel
  bool is_assigned_parallel_ = false;  // false: origin parallel; true: dynamic_shape parallel
  // 'corrected_input_indices_' used to store the indices of input that have ALREADY been corrected.
  std::vector<size_t> corrected_input_indices_;
  // Given a parallelization strategy, there is a cost.
  std::vector<std::shared_ptr<StrategyWithCost>> strategy_cost_;
  std::string involved_param_name_;
  // For each input in 'inputs_', there is a bool variable indicating whether that the corresponding input is parameter
  std::vector<bool> is_parameter_;
  // For each input in 'inputs_', a bool variable is true if the corresponding one is a parameter or a output of
  // pre-operator that has parameters as input.
  std::vector<bool> is_parameter_involve_;
  // If any input is parameter-involved, the output is parameter-involved. This variable is used in calculating
  // peak memory cost in the training phase.
  // -1: unset; 0: not parameter_involved; 1: parameter_involved
  int64_t is_output_parameter_involve_ = -1;
  // Whether this output is critical, which means that this output is included in calculating peak memory cost
  // in the inference phase.
  // -1 : unset; 0: not critical; 1: critical
  int64_t is_output_critical_ = -1;
  double outputs_total_size_ = 0.0;
  bool is_calculated_outputs_size_ = false;
  // for each input and output, the followings record the number of bytes of each element
  std::vector<size_t> inputs_type_lengths_;
  std::vector<size_t> outputs_type_lengths_;
  std::vector<std::shared_ptr<Edge>> prev_edges_;
  std::vector<std::shared_ptr<Edge>> succ_edges_;
  std::vector<std::shared_ptr<Edge>> visited_edges_;
  StrategyPtr selected_strategy_;
  int64_t selected_strategy_depth_ = -1;
  int64_t topo_index_ = -1;
  // Used in DP algorithm
  bool is_alive_;
  CostPtr selected_cost_;
  std::vector<bool> split_flag_list_;
  std::string refkey_parameter_name_;
  CNodePtr cnode_;
  std::vector<CNodePtr> cnodes_;
  int64_t used_devices_ = -1;
  // the repeated_calc_num_ will be inserted to the last dimension of dev matrix in default
  bool repeated_num_in_dev_matrix_right_ = true;
  // Whether the list of available strategies is exact or approximate
  bool is_strategy_cost_exact_ = true;
  bool self_define_shard_;
  bool use_shape_base_ = false;

  // for strategy propagation in auto parallel
  bool is_in_layout_propagation_ = false;

 private:
  OperatorCostPtr operator_cost_;
  std::vector<TypePtr> outputs_type_;
  int64_t swc_index_ = -1;
  std::map<int64_t, std::vector<Shape>> tensor_map_possibility;
  Status GetLayoutConfig();
  Status GetRepeatedNumInDevMatrixRight();
  Status CheckLayoutConfigBase();

  Status SetDevMatrixShapeByLayout();
  Status SetTensorMapByLayout();
  Status SetTensorMapBeforeByLayout();
  Status SetOutDevMatrixShapeByLayout();
  Status SetOutTensorMapByLayout();
  Status SetOutTensorMapBeforeByLayout();
};

Shape GetSliceShape(const Shape &tensor_shape, const Dimensions &strategy);
Status CheckStrategyValue(const StrategyPtr &strategy, const Shapes &inputs_shape, bool);
Operator CreateVirtualDivOp(int64_t div_num);
Operator CreateAllReduceOp(const std::string &reduce_op, const std::string &group);
Operator CreateReduceScatterOp(const std::string &reduce_op, const std::string &group);
Operator CreateAllGatherOp(const std::string &group);
Operator CreateCastOp(TypePtr type);
Operator CreateDivOp(float scale);
Operator CreateScalarDivOp(int64_t div_num);
Operator CreateScalarCastOp(TypePtr type);
Operator CreateScalarFloorDivOp(int64_t div_num);
Operator CreateScalarMulOp(int64_t scalar);
void AddCNodePrimAttr(const CNodePtr &comm_node, const std::string &attr_name, const ValuePtr &attr_val);
int32_t AddCommOpFusionType(const CNodePtr &comm_node, const AnfNodePtr &param_node);
Operator CreateMicroStepAllGatherOp(const std::string &group);
void AddCommOpMeanFlag(const CNodePtr &comm_node);
void AddCommOpParamFlag(const CNodePtr &comm_node);
Operator CreateGetTensorSliceOp(const TensorLayout &tensor_layout);
OperatorVector CreateMirrorOps(const std::string &group_name, size_t dev_num);
int64_t ComputeRepeatDeviceNumByTensorMap(const Shape &dev_matrix_shape, const Shape &tensor_map);
std::shared_ptr<Strategies> GenerateBatchStrategiesBySplitFlag(const Shapes &shapes,
                                                               const std::vector<bool> &split_flag_list);
std::string StrategyToString(const Strategies &strategy);
Status GenerateStrategiesForIndependentInputsBase(int64_t stage_id, size_t dev_num, const Shapes &inputs_shape,
                                                  const Shapes &splittable_inputs, std::vector<StrategyPtr> *sp_vector);
// generate strategies for that all inputs' dimensions are independent, such as: ([a, b, c, d])
Status GenerateStrategiesForIndependentInputs(int64_t stage_id, const Shapes &inputs_shape,
                                              const Shapes &splittable_inputs, std::vector<StrategyPtr> *sp_vector);
// generate strategies for that inputs' dimension maybe dependent
Status GenerateStrategiesForDependentInputs(int64_t stage_id, const Shapes &inputs_shape,
                                            const Shapes &splittable_inputs, std::vector<StrategyPtr> *sp);
// generate strategies for that have two inputs, and input0 or input1 maybe broadcast,
// and the corresponding dimensions that are not broadcast are all relevant dimensions
// such as: ([a, b, c, d], [a, b, c, d]) or ([b, c, d], [a, b, c, d]) or ([1, c, d], [a, b, c, d])
// or ([a, b, c, d], [b, c, d]) or ([a, b, c, d], [1, c, d])
// or ([a, 1], [1, b]) or ([a, b, c, d], [1, b, c, d]) or ([a, b, c, 1], [1, b, c, d])
Status GenerateStrategiesWithBroadcast(int64_t stage_id, const Shapes &inputs_shape, const Shapes &splittable_inputs,
                                       std::vector<StrategyPtr> *sp_vector);
std::vector<ValuePtr> GetValueSequence(const ValuePtr &sequence);
ValuePtr MakeListValue(const std::vector<int64_t> &v);
ValuePtr MakeTupleListValue(const Shapes &v);
AnfNodePtr CreateValueTupleAnfNodePtr(const std::vector<int64_t> &value_tuple);
AnfNodePtr CreateTensorTupleAnfNodePtr(const tensor::TensorPtrList &tensor_tuple);

ForwardOp CreateAllReduceMeanForwardOp(const Group &forward_group, const TypePtr &dtype);
Operator CreateDivOpWithType(float divisor, const TypePtr &dtype);
std::vector<int64_t> GetTensorValue(const ValuePtr &ori_value);

inline std::string GetPrimNameFromInfoName(const std::string &info_name) {
  auto prim_name = info_name;
  if (auto pos = info_name.rfind("Info"); pos != std::string::npos) {
    prim_name = info_name.substr(0, pos);
  }
  return prim_name;
}

template <typename T>
std::optional<T> GetScalarValueFromInputs(const std::vector<ValuePtr> &input_value, size_t idx) {
  if (idx == SIZE_MAX) {
    MS_EXCEPTION(ValueError) << "Index is the size max, target value maybe wrong!";
  }

  if (input_value.size() <= idx || input_value[idx] == nullptr) {
    return std::nullopt;
  }
  return GetScalarValue<T>(input_value[idx]);
}

template <typename T>
T GetInputValueFromCNode(const CNodePtr &cnode, size_t index) {
  MS_EXCEPTION_IF_NULL(cnode);
  auto inputs = cnode->inputs();
  if (index >= inputs.size()) {
    MS_LOG_WITH_NODE(EXCEPTION, cnode) << "The input index (" << index << ") is exceed of inputs size ("
                                       << inputs.size() << ").";
  }
  auto input_node = inputs[index];
  MS_EXCEPTION_IF_NULL(input_node);
  if (!input_node->isa<ValueNode>()) {
    MS_LOG_WITH_NODE(EXCEPTION, cnode) << "The input index (" << index << ") is not a value node.";
  }
  auto value_temp = input_node->cast<ValueNodePtr>();
  MS_EXCEPTION_IF_NULL(value_temp);
  auto value = value_temp->value();
  MS_EXCEPTION_IF_NULL(value);
  return GetValue<T>(value);
}

// Return default value if get value from input failed
template <typename T>
T GetInputValueFromCNodeWithDefaultValue(const CNodePtr &cnode, size_t index, T default_value) {
  MS_EXCEPTION_IF_NULL(cnode);
  auto inputs = cnode->inputs();
  if (index >= inputs.size()) {
    MS_LOG_WITH_NODE(DEBUG, cnode) << "The input index (" << index << ") is exceed of inputs size (" << inputs.size()
                                   << "). Return default value: " << default_value;
    return default_value;
  }
  auto input_node = inputs[index];
  MS_EXCEPTION_IF_NULL(input_node);
  if (!input_node->isa<ValueNode>()) {
    MS_LOG_WITH_NODE(DEBUG, cnode) << "The input index (" << index
                                   << ") is not a value node. Return default value: " << default_value;
    return default_value;
  }
  auto value_ptr = input_node->cast<ValueNodePtr>();
  MS_EXCEPTION_IF_NULL(value_ptr);
  auto value = value_ptr->value();
  MS_EXCEPTION_IF_NULL(value);
  return GetValue<T>(value);
}

template <typename T>
void SetValueInputToCNode(const CNodePtr &cnode, size_t index, T value) {
  MS_EXCEPTION_IF_NULL(cnode);
  auto inputs = cnode->inputs();
  if (index >= inputs.size()) {
    MS_LOG_WITH_NODE(EXCEPTION, cnode) << "The input index (" << index << ") is exceed of inputs size ("
                                       << inputs.size() << ").";
  }
  auto func_graph = cnode->func_graph();
  MS_EXCEPTION_IF_NULL(func_graph);
  auto manager = func_graph->manager();
  auto value_node = NewValueNode(MakeValue(value));
  MS_EXCEPTION_IF_NULL(value_node);
  manager->SetEdge(cnode, index, value_node);
}

template <typename T>
std::optional<T> GetScalarValueFromInputs(const std::vector<ValuePtr> &input_value, const std::string &op_name,
                                          const std::string &attr_name) {
  auto prim_name = GetPrimNameFromInfoName(op_name);
  auto idx = ops::GetInputIndexByName(prim_name, attr_name);
  return GetScalarValueFromInputs<T>(input_value, idx);
}

template <typename T>
std::optional<std::vector<T>> GetArrayValueFromInputs(const std::vector<ValuePtr> &input_value, size_t idx) {
  if (idx == SIZE_MAX) {
    MS_EXCEPTION(ValueError) << "Index is the size max, target value maybe wrong!";
  }

  if (input_value.size() <= idx || input_value[idx] == nullptr) {
    return std::nullopt;
  }
  auto array_opt = GetArrayValue<T>(input_value[idx]);
  if (!array_opt.has_value() || array_opt.value().HasUnknownValue()) {
    return std::nullopt;
  }
  return array_opt.value().ToVector();
}

template <typename T>
std::optional<std::vector<T>> GetArrayValueFromInputs(const std::vector<ValuePtr> &input_value,
                                                      const std::string &op_name, const std::string &attr_name) {
  auto prim_name = GetPrimNameFromInfoName(op_name);
  auto idx = ops::GetInputIndexByName(prim_name, attr_name);
  return GetArrayValueFromInputs<T>(input_value, idx);
}

template <typename T>
std::optional<std::vector<T>> GetArrayValueFromInputsWithCheck(const std::vector<ValuePtr> &input_value,
                                                               const std::string &op_name,
                                                               const std::string &attr_name) {
  auto attr_opt = GetArrayValueFromInputs<T>(input_value, op_name, attr_name);
  if (!attr_opt.has_value()) {
    MS_LOG(ERROR) << op_name << ": Don't have attribution " << attr_name;
    return std::nullopt;
  }
  return attr_opt;
}

template <typename T>
std::optional<T> GetScalarValueFromInputsWithCheck(const std::vector<ValuePtr> &input_value, const std::string &op_name,
                                                   const std::string &attr_name) {
  auto attr_opt = GetScalarValueFromInputs<T>(input_value, op_name, attr_name);
  if (!attr_opt.has_value()) {
    MS_LOG(ERROR) << op_name << ": Don't have attribution " << attr_name;
    return std::nullopt;
  }
  return attr_opt;
}

}  // namespace parallel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_OPERATOR_INFO_H_
