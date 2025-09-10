/**
 * Copyright 2023 Huawei Technologies Co., Ltd
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
#ifndef MINDSPORE_CCSRC_MINDDATA_DATASET_KERNELS_IMAGE_DVPP_UTILS_DVPP_IMAGE_UTILS_H_
#define MINDSPORE_CCSRC_MINDDATA_DATASET_KERNELS_IMAGE_DVPP_UTILS_DVPP_IMAGE_UTILS_H_

#include <csetjmp>

#include <cmath>
#include <memory>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>
#if defined(_WIN32) || defined(_WIN64)
#undef HAVE_STDDEF_H
#undef HAVE_STDLIB_H
#elif __APPLE__
#include <sys/param.h>
#include <sys/mount.h>
#endif
#include "minddata/dataset/core/tensor.h"
#include "minddata/dataset/kernels/tensor_op.h"
#include "minddata/dataset/util/status.h"
#include "minddata/dataset/util/validators.h"
#include "minddata/dataset/kernels/image/dvpp/utils/ErrorCode.h"

#include "acldvppop/acldvpp_base.h"

namespace mindspore {
namespace dataset {
const int kInvalidInterpolationMode = 100;
const int kInvalidPaddingMode = 101;
const int kInvalidRotateMode = 102;
const int kInvalidConvertMode = 103;

APP_ERROR GetDVPPConvertMode(ConvertMode convertMode, acldvppConvertMode *dvpp_mode);

/// \brief Convert ConvertMode to dvpp mode
inline int GetDVPPConvertMode(ConvertMode convertMode) {
  switch (convertMode) {
    case ConvertMode::COLOR_BGR2BGRA:              // COLOR_BGR2BGRA=COLOR_RGB2RGBA
      return acldvppConvertMode::COLOR_BGR2BGRA;   // dvpp alpha channel COLOR_BGR2BGRA/COLOR_RGB2RGBA
    case ConvertMode::COLOR_BGRA2BGR:              // COLOR_BGRA2BGR=COLOR_RGBA2RGB
      return acldvppConvertMode::COLOR_BGRA2BGR;   // dvpp alpha channel COLOR_BGRA2BGR/COLOR_RGBA2RGB
    case ConvertMode::COLOR_BGR2RGBA:              // COLOR_BGR2RGBA=COLOR_RGB2BGRA
      return acldvppConvertMode::COLOR_BGR2RGBA;   // dvpp COLOR_BGR2RGBA/COLOR_RGB2BGRA
    case ConvertMode::COLOR_RGBA2BGR:              // COLOR_RGBA2BGR=COLOR_BGRA2RGB
      return acldvppConvertMode::COLOR_RGBA2BGR;   // dvpp COLOR_RGBA2BGR/COLOR_BGRA2RGB
    case ConvertMode::COLOR_BGR2RGB:               // COLOR_BGR2RGB=COLOR_RGB2BGR
      return acldvppConvertMode::COLOR_BGR2RGB;    // dvpp COLOR_BGR2RGB/COLOR_RGB2BGR
    case ConvertMode::COLOR_BGRA2RGBA:             // COLOR_BGRA2RGBA=COLOR_RGBA2BGRA
      return acldvppConvertMode::COLOR_BGRA2RGBA;  // dvpp COLOR_BGRA2RGBA/COLOR_RGBA2BGRA
    case ConvertMode::COLOR_BGR2GRAY:
      return acldvppConvertMode::COLOR_BGR2GRAY;  // dvpp COLOR_BGR2GRAY
    case ConvertMode::COLOR_RGB2GRAY:
      return acldvppConvertMode::COLOR_RGB2GRAY;   // dvpp COLOR_RGB2GRAY
    case ConvertMode::COLOR_GRAY2BGR:              // COLOR_GRAY2BGR=COLOR_GRAY2RGB
      return acldvppConvertMode::COLOR_GRAY2BGR;   // dvpp COLOR_GRAY2BGR/COLOR_GRAY2RGB
    case ConvertMode::COLOR_GRAY2BGRA:             // COLOR_GRAY2BGRA=COLOR_GRAY2RGBA
      return acldvppConvertMode::COLOR_GRAY2BGRA;  // dvpp COLOR_GRAY2BGRA/COLOR_GRAY2RGBA
    case ConvertMode::COLOR_BGRA2GRAY:
      return acldvppConvertMode::COLOR_BGRA2GRAY;  // dvpp COLOR_BGRA2GRAY
    case ConvertMode::COLOR_RGBA2GRAY:
      return acldvppConvertMode::COLOR_RGBA2GRAY;  // dvpp COLOR_RGBA2GRAY
    default:
      return kInvalidConvertMode;
  }
}

/// \brief Convert InterpolationMode to dvpp mode
inline int GetDVPPInterpolationMode(InterpolationMode mode) {
  switch (mode) {
    case InterpolationMode::kLinear:
      return 0;  // dvpp BILINEAR
    case InterpolationMode::kCubic:
      return 2;  // dvpp BICUBIC
    case InterpolationMode::kArea:
      return kInvalidInterpolationMode;
    case InterpolationMode::kNearestNeighbour:
      return 1;  // dvpp NEAREST
    default:
      return kInvalidInterpolationMode;
  }
}

/// \brief Convert Padding BorderType to dvpp mode
inline uint32_t GetDVPPPaddingMode(BorderType type) {
  switch (type) {
    case BorderType::kConstant:
      return 0;  // dvpp Constant
    case BorderType::kEdge:
      return 1;  // dvpp Edge
    case BorderType::kReflect:
      return 2;  // dvpp Reflect
    case BorderType::kSymmetric:
      return 3;  // dvpp Symmetric
    default:
      return kInvalidPaddingMode;
  }
}

/// \brief Convert Rotate InterpolationMode to dvpp mode
inline uint32_t GetDVPPRotateMode(InterpolationMode mode) {
  switch (mode) {
    case InterpolationMode::kLinear:
      return 0;  // dvpp BILINEAR
    case InterpolationMode::kNearestNeighbour:
      return 1;  // dvpp NEAREST
    default:
      return kInvalidRotateMode;
  }
}

inline Status CheckDvppLimit(int64_t input_h, int64_t input_w, int64_t h_lb, int64_t w_lb, int64_t h_ub, int64_t w_ub,
                             const std::string &op_name, const std::string &param_name = "input") {
  if ((input_h < h_lb || input_h > h_ub) || (input_w < w_lb || input_w > w_ub)) {
    auto error = op_name + ": the " + param_name + " shape should be from [" + std::to_string(h_lb) + ", " +
                 std::to_string(w_lb) + "] to [" + std::to_string(h_ub) + ", " + std::to_string(w_ub) + "], but got [" +
                 std::to_string(input_h) + ", " + std::to_string(input_w) + "].";
    RETURN_STATUS_UNEXPECTED(error);
  }
  return Status::OK();
}

/// \brief Returns image with adjusting brightness.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Augmented image Tensor of same input shape (type DE_FLOAT32 or DE_UINT8).
/// \param factor: brightness factor.
APP_ERROR DvppAdjustBrightness(const std::shared_ptr<DeviceTensorAscend910B> &input,
                               std::shared_ptr<DeviceTensorAscend910B> *output, float factor);

/// \brief Returns image with adjusting contrast.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Augmented image Tensor of same input shape (type DE_FLOAT32 or DE_UINT8).
/// \param factor: contrast factor.
APP_ERROR DvppAdjustContrast(const std::shared_ptr<DeviceTensorAscend910B> &input,
                             std::shared_ptr<DeviceTensorAscend910B> *output, float factor);

/// \brief Returns image with adjusting hue.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Augmented image Tensor of same input shape (type DE_FLOAT32 or DE_UINT8).
/// \param factor: hue factor.
APP_ERROR DvppAdjustHue(const std::shared_ptr<DeviceTensorAscend910B> &input,
                        std::shared_ptr<DeviceTensorAscend910B> *output, float factor);

/// \brief Returns image with adjusting saturation.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Augmented image Tensor of same input shape (type DE_FLOAT32 or DE_UINT8).
/// \param factor: saturation factor.
APP_ERROR DvppAdjustSaturation(const std::shared_ptr<DeviceTensorAscend910B> &input,
                               std::shared_ptr<DeviceTensorAscend910B> *output, float factor);

/// \brief Returns image with adjusting sharpness.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Augmented image Tensor of same input shape (type DE_FLOAT32 or DE_UINT8).
/// \param factor: sharpness factor.
APP_ERROR DvppAdjustSharpness(const std::shared_ptr<DeviceTensorAscend910B> &input,
                              std::shared_ptr<DeviceTensorAscend910B> *output, float factor);

/// \brief Returns transformed image with affine matrix.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Transformed image Tensor (type DE_FLOAT32 or DE_UINT8).
/// \param matrix: affine matrix.
/// \param interpolation_mode: the mode of interpolation.
/// \param padding_mode: the mode of padding.
/// \param fill: fill value for color channel.
APP_ERROR DvppAffine(const std::shared_ptr<DeviceTensorAscend910B> &input,
                     std::shared_ptr<DeviceTensorAscend910B> *output, const std::vector<float> &matrix,
                     uint32_t interpolation_mode, uint32_t padding_mode, const std::vector<float> &fill);

/// \brief Returns image with contrast maximized.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Transformed image Tensor (type DE_FLOAT32 or DE_UINT8).
/// \param cutoff: cutoff percentage of how many pixels are to be removed from the high and low ends of the histogram.
/// \param ignore: pixel values to be ignored in the algorithm.
APP_ERROR DvppAutoContrast(const std::shared_ptr<DeviceTensorAscend910B> &input,
                           std::shared_ptr<DeviceTensorAscend910B> *output, const std::vector<float> &cutoff,
                           const std::vector<uint32_t> &ignore);

/// \brief Returns Convertcolor image.
/// \param input: Tensor of shape <N,H,W,C>, c support [1, 3, 4], N only support 1.
/// \param output: Transformed image Tensor (type DE_FLOAT32 or DE_UINT8), c = [1, 3, 4].
/// \param convertMode: the ConvertMode mode.
APP_ERROR DvppConvertColor(const std::shared_ptr<DeviceTensorAscend910B> &input,
                           std::shared_ptr<DeviceTensorAscend910B> *output, ConvertMode convertMode);

/// \brief Returns croped image.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Croped image Tensor (type DE_FLOAT32 or DE_UINT8).
/// \param top: the vertical starting coordinate.
/// \param left: the horizontal starting coordinate.
/// \param height: the height of the crop box.
/// \param width: the width of the crop box.
APP_ERROR DvppCrop(const std::shared_ptr<DeviceTensorAscend910B> &input,
                   std::shared_ptr<DeviceTensorAscend910B> *output, uint32_t top, uint32_t left, uint32_t height,
                   uint32_t width);

/// \brief Returns Decoded image.
/// Supported images: JPEG JPG
/// \param input: input containing the not decoded image 1D bytes.
/// \param output: Decoded image Tensor of shape <H,W,C> and type DE_UINT8. Pixel order is RGB.
APP_ERROR DvppDecode(const std::shared_ptr<DeviceTensorAscend910B> &input,
                     std::shared_ptr<DeviceTensorAscend910B> *output);

/// \brief Returns equalized image.
/// \param input: Tensor of shape <N,H,W,C>, c == 1 or c == 3.
/// \param output: Equalized image Tensor (type DE_UINT8).
APP_ERROR DvppEqualize(const std::shared_ptr<DeviceTensorAscend910B> &input,
                       std::shared_ptr<DeviceTensorAscend910B> *output);
/// \brief Returns Erased image.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Erased image Tensor (type DE_FLOAT32 or DE_UINT8).
/// \param top: top of the cropped box.
/// \param left: left of the cropped box.
/// \param height: height of the cropped box.
/// \param width: width of the cropped box.
/// \param value: fill value for erase
APP_ERROR DvppErase(const std::shared_ptr<DeviceTensorAscend910B> &input,
                    std::shared_ptr<DeviceTensorAscend910B> *output, uint32_t top, uint32_t left, uint32_t height,
                    uint32_t width, const std::vector<float> &value);

/// \brief Blur input image with the specified Gaussian kernel.
/// \param input: input containing the not decoded image 1D bytes.
/// \param output: Blurred image Tensor (type DE_FLOAT32 or DE_UINT8).
/// \param kernel_size: The size of the Gaussian kernel.
/// \param sigma:  The standard deviation of the Gaussian kernel.
/// \param padding_mode: The method of padding.
APP_ERROR DvppGaussianBlur(const std::shared_ptr<DeviceTensorAscend910B> &input,
                           std::shared_ptr<DeviceTensorAscend910B> *output, const std::vector<int64_t> &kernel_size,
                           const std::vector<float> &sigma, uint32_t padding_mode);

/// \brief Returns horizontal flip image
/// \param input: Tensor of shape <N,H,W,C>, c == 1 or c == 3
/// \param output: Flipped image Tensor of same input shape (type DE_FLOAT32 or DE_UINT8)
APP_ERROR DvppHorizontalFlip(const std::shared_ptr<DeviceTensorAscend910B> &input,
                             std::shared_ptr<DeviceTensorAscend910B> *output);

/// \brief Returns invert image
/// \param input: Tensor of shape <N,H,W,C>, c == 1 or c == 3
/// \param output: Invert image Tensor of same input shape (type DE_FLOAT32 or DE_UINT8)
APP_ERROR DvppInvert(const std::shared_ptr<DeviceTensorAscend910B> &input,
                     std::shared_ptr<DeviceTensorAscend910B> *output);

/// \brief Returns Normalized image.
/// \param input: Tensor of shape <H,W,C> in RGB order.
/// \param output: Normalized image Tensor of same input shape and type DE_FLOAT32.
/// \param mean: Tensor of shape <3> and type DE_FLOAT32 which are mean of each channel in RGB order.
/// \param std:  Tensor of shape <3> and type DE_FLOAT32 which are std of each channel in RGB order.
/// \param is_hwc: Check if input is HWC/CHW format.
APP_ERROR DvppNormalize(const std::shared_ptr<DeviceTensorAscend910B> &input,
                        std::shared_ptr<DeviceTensorAscend910B> *output, std::vector<float> mean,
                        std::vector<float> std, bool is_hwc);

/// \brief Returns Padded image.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Padded image (type DE_FLOAT32 or DE_UINT8).
/// \param padding The number of pixels to pad each border of the image [left, top, right, bottom].
/// \param[in] padding_mode The method of padding.
/// \param[in] fill The pixel intensity of the borders.
APP_ERROR DvppPad(const std::shared_ptr<DeviceTensorAscend910B> &input, std::shared_ptr<DeviceTensorAscend910B> *output,
                  const std::vector<int64_t> &padding, uint32_t padding_mode, const std::vector<float> &fill);

/// \brief Returns Perspective image.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Transformed image Tensor of same input shape (type DE_FLOAT32 or DE_UINT8).
/// \param start_points List containing four lists of two integers corresponding to four
///     corners [top-left, top-right, bottom-right, bottom-left] of the original image.
/// \param[in] end_points List containing four lists of two integers corresponding to four
///     corners [top-left, top-right, bottom-right, bottom-left] of the transformed image.
/// \param[in] interpolation Method of interpolation, support linear and nearest-neighbor interpolation.
APP_ERROR DvppPerspective(const std::shared_ptr<DeviceTensorAscend910B> &input,
                          std::shared_ptr<DeviceTensorAscend910B> *output,
                          const std::vector<std::vector<int32_t>> &start_points,
                          const std::vector<std::vector<int32_t>> &end_points,
                          InterpolationMode interpolation = InterpolationMode::kLinear);

/// \brief Returns Padded image.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: Padded image (type DE_FLOAT32 or DE_UINT8).
APP_ERROR DvppPosterize(const std::shared_ptr<DeviceTensorAscend910B> &input,
                        std::shared_ptr<DeviceTensorAscend910B> *output, uint8_t bits);

/// \brief Returns Resized image.
/// \param input: Tensor of shape <N,H,W,C>, c == 1 or c == 3
/// \param output: Resized image of shape <H,outputHeight,outputWidth,C> and same type as input.
/// \param output_height: height of output.
/// \param output_width: width of output.
/// \param fx: horizontal scale.
/// \param fy: vertical scale.
/// \param InterpolationMode: the interpolation mode.
APP_ERROR DvppResize(const std::shared_ptr<DeviceTensorAscend910B> &input,
                     std::shared_ptr<DeviceTensorAscend910B> *output, int32_t output_height, int32_t output_width,
                     double fx = 0.0, double fy = 0.0, InterpolationMode mode = InterpolationMode::kLinear);

/// \brief Returns Crop and Resized image.
/// \param input: Tensor of shape <N,H,W,C>, c == 1 or c == 3.
/// \param output: Resized image of shape <H,outputHeight,outputWidth,C> and same type as input.
/// \param top: horizontal start point.
/// \param left: vertical start point.
/// \param height: height of the cropped ROI.
/// \param width: width of the cropped ROI.
/// \param output_height: height of output.
/// \param output_width: width of output.
/// \param mode: the interpolation mode.
APP_ERROR DvppResizedCrop(const std::shared_ptr<DeviceTensorAscend910B> &input,
                          std::shared_ptr<DeviceTensorAscend910B> *output, int32_t top, int32_t left, int32_t height,
                          int32_t width, int32_t output_height, int32_t output_width, InterpolationMode mode);

/// \brief Returns rotate image.
/// \param input: Tensor of shape <N,H,W,C>, c == 1 or c == 3
/// \param output: Rotate image Tensor (type DE_FLOAT32 or DE_UINT8).
APP_ERROR DvppRotate(const std::shared_ptr<DeviceTensorAscend910B> &input,
                     std::shared_ptr<DeviceTensorAscend910B> *output, float degrees, InterpolationMode mode,
                     bool expand, const std::vector<float> &center, const std::vector<float> &fill);

/// \brief Returns image with solarize.
/// \param input: Tensor of shape <H,W,C> format.
/// \param output: solarize image Tensor of same input shape (type DE_FLOAT32 or DE_UINT8).
/// \param factor: saturation factor.
APP_ERROR DvppSolarize(const std::shared_ptr<DeviceTensorAscend910B> &input,
                       std::shared_ptr<DeviceTensorAscend910B> *output, const std::vector<float> &threshold);

/// \brief Returns vertical flip image.
/// \param input: Tensor of shape <N,H,W,C>, c == 1 or c == 3
/// \param output: Flipped image Tensor of same input shape (type DE_FLOAT32 and DE_UINT8)
APP_ERROR DvppVerticalFlip(const std::shared_ptr<DeviceTensorAscend910B> &input,
                           std::shared_ptr<DeviceTensorAscend910B> *output);

APP_ERROR GetSocName(std::string *soc_name);

APP_ERROR CreateAclTensor(const int64_t *view_dims, uint64_t view_dims_num, mindspore::TypeId data_type,
                          const int64_t *stride, int64_t offset, const int64_t *storage_dims, uint64_t storage_dims_num,
                          void *tensor_data, bool is_hwc, void **acl_tensor);

APP_ERROR DestroyTensor(void *tensor);

APP_ERROR DestroyFloatArray(void *float_array);

APP_ERROR DestroyIntArray(void *int_array);
}  // namespace dataset
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_MINDDATA_DATASET_KERNELS_IMAGE_DVPP_UTILS_DVPP_IMAGE_UTILS_H_
