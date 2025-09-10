/**
 * Copyright 2025 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_BACKEND_GEBACKEND_RUNTIME_ACTOR_CONTROLFLOW_ENTRANCE_ACTOR_H_
#define MINDSPORE_CCSRC_BACKEND_GEBACKEND_RUNTIME_ACTOR_CONTROLFLOW_ENTRANCE_ACTOR_H_

#include <vector>
#include <string>
#include <memory>
#include <stack>
#include <queue>
#include <set>
#include <algorithm>
#include "utils/hash_map.h"
#include "backend/ge_backend/runtime/actor/actor_common.h"
#include "backend/ge_backend/runtime/actor/control_flow/control_actor.h"

namespace mindspore {
namespace ge_backend {
namespace runtime {
// Entrance actor is used in the control flow to receive a set of result arrow and a branch id and then send
// the data to the corresponding actor. It is the entry point for subgraph execution.
class EntranceActor : public ControlActor {
 public:
  EntranceActor(const std::string &name, const AID &memory_manager_aid, const std::vector<KernelWithIndex> &parameters,
                const std::set<KernelWithIndex> &call_nodes, const AnfNodePtr &node)
      : ControlActor(name, KernelTransformType::kEntranceActor, memory_manager_aid, parameters, node),
        call_nodes_(call_nodes) {
    input_kernel_tensors_.resize(parameters.size());
  }
  ~EntranceActor() override = default;

  void RunOpControl(AID *const input_control, OpContext<KernelTensor> *const context) override;

  void RunOpRealParameterWithBranchID(const OpRealParameterWithBranchID &real_parameter_with_branch_id,
                                      OpContext<KernelTensor> *const context);

  void SendMemoryFreeReq(OpContext<KernelTensor> *const context) override;

  // Clear the data which are generated in the loop body execution.
  void ClearDataOnStepEnd(AID *const input_control, OpContext<KernelTensor> *const context);

  const std::vector<AID> &loop_body_input_control_arrow_aids() const { return loop_body_input_control_arrow_aids_; }

 protected:
  void Run(OpContext<KernelTensor> *const context) override;
  void FetchInput(OpContext<KernelTensor> *const context) override;
  bool CheckRunningCondition(const OpContext<KernelTensor> *context) const override;
  void EraseInput(const OpContext<KernelTensor> *const context) override;

 private:
  friend class ControlNodeScheduler;
  friend class SchedulerHelper;

  // Indicate whether the entrance actor is the execution of loop body. In the control flow, the subgraph can be
  // triggered to execute in two ways: one is the begin execution of step, another is the execution of loop body.
  // The input controls are different in the two ways.
  bool is_loop_body_execution_{false};
  // The dependent of loop body input actors.
  mindspore::HashMap<int, std::vector<AID *>> loop_body_input_op_controls_;
  std::vector<AID> loop_body_input_control_arrow_aids_;
  size_t loop_body_input_controls_nums_{0};

  // Input data with branch id.
  mindspore::HashMap<int, std::queue<OpRealParameterWithBranchID>> real_parameters_with_branch_id_;

  // Call nodes are used to record the caller of the subgraph, and are used to connect the data arrow
  // and branch id arrow in the link process.
  std::set<KernelWithIndex> call_nodes_;
};

using EntranceActorPtr = std::shared_ptr<EntranceActor>;
}  // namespace runtime
}  // namespace ge_backend
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_BACKEND_GEBACKEND_RUNTIME_ACTOR_CONTROLFLOW_ENTRANCE_ACTOR_H_
