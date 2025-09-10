/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef ATBOPS_PARAMS_PAD_WITH_HIDDEN_STATE_H
#define ATBOPS_PARAMS_PAD_WITH_HIDDEN_STATE_H

#include <cstdint>
#include <string>
#include <sstream>
#include <vector>
#include "mki/utils/compare/compare.h"

namespace AtbOps {
namespace OpParam {
struct PadWithHiddenState {
    std::vector<int32_t> qSeqLen;
    uint32_t maxSeqLen = 0;

    bool operator==(const PadWithHiddenState &other) const
    {
        return this->qSeqLen == other.qSeqLen && this->maxSeqLen == other.maxSeqLen;
    }
};
} // namespace OpParam
} // namespace AtbOps

#endif // ATBOPS_PARAMS_PAD_WITH_HIDDEN_STATE_H