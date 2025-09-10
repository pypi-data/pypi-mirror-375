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
#ifndef MINDSPORE_CORE_OP_NAME_I_H_
#define MINDSPORE_CORE_OP_NAME_I_H_

namespace mindspore::ops {
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInplaceRemainderTensorTensor = "InplaceRemainderTensorTensor";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInplaceRemainderTensorScalar = "InplaceRemainderTensorScalar";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameInplaceBernoulliTensor = "InplaceBernoulliTensor";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInplaceBernoulliScalar = "InplaceBernoulliScalar";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
