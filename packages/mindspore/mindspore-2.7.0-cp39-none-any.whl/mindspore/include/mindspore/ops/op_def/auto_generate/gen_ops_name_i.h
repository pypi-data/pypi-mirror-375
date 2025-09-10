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
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInplaceBernoulliTensor = "InplaceBernoulliTensor";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInplaceRemainderTensorScalar = "InplaceRemainderTensorScalar";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInplaceRemainderTensorTensor = "InplaceRemainderTensorTensor";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInplaceBernoulliScalar = "InplaceBernoulliScalar";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
