/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef ATB_OPERATION_H
#define ATB_OPERATION_H
#include <cstdint>
#include <functional>
#include <string>
#include "atb/types.h"
#include "atb/svector.h"
#include "atb/context.h"

//!
//! \file operation.h
//!
//! \brief 定义加速库Operation类
//!

namespace atb {

//!
//! \class Operation.
//!
//! \brief 加速库Operation类.
//!
//! 该接口类定义了算子准备与执行的需要的一系列的接口，通过创建Operation可以执行算子
//!
class Operation {
public:
    //! \brief 默认构造函数.
    Operation() = default;

    //! \brief 默认析构函数.
    virtual ~Operation() = default;
    //!
    //! \brief 获取创建的Operation的名字
    //!
    //! \return 返回字符串
    //!
    virtual std::string GetName() const = 0;

    //!
    //! \brief 根据输入Tensor描述信息推导出输出Tensor的描述信息。
    //!
    //! \param inTensorDescs 存放所有输入tensor描述信息的SVector
    //! \param outTensorDescs 存放所有输出tensor描述信息的SVector
    //!
    //! \return 状态值，如果成功，返回NO_ERROR
    //!
    virtual Status InferShape(const SVector<TensorDesc> &inTensorDescs, SVector<TensorDesc> &outTensorDescs) const = 0;

    //!
    //! \brief 获取Op/GraphOp输入Tensor个数接口。
    //!
    //! \return 整数值
    //!
    virtual uint32_t GetInputNum() const = 0;

    //!
    //! \brief 获取Op/GraphOp输出Tensor个数接口。
    //!
    //! \return 整数值
    //!
    virtual uint32_t GetOutputNum() const = 0;

    //!
    //! \brief Operation执行前的一系列准备工作
    //!
    //! 主要是计算Operation执行过程需要分配的内存空间workspaceSize
    //!
    //! \param variantPack 输入与输出Tensor
    //! \param workspaceSize 获取Operation执行需要分配的内存空间
    //! \param context Operation执行准备工作所在的上下文
    //!
    //! \return 状态值，如果成功，返回NO_ERROR
    //!
    virtual Status Setup(const VariantPack &variantPack, uint64_t &workspaceSize, Context *context) = 0;

    //!
    //! \brief Operation执行的流程
    //!
    //! 根据setup过程中得到的workspaceSize为Operation执行分配实际的内存，并执行Operation
    //!
    //! \param variantPack 输入与输出Tensor
    //! \param workspace Operation执行分配的内存地址
    //! \param workspaceSize Operation执行需要分配的内存空间
    //! \param context Operation执行所在的上下文
    //!
    //! \return 状态值，如果成功，返回NO_ERROR
    //!
    virtual Status Execute(const VariantPack &variantPack, uint8_t *workspace, uint64_t workspaceSize,
                           Context *context) = 0;
};

//!
//! \brief 创建Operation
//!
//! \param opParam 根据参数来指定调用的Operation
//! \param operation Operation指针地址
//!
//! \return 状态值，如果成功，返回NO_ERROR
//!
template <typename OpParam> Status CreateOperation(const OpParam &opParam, Operation **operation);

//!
//! \brief 销毁Operation
//!
//! \param operation Operation指针
//!
//! \return 状态值，如果成功，返回NO_ERROR
//!
//! \note 调用CreateOperation接口创建Operation，执行完Operation后需要调用DestroyOperation接口进行销毁。否则将导致内存泄漏。
//!
Status DestroyOperation(Operation *operation);

//!
//! \brief 拷贝Operation的Param参数
//!
//! \param operation Operation指针
//! \param opParam OpParam的引用，将返回operation的opParam浅拷贝
//!
//! \return 状态值，如果成功，返回NO_ERROR
//!
template <typename OpParam> Status CloneOperationParam(const Operation *operation, OpParam &opParam);

//!
//! \brief 更新Operation的Param参数
//!
//! \param operation Operation指针
//! \param opParam Operation新的param值
//!
//! \return 状态值，如果成功，返回NO_ERROR
//!
template <typename OpParam> Status UpdateOperationParam(Operation *operation, const OpParam &opParam);

//!
//! \brief 设置Operation使用的streamId
//!
//! \param operation 被设置的Operation指针
//! \param streamId 需要设置的streamId
//!
//! \return 状态值，如果成功，返回NO_ERROR
//!
Status SetExecuteStreamId(Operation *operation, uint32_t streamId);

//!
//! \brief 获取Operation使用的streamId
//!
//! \param operation 需要获取的streamId的Operation指针
//!
//! \return 该Operation当前使用的streamId
//!
uint32_t GetExecuteStreamId(Operation *operation);
} // namespace atb
#endif