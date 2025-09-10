/**
 * Copyright 2024-2025 Huawei Technologies Co., Ltd
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
#ifndef MINDSPORE_CCSRC_BACKEND_BACKENDMANAGER_BACKEND_JIT_CONFIG_H
#define MINDSPORE_CCSRC_BACKEND_BACKENDMANAGER_BACKEND_JIT_CONFIG_H

#include <vector>
#include <string>
#include <map>
#include <nlohmann/json.hpp>
#include "utils/phase.h"
#include "backend/backend_manager/visible.h"

namespace mindspore {
namespace backend {
struct BackendJitConfig {
  // parse jit setting from PhaseManager::GetInstance().jit_config()
  static BackendJitConfig ParseBackendJitConfig() {
    BackendJitConfig backend_jit_config;

    const auto &jit_config = PhaseManager::GetInstance().jit_config();
    auto iter = jit_config.find("jit_level");
    if (iter != jit_config.end()) {
      backend_jit_config.jit_level = iter->second;
    }
    iter = jit_config.find("backend");
    if (iter != jit_config.end()) {
      backend_jit_config.backend = iter->second;
    }

    iter = jit_config.find("options");
    if (iter != jit_config.end()) {
      nlohmann::json options_json = nlohmann::json::parse(iter->second);
      if (options_json.contains("disable_format_transform")) {
        options_json["disable_format_transform"].get_to(backend_jit_config.disable_format_transform);
      }
      if (options_json.contains("exec_order")) {
        options_json["exec_order"].get_to(backend_jit_config.exec_order);
      }
      if (options_json.contains("ge_options")) {
        options_json["ge_options"].get_to(backend_jit_config.ge_options);
      }
    }

    return backend_jit_config;
  }

  nlohmann::json to_json() const {
    auto ret = nlohmann::json{{"jit_level", jit_level},
                              {"backend", backend},
                              {"disable_format_transform", disable_format_transform},
                              {"exec_order", exec_order},
                              {"ge_options", ge_options}};
    return ret;
  }

  void from_json(const nlohmann::json &j) {
    j.at("jit_level").get_to(jit_level);
    j.at("backend").get_to(backend);
    j.at("disable_format_transform").get_to(disable_format_transform);
    j.at("exec_order").get_to(exec_order);
    j.at("ge_options").get_to(ge_options);
  }

  // jit level, O0/O1
  std::string jit_level = "";
  // backend, ms_backend/GE, may not be set when using graphpipeline
  std::string backend = "";
  // Whether to disable the automatic format transform function from NCHW to NHWC
  bool disable_format_transform = false;
  // Sorting method for operator execution in KBK
  std::string exec_order = "";
  // GE options, {"graph":{option:value}, "session":{option:value}, "graph":{option:value}}
  std::map<std::string, std::map<std::string, std::string> > ge_options = {};
};
}  // namespace backend
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_BACKEND_BACKENDMANAGER_BACKEND_JIT_CONFIG_H
