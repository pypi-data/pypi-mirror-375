/**
 * Copyright 2023-2025 Huawei Technologies Co., Ltd
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
#ifndef MINDSPORE_CORE_OP_NAME_D_H_
#define MINDSPORE_CORE_OP_NAME_D_H_

namespace mindspore::ops {
constexpr auto kNameDiagonalView = "DiagonalView";
constexpr auto kNameDistCommGather = "DistCommGather";
constexpr auto kNameDistCommIsend = "DistCommIsend";
constexpr auto kNameDivMods = "DivMods";
constexpr auto kNameDropoutGradExt = "DropoutGradExt";
constexpr auto kNameDistCommAllGatherIntoTensor = "DistCommAllGatherIntoTensor";
constexpr auto kNameDistCommAllReduce = "DistCommAllReduce";
constexpr auto kNameDistCommBarrier = "DistCommBarrier";
constexpr auto kNameDCT = "DCT";
constexpr auto kNameDistCommAllGatherIntoTensorUneven = "DistCommAllGatherIntoTensorUneven";
constexpr auto kNameDCTN = "DCTN";
constexpr auto kNameDistCommReduce = "DistCommReduce";
constexpr auto kNameDistCommAllGather = "DistCommAllGather";
constexpr auto kNameDiagonal = "Diagonal";
constexpr auto kNameDivMod = "DivMod";
constexpr auto kNameDistCommReduceScatterTensor = "DistCommReduceScatterTensor";
constexpr auto kNameDense = "Dense";
constexpr auto kNameDistCommIrecv = "DistCommIrecv";
constexpr auto kNameDistCommAllToAllV = "DistCommAllToAllV";
constexpr auto kNameDiagExt = "DiagExt";
constexpr auto kNameDot = "Dot";
constexpr auto kNameDistCommAllToAllVSingle = "DistCommAllToAllVSingle";
constexpr auto kNameDropout = "Dropout";
constexpr auto kNameDistCommGatherIntoTensor = "DistCommGatherIntoTensor";
constexpr auto kNameDropoutExt = "DropoutExt";
constexpr auto kNameDistCommScatter = "DistCommScatter";
constexpr auto kNameDistCommBroadcast = "DistCommBroadcast";
constexpr auto kNameDistCommBatchIsendIrecv = "DistCommBatchIsendIrecv";
constexpr auto kNameDistCommReduceScatter = "DistCommReduceScatter";
constexpr auto kNameDiv = "Div";
constexpr auto kNameDiag = "Diag";
constexpr auto kNameDivs = "Divs";
constexpr auto kNameDistCommReduceScatterTensorUneven = "DistCommReduceScatterTensorUneven";
constexpr auto kNameDropoutDoMaskExt = "DropoutDoMaskExt";
constexpr auto kNameDistCommScatterTensor = "DistCommScatterTensor";
constexpr auto kNameDumpGradient = "DumpGradient";
constexpr auto kNameDropoutGenMaskExt = "DropoutGenMaskExt";
constexpr auto kNameDynamicQuantExt = "DynamicQuantExt";
constexpr auto kNameDynamicNTK = "DynamicNTK";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_D_H_
