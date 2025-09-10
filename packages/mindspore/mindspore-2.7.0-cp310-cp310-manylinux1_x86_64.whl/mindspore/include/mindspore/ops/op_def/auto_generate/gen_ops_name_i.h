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
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceRemainderTensorScalar = "InplaceRemainderTensorScalar";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInplaceBernoulliTensor = "InplaceBernoulliTensor";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameInplaceSiLU = "InplaceSiLU";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceBernoulliScalar = "InplaceBernoulliScalar";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameInplaceMatmulAdd = "InplaceMatmulAdd";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameIndex = "Index";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInnerMoeTokenUnpermute = "InnerMoeTokenUnpermute";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceRemainderTensorTensor = "InplaceRemainderTensorTensor";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInplaceExponential = "InplaceExponential";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
