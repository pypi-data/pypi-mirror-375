/**
 * Copyright 2020-2024 Huawei Technologies Co., Ltd
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
#ifndef MINDSPORE_TENSOR_SUMMARY_H
#define MINDSPORE_TENSOR_SUMMARY_H

#include <vector>
#include <tuple>
#include <memory>
#include <string>

#include "utils/hash_map.h"
#include "debug/debug_services.h"

namespace mindspore {
class MeanCalculator {
 public:
  MeanCalculator();
  ~MeanCalculator() = default;
  void ProcessElement(double value);
  double GetMean() const;

 protected:
  double mean;
  int count;
};

class L2Calculator {
 public:
  L2Calculator() : squre_sum(0.0) {}
  ~L2Calculator() = default;
  void ProcessElement(double value);
  void ProcessElement(const L2Calculator &other);
  double GetL2Value() const;

 private:
  // save (x^2 + y^2)/y^2, when y > x, to avoid itermidiate value overflow
  // the true l2 value should be sqrt(squre_sum_div_max_ * max_value_^2)
  double squre_sum;
};

class ITensorSummary {
 public:
  virtual ~ITensorSummary() = default;
  virtual void TensorStatistics(DbgDataType dtype_value) = 0;
  virtual const bool is_bool() const = 0;
  virtual const double max_value() const = 0;
  virtual const double min_value() const = 0;
  virtual const double avg_value() const = 0;
  virtual const double l2_value() const = 0;

  virtual const uint64_t count() const = 0;
  virtual const uint64_t neg_zero_count() const = 0;
  virtual const uint64_t pos_zero_count() const = 0;
  virtual const uint64_t nan_count() const = 0;
  virtual const uint64_t neg_inf_count() const = 0;
  virtual const uint64_t pos_inf_count() const = 0;
  virtual const uint64_t zero_count() const = 0;
};

template <typename T>
class TensorSummary : public ITensorSummary {
 public:
  TensorSummary() = default;
  ~TensorSummary() override = default;
  TensorSummary(const void *current_tensor_ptr, const void *const previous_tensor_ptr, uint64_t num_elements,
                uint64_t prev_num_elements);
  void TensorStatistics(DbgDataType dtype_value) override;
  const bool is_bool() const override { return is_bool_; }
  const double max_value() const override { return max_; }
  const double min_value() const override { return min_; }
  const double avg_value() const override { return avg_; }
  const uint64_t count() const override { return num_elements_; }
  const uint64_t neg_zero_count() const override { return neg_zero_count_; }
  const uint64_t pos_zero_count() const override { return pos_zero_count_; }
  const uint64_t nan_count() const override { return nan_count_; }
  const uint64_t neg_inf_count() const override { return neg_inf_count_; }
  const uint64_t pos_inf_count() const override { return pos_inf_count_; }
  const uint64_t zero_count() const override { return zero_count_; }
  const double l2_value() const override { return l2_calc_.GetL2Value(); }

 private:
  const T *current_tensor_ptr_;
  const T *prev_tensor_ptr_;
  uint64_t num_elements_;
  uint64_t prev_num_elements_;
  double min_;
  double max_;
  double avg_;
  bool is_bool_;
  uint64_t neg_zero_count_;
  uint64_t pos_zero_count_;
  uint64_t pos_inf_count_;
  uint64_t neg_inf_count_;
  uint64_t inf_count_;
  uint64_t nan_count_;
  uint64_t zero_count_;
  L2Calculator l2_calc_;
  void TensorStatisticsSingleThread();
};
}  // namespace mindspore
#endif  // MINDSPORE_TENSOR_SUMMARY_H
