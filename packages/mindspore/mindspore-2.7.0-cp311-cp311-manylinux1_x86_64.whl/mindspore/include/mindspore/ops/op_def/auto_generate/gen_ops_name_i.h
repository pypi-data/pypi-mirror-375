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
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInplaceRemainderTensorScalar = "InplaceRemainderTensorScalar";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInplaceBernoulliScalar = "InplaceBernoulliScalar";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInplaceRemainderTensorTensor = "InplaceRemainderTensorTensor";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameInplaceBernoulliTensor = "InplaceBernoulliTensor";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
