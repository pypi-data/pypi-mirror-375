/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef MKI_UTILS_SHARE_MEMORY_SHARE_MEMORY_H
#define MKI_UTILS_SHARE_MEMORY_SHARE_MEMORY_H

#include <semaphore.h>
#include <iostream>

namespace Mki {
class ShareMemory {
public:
    ShareMemory(const std::string &name, uint32_t size);
    ~ShareMemory();
    ShareMemory(const ShareMemory &other) = delete;
    ShareMemory &operator=(const ShareMemory &other) = delete;
    void *GetShm();
    void SemLock() const;
    void SemUnLock() const;

private:
    void *CreateShareMemory(const std::string &name, uint32_t size);
    void CleanUpShm();
    void CleanUpSem();

private:
    std::string fullName_;
    sem_t *sem_ = nullptr;
    uint8_t *shareMemory_ = nullptr;
    uint32_t memSize_ = 0;
    int shmid_ = -1;
};
}

#endif
