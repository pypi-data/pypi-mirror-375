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

#ifndef MINDSPORE_CCSRC_DISTRIBUTED_TCP_STORE_H_
#define MINDSPORE_CCSRC_DISTRIBUTED_TCP_STORE_H_

#include <string>
#include <memory>
#include <vector>
#if defined(__linux__) && defined(WITH_BACKEND)
#include "include/backend/distributed/cluster/cluster_context.h"
#include "include/backend/distributed/cluster/topology/compute_graph_node.h"
#else
#include "include/backend/distributed/cluster/dummy_cluster_context.h"
#endif
#include "pybind11/pybind11.h"
namespace py = pybind11;

namespace mindspore {
namespace distributed {
namespace cluster {
class BACKEND_EXPORT TCPStoreClient {
 public:
  TCPStoreClient();
  ~TCPStoreClient();
  static std::shared_ptr<TCPStoreClient> instance();

  // Get the rank id of this process in the specified group.
  py::bytes GetKey(const std::string &key);

  // Get the size of the specified group.
  void SetKey(const std::string &key, const std::string &value);

  bool DeleteKey(const std::string &key);
};

}  // namespace cluster
}  // namespace distributed
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_DISTRIBUTED_TCP_STORE_H_
