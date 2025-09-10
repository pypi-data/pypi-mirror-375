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
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInplaceBernoulliScalar = "InplaceBernoulliScalar";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameInplaceRemainderTensorScalar = "InplaceRemainderTensorScalar";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceBernoulliTensor = "InplaceBernoulliTensor";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInplaceRemainderTensorTensor = "InplaceRemainderTensorTensor";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
