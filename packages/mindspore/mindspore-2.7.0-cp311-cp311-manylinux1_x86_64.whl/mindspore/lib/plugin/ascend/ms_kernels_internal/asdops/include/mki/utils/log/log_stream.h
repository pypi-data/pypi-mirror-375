/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef MKI_UTILS_LOG_LOG_STREAM_H
#define MKI_UTILS_LOG_LOG_STREAM_H
#include <sstream>
#include "mki/utils/log/log_entity.h"

namespace Mki {
class LogStream {
public:
    LogStream(const char *filePath, int line, const char *funcName, LogLevel level);
    ~LogStream();
    template <typename T> LogStream &operator<<(const T &value)
    {
        stream_ << value;
        return *this;
    }
    void Format(const char *format, ...);

private:
    LogEntity logEntity_;
    bool useStream_ = true;
    std::ostringstream &stream_;
};
} // namespace Mki
#endif
