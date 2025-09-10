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
#ifndef MINDSPORE_CORE_INCLUDE_UTILS_DISTRIBUTED_META_H_
#define MINDSPORE_CORE_INCLUDE_UTILS_DISTRIBUTED_META_H_

#include <memory>
#include <string>
#include <map>
#include "mindapi/base/macros.h"

namespace mindspore {
class MS_CORE_API DistributedMeta {
 public:
  DistributedMeta() = default;
  ~DistributedMeta() = default;
  DistributedMeta(const DistributedMeta &) = delete;
  DistributedMeta &operator=(const DistributedMeta &) = delete;
  static std::shared_ptr<DistributedMeta> GetInstance();

  void set_initialized() { inited_ = true; }
  bool initialized() const { return inited_; }

  void set_global_rank_id(uint32_t rank_id) { global_rank_id_ = rank_id; }
  uint32_t global_rank_id() const { return global_rank_id_; }

  void set_global_rank_size(uint32_t rank_size) { global_rank_size_ = rank_size; }
  uint32_t global_rank_size() const { return global_rank_size_; }

  void set_local_rank_id(uint32_t rank_id) { local_rank_id_ = rank_id; }
  uint32_t local_rank_id() const { return local_rank_id_; }

  void set_local_rank_size(uint32_t rank_size) { local_rank_size_ = rank_size; }
  uint32_t local_rank_size() const { return local_rank_size_; }

  // Set whether enable cross cluster communication.
  void set_enable_cross_cluster(bool enable_cross_cluster) { enable_cross_cluster_ = enable_cross_cluster; }
  // Return whether enable cross cluster communication.
  bool enable_cross_cluster() const { return enable_cross_cluster_; }

 private:
  static std::shared_ptr<DistributedMeta> instance_;
  bool inited_{false};
  uint32_t global_rank_id_{0};
  uint32_t global_rank_size_{1};
  uint32_t local_rank_id_{0};
  uint32_t local_rank_size_{1};
  // Indicate whether enable cross cluster communication.
  bool enable_cross_cluster_{false};
};
}  // namespace mindspore
#endif  // MINDSPORE_CORE_INCLUDE_UTILS_DISTRIBUTED_META_H_
