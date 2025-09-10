/**
 * Copyright 2024 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_MINDSPORE_CCSRC_PYBIND_API_IR_TENSOR_API_H_
#define MINDSPORE_MINDSPORE_CCSRC_PYBIND_API_IR_TENSOR_API_H_
#include "pybind11/pybind11.h"

namespace py = pybind11;
namespace mindspore {
namespace tensor {

py::object TensorMethodSinh(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLog(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSubtract(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodBitwiseOr(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodRoll(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAllclose(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodModMagic(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodDiv_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLogicalAnd(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodNansum(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodIsinf(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodPut_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodIsfinite(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodProd(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAtan2(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSquare(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodChunk(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAtan(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodEq(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodArgmax(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodUnbind(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSub_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodErf(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLogaddexp2(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLerp(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodExpandAs(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSub(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAcos(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLogicalOr(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodFrac(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAcosh(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodGreaterEqual(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodOuter(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodRemainder_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMaskedScatter(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodXlogy(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodIsneginf(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodKthvalue(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodIndexAdd(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLog_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodUnique(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodArgsort(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodDiv(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodReciprocal(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLess(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMedian(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAtanh(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAddcdiv(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodGather(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodExp_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAdd(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodNewEmpty(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodNanToNum(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodBitwiseNot(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodIsclose(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLogicalXor(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodWhere(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMin(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodBitwiseXor(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodNewFull(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodGcd(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodNarrow(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodCopy_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodFillDiagonal_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodPow(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTrueDivide(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTanh(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMm(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLessEqual(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLog1p(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodExp(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLogaddexp(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodStd(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodCumsum(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodFill_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodCeil(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodRepeatInterleave(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodClamp(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodHardshrink(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodExpm1(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTril(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodFloorDivide_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAll(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodNewOnes(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSqrt(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodBitwiseAnd(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTopk(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSort(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAdd_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMul_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodCountNonzero(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSplit(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAddbmm(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodReshape(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodGreater(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTile(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTo(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodRound(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodFloor(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSigmoid(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodFlatten(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLogicalNot(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodDot(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodNotEqual(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSum(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodHistc(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMaximum(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodBincount(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodRemainder(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTan(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodViewAs(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTranspose(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAsin(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMaskedFill_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMaskedFill(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodScatter(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodCos(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTrunc(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLogsumexp(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodRepeat(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodScatter_(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodScatterAdd(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTake(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAsinh(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTriu(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAddmv(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodErfc(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodT(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAddmm(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodCosh(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodIndexSelect(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSinc(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLog10(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSelect(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMax(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMul(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMinimum(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodVar(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodNeg(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodLog2(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodSin(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodClone(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodRsqrt(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMaskedSelect(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodArgmin(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAbs(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodDiag(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodAny(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodInverse(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodBaddbmm(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodUnsqueeze(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodFloorDivide(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodNewZeros(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMatmul(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodTypeAs(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodMean(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);
py::object TensorMethodFmod(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);

}  // namespace tensor
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_PYBIND_API_IR_TENSOR_API_H_