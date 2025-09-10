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
constexpr auto kNameDistCommAllGather = "DistCommAllGather";
constexpr auto kNameDistCommAllReduce = "DistCommAllReduce";
constexpr auto kNameDistCommAllGatherIntoTensorUneven = "DistCommAllGatherIntoTensorUneven";
constexpr auto kNameDense = "Dense";
constexpr auto kNameDistCommAllGatherIntoTensor = "DistCommAllGatherIntoTensor";
constexpr auto kNameDropout = "Dropout";
constexpr auto kNameDiag = "Diag";
constexpr auto kNameDistCommScatterTensor = "DistCommScatterTensor";
constexpr auto kNameDumpGradient = "DumpGradient";
constexpr auto kNameDistCommGather = "DistCommGather";
constexpr auto kNameDistCommIsend = "DistCommIsend";
constexpr auto kNameDivMods = "DivMods";
constexpr auto kNameDistCommIrecv = "DistCommIrecv";
constexpr auto kNameDCT = "DCT";
constexpr auto kNameDropoutDoMaskExt = "DropoutDoMaskExt";
constexpr auto kNameDivMod = "DivMod";
constexpr auto kNameDistCommAllToAllVSingle = "DistCommAllToAllVSingle";
constexpr auto kNameDiagonalView = "DiagonalView";
constexpr auto kNameDropoutGradExt = "DropoutGradExt";
constexpr auto kNameDot = "Dot";
constexpr auto kNameDCTN = "DCTN";
constexpr auto kNameDiagExt = "DiagExt";
constexpr auto kNameDiagonal = "Diagonal";
constexpr auto kNameDropoutExt = "DropoutExt";
constexpr auto kNameDistCommReduceScatter = "DistCommReduceScatter";
constexpr auto kNameDistCommGatherIntoTensor = "DistCommGatherIntoTensor";
constexpr auto kNameDistCommAllToAllV = "DistCommAllToAllV";
constexpr auto kNameDivs = "Divs";
constexpr auto kNameDistCommBarrier = "DistCommBarrier";
constexpr auto kNameDistCommReduce = "DistCommReduce";
constexpr auto kNameDiv = "Div";
constexpr auto kNameDistCommReduceScatterTensor = "DistCommReduceScatterTensor";
constexpr auto kNameDistCommBatchIsendIrecv = "DistCommBatchIsendIrecv";
constexpr auto kNameDistCommScatter = "DistCommScatter";
constexpr auto kNameDistCommBroadcast = "DistCommBroadcast";
constexpr auto kNameDropoutGenMaskExt = "DropoutGenMaskExt";
constexpr auto kNameDistCommReduceScatterTensorUneven = "DistCommReduceScatterTensorUneven";
constexpr auto kNameDynamicQuantExt = "DynamicQuantExt";
constexpr auto kNameDynamicNTK = "DynamicNTK";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_D_H_
