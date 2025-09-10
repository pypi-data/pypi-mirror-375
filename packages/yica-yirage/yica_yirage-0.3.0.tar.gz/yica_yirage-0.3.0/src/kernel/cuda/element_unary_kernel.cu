/* Copyright 2025-2026 YICA TEAM
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "cutlass/fast_math.h"
#include "yirage/config.h"
#include "yirage/kernel/device_memory_manager.h"
#include "yirage/kernel/element_unary.h"
#include "yirage/kernel/graph.h"
#include "yirage/utils/cuda_helper.h"
#include "yirage/utils/fingerprint_functions.h"
#include "yirage/utils/hash_utils.h"
#include <cassert>

namespace yirage {
namespace kernel {

using namespace yirage::type;
using namespace yirage::config;
using namespace yirage::utils;

__constant__ float CLAMP_MIN_MAX_DEVICE[2];

template <typename DT>
__global__ void execute_elementunary(yirage::type::KNOperatorType type,
                                     DT *input_ptr,
                                     DT *output_ptr,
                                     int num_elements) {
  int i = threadIdx.x + blockIdx.x * blockDim.x;
  if (type == yirage::type::KN_EXP_OP) {
    if (i < num_elements) {
      output_ptr[i] = cutlass::fast_exp(input_ptr[i]);
    }
  } else if (type == yirage::type::KN_SQUARE_OP) {
    if (i < num_elements) {
      output_ptr[i] = input_ptr[i] * input_ptr[i];
    }
  } else if (type == yirage::type::KN_SQRT_OP) {
    if (i < num_elements) {
      output_ptr[i] = cutlass::fast_sqrt(input_ptr[i]);
    }
  } else if (type == yirage::type::KN_SILU_OP) {
    if (i < num_elements) {
      DT x = input_ptr[i];
      output_ptr[i] = x / (1.0f + cutlass::fast_exp(-x));
    }
  } else if (type == yirage::type::KN_GELU_OP) {
    if (i < num_elements) {
      DT x = input_ptr[i];
      output_ptr[i] = (x / 2.0f) * (1.0f + erff(x / sqrtf(2.0f)));
    }
  } else if (type == yirage::type::KN_RELU_OP) {
    if (i < num_elements) {
      DT x = input_ptr[i];
      if (x > 0.0f) {
        output_ptr[i] = x;
      } else {
        output_ptr[i] = 0.0f;
      }
    }
  } else if (type == yirage::type::KN_CLAMP_OP) {
    if (i < num_elements) {
      DT x = input_ptr[i];
      if (x < CLAMP_MIN_MAX_DEVICE[0]) {
        output_ptr[i] = CLAMP_MIN_MAX_DEVICE[0];
      } else if (x > CLAMP_MIN_MAX_DEVICE[1]) {
        output_ptr[i] = CLAMP_MIN_MAX_DEVICE[1];
      } else {
        output_ptr[i] = x;
      }
    }
  } else {
    assert(false && "Unimplemented");
  }
}

__global__ void
    compute_elementunary_fingerprint(yirage::type::KNOperatorType type,
                                     FPType *exp_lookup_table,
                                     FPType *sqrt_p_lookup_table,
                                     FPType *sqrt_q_lookup_table,
                                     yirage::type::FPType *input_ptr,
                                     yirage::type::FPType *output_ptr,
                                     int num_elements) {
  int i = threadIdx.x + blockIdx.x * blockDim.x;
  if (i < num_elements) {
    if (type == yirage::type::KN_EXP_OP) {
      output_ptr[i] = compute_exp_fingerprint(input_ptr[i], exp_lookup_table);
    } else if (type == yirage::type::KN_SQUARE_OP) {
      output_ptr[i] = compute_square_fingerprint(input_ptr[i]);
    } else if (type == yirage::type::KN_SQRT_OP) {
      output_ptr[i] = compute_sqrt_fingerprint(
          input_ptr[i], sqrt_p_lookup_table, sqrt_q_lookup_table);
    } else if (type == yirage::type::KN_SILU_OP) {
      output_ptr[i] = compute_silu_fingerprint(input_ptr[i], exp_lookup_table);
    } else if (type == yirage::type::KN_GELU_OP) {
      output_ptr[i] = compute_gelu_fingerprint(input_ptr[i], exp_lookup_table);
    } else if (type == yirage::type::KN_RELU_OP) {
      output_ptr[i] = compute_relu_fingerprint(input_ptr[i]);
    } else if (type == yirage::type::KN_CLAMP_OP) {
      output_ptr[i] = compute_clamp_fingerprint(input_ptr[i]);
    } else {
      assert(false && "Unimplemented");
    }
  }
}

bool KNElementUnaryOp::fingerprint(void) {
  // assert a 1-D GPU mesh
  assert(kgraph->gpu_dim.y == 1);
  assert(kgraph->gpu_dim.z == 1);
  assert(input_tensors[0].num_elements() == output_tensors[0].num_elements());
  int num_elements = input_tensors[0].num_elements();
  int const num_threads_per_blk = 1024;
  int num_blocks =
      (num_elements + num_threads_per_blk - 1) / num_threads_per_blk;
  yirage::kernel::DeviceMemoryManager *dmm =
      yirage::kernel::DeviceMemoryManager::get_instance();
  // Use GPU dmm->gpu_id for computing fingerprint
  checkCUDA(cudaSetDevice(dmm->gpu_id));

  for (int gpu_id = 0; gpu_id < kgraph->gpu_dim.x; gpu_id++) {
    yirage::type::FPType *input_fp_ptr =
        reinterpret_cast<yirage::type::FPType *>(dmm->fp_base_ptr[gpu_id] +
                                                 input_tensors[0].fp_offset);
    yirage::type::FPType *output_fp_ptr =
        reinterpret_cast<yirage::type::FPType *>(dmm->fp_base_ptr[gpu_id] +
                                                 output_tensors[0].fp_offset);
    compute_elementunary_fingerprint<<<num_blocks, num_threads_per_blk>>>(
        op_type,
        dmm->exp_lookup_table,
        dmm->sqrt_p_lookup_table,
        dmm->sqrt_q_lookup_table,
        input_fp_ptr,
        output_fp_ptr,
        num_elements);
    checkCUDA(cudaDeviceSynchronize());
  }
  return true;
}

} // namespace kernel
} // namespace yirage
