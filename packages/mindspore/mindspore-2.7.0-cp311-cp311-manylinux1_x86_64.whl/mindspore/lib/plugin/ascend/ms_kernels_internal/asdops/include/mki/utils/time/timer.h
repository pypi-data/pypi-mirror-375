/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef MKI_UTILS_TIME_TIMER_H
#define MKI_UTILS_TIME_TIMER_H
#include <cstdint>

namespace Mki {
class Timer {
public:
    Timer();
    ~Timer();
    uint64_t ElapsedMicroSecond();
    void Reset();

private:
    uint64_t GetCurrentTimepoint() const;

private:
    uint64_t startTimepoint_ = 0;
};
} // namespace Mki
#endif
