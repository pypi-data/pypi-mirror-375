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

#include "yirage/kernel/customized.h"
#include "yirage/kernel/device_memory_manager.h"
#include "yirage/kernel/graph.h"
#include "yirage/threadblock/cuda/concat.h"
#include "yirage/threadblock/cuda/element_binary.h"
#include "yirage/threadblock/cuda/element_unary.h"
#include "yirage/threadblock/cuda/forloop_accum.h"
#include "yirage/threadblock/cuda/input_loader.h"
#include "yirage/threadblock/cuda/matmul.h"
#include "yirage/threadblock/cuda/output_saver.h"
#include "yirage/threadblock/cuda/reduction.h"
#include "yirage/threadblock/cuda/rms_norm.h"
#include "yirage/threadblock/graph.h"
#include "yirage/threadblock/serializer/concat_serializer.h"
#include "yirage/threadblock/serializer/element_binary_serializer.h"
#include "yirage/threadblock/serializer/element_unary_serializer.h"
#include "yirage/threadblock/serializer/forloop_accum_serializer.h"
#include "yirage/threadblock/serializer/input_loader_serializer.h"
#include "yirage/threadblock/serializer/matmul_serializer.h"
#include "yirage/threadblock/serializer/output_saver_serializer.h"
#include "yirage/threadblock/serializer/reduction_serializer.h"
#include "yirage/threadblock/serializer/rms_norm_serializer.h"
#include "yirage/utils/cuda_helper.h"
#include "yirage/utils/fingerprint_functions.h"
#include "yirage/warp/cuda/matmul.h"

namespace yirage {
namespace kernel {

// TODO: deprecated; to be removed
__global__ void customized_kernel_function(
    yirage::threadblock::NewKernelParams const new_params,
    int forloop_range,
    char *dmem_base_ptr) {
  // since we are using cutlass, we group all threads within a threadblock
  // as a 1-D list of threads, therefore blockDim.y and blockDim.z must be
  // 1
  if (blockDim.y > 1 || blockDim.z > 1) {
    assert(false && "blockDim.y and blockDim.z must be 1");
  }

  extern __shared__ char smem_buffer[];

  int param_idx = 0;
  for (int i = 0; i < forloop_range; i++) {
    // start executing operators
    param_idx = 0;
    for (int op = 0; op < new_params.num_operators; op++) {
      yirage::type::TBOperatorType op_type = new_params.operator_types[op];
      if (op_type == yirage::type::TB_INPUT_OP) {
        // Assume that InputLoaders are the first operators
        char *dtensor_ptr = dmem_base_ptr + new_params.dmem_input_offsets[op];
        int3 input_matrix_row_offset_block_stride;
        int3 input_matrix_column_offset_block_stride;
        int input_matrix_row_offset_forloop_stride;
        int input_matrix_column_offset_forloop_stride;
        int3 global_offset_block_stride;
        int global_offset_forloop_stride;
        int2 dtensor_matrix_shape, stensor_matrix_shape;
        int input_smem_offset;
        yirage::layout::DmemLayout dtensor_layout;
        yirage::layout::SmemLayout stensor_layout;
        yirage::threadblock::deserialize_input_loader_parameters(
            new_params.parameters,
            param_idx,
            input_matrix_row_offset_block_stride,
            input_matrix_column_offset_block_stride,
            input_matrix_row_offset_forloop_stride,
            input_matrix_column_offset_forloop_stride,
            global_offset_block_stride,
            global_offset_forloop_stride,
            dtensor_matrix_shape,
            stensor_matrix_shape,
            dtensor_layout,
            stensor_layout,
            input_smem_offset);

        int tb_offset_row =
            blockIdx.x * input_matrix_row_offset_block_stride.x +
            blockIdx.y * input_matrix_row_offset_block_stride.y +
            blockIdx.z * input_matrix_row_offset_block_stride.z +
            i * input_matrix_row_offset_forloop_stride;
        int tb_offset_column =
            blockIdx.x * input_matrix_column_offset_block_stride.x +
            blockIdx.y * input_matrix_column_offset_block_stride.y +
            blockIdx.z * input_matrix_column_offset_block_stride.z +
            i * input_matrix_column_offset_forloop_stride;
        int global_offset = blockIdx.x * global_offset_block_stride.x +
                            blockIdx.y * global_offset_block_stride.y +
                            blockIdx.z * global_offset_block_stride.z +
                            i * global_offset_forloop_stride;
        cutlass::MatrixCoord matrix_offset = {tb_offset_row, tb_offset_column};
        cutlass::half_t *stensor_ptr =
            (cutlass::half_t *)(smem_buffer + input_smem_offset);
        yirage::threadblock::GenericInputLoader loader(dtensor_ptr,
                                                       stensor_ptr,
                                                       dtensor_matrix_shape,
                                                       stensor_matrix_shape,
                                                       dtensor_layout,
                                                       stensor_layout,
                                                       threadIdx.x,
                                                       blockDim.x,
                                                       matrix_offset,
                                                       global_offset);
        __syncthreads();
      } else if (op_type == yirage::type::TB_OUTPUT_OP) {
        // Only save outputs after forloop
        // So we do nothing for output saver
      } else if (op_type == yirage::type::TB_FORLOOP_ACCUM_NO_RED_OP ||
                 op_type == yirage::type::TB_FORLOOP_ACCUM_RED_LD_SUM_OP ||
                 op_type == yirage::type::TB_FORLOOP_ACCUM_RED_LD_MEAN_OP ||
                 op_type == yirage::type::TB_FORLOOP_ACCUM_RED_LD_RMS_OP ||
                 op_type == yirage::type::TB_FORLOOP_ACCUM_REDTOX_LD_SUM_OP) {
        // Do nothing since accum can be performed as an epilogue of
        // the previous operator
        int input_smem_offset, accum_smem_offset;
        int accum_num_elements, per_iter_reduction_degree, inner_range;
        yirage::threadblock::deserialize_forloop_accum_parameters(
            new_params.parameters,
            param_idx,
            accum_num_elements,
            per_iter_reduction_degree,
            inner_range,
            input_smem_offset,
            accum_smem_offset);
      } else if (op_type == yirage::type::TB_MATMUL_OP) {
        int thread_idx = threadIdx.x;
        // Broadcast the warp_id computed by lane 0 to ensure dependent code
        // is compiled as warp-uniform.
        int warp_idx = __shfl_sync(0xffffffff, threadIdx.x / 32, 0);
        int lane_idx = threadIdx.x % 32;
        int m, n, k;
        int A_smem_offset, B_smem_offset, C_smem_offset;
        yirage::threadblock::deserialize_matmul_op_parameters(
            new_params.parameters,
            param_idx,
            m,
            n,
            k,
            A_smem_offset,
            B_smem_offset,
            C_smem_offset);

        cutlass::half_t *A_ptr =
            (cutlass::half_t *)(smem_buffer + A_smem_offset);
        cutlass::half_t *B_ptr =
            (cutlass::half_t *)(smem_buffer + B_smem_offset);
        cutlass::half_t *C_ptr =
            (cutlass::half_t *)(smem_buffer + C_smem_offset);

        yirage::type::ActivationType act_type =
            yirage::utils::get_matmul_activation_type(
                new_params.operator_types, op, new_params.num_operators);

        if (act_type == yirage::type::ACT_NONE) {
          yirage::threadblock::GenericMatmulExecutor<yirage::type::ACT_NONE>
              executor(
                  A_ptr, B_ptr, C_ptr, m, n, k, thread_idx, warp_idx, lane_idx);

        } else if (act_type == yirage::type::ACT_EXP) {
          // fuse this matmul with next op
          int smem_offset, num_elements;
          yirage::threadblock::deserialize_elementunary_op_parameters(
              new_params.parameters, param_idx, smem_offset, num_elements);
          C_ptr = (cutlass::half_t *)(smem_buffer + smem_offset);
          yirage::threadblock::GenericMatmulExecutor<yirage::type::ACT_EXP>
              executor(
                  A_ptr, B_ptr, C_ptr, m, n, k, thread_idx, warp_idx, lane_idx);
          op += 1;
        }
        __syncthreads();
      } else if (op_type == yirage::type::TB_EXP_OP ||
                 op_type == yirage::type::TB_SQUARE_OP ||
                 op_type == yirage::type::TB_SQRT_OP ||
                 op_type == yirage::type::TB_SILU_OP ||
                 op_type == yirage::type::TB_GELU_OP ||
                 op_type == yirage::type::TB_RELU_OP ||
                 op_type == yirage::type::TB_CLAMP_OP) {
        int smem_offset, num_elements;
        yirage::threadblock::deserialize_elementunary_op_parameters(
            new_params.parameters, param_idx, smem_offset, num_elements);
        cutlass::half_t *base_ptr =
            (cutlass::half_t *)(smem_buffer + smem_offset);
        yirage::threadblock::ElementUnaryExecutor<cutlass::half_t> executor(
            op_type, base_ptr, num_elements, threadIdx.x, blockDim.x);
        __syncthreads();
      } else if (op_type == yirage::type::TB_DIV_OP ||
                 op_type == yirage::type::TB_ADD_OP ||
                 op_type == yirage::type::TB_MUL_OP ||
                 op_type == yirage::type::TB_POW_OP) {
        int3 input1_shape, input2_shape;
        int input1_smem_offset, input2_smem_offset, output_smem_offset;
        yirage::threadblock::deserialize_elementbinary_op_parameters(
            new_params.parameters,
            param_idx,
            input1_shape,
            input2_shape,
            input1_smem_offset,
            input2_smem_offset,
            output_smem_offset);
        cutlass::half_t *input1_ptr =
            (cutlass::half_t *)(smem_buffer + input1_smem_offset);
        cutlass::half_t *input2_ptr =
            (cutlass::half_t *)(smem_buffer + input2_smem_offset);
        cutlass::half_t *output_ptr =
            (cutlass::half_t *)(smem_buffer + output_smem_offset);
        yirage::threadblock::ElementBinaryExecutor<cutlass::half_t> executor(
            op_type,
            input1_ptr,
            input2_ptr,
            output_ptr,
            input1_shape,
            input2_shape,
            threadIdx.x,
            blockDim.x);
        __syncthreads();
      } else if ((op_type >= yirage::type::TB_REDUCTION_FIRST_OP_ID) &&
                 (op_type <= yirage::type::TB_REDUCTION_LAST_OP_ID)) {
        int output_num_elements, reduction_degree, inner_range;
        int input_smem_offset, output_smem_offset;
        yirage::threadblock::deserialize_reduction_op_parameters(
            new_params.parameters,
            param_idx,
            output_num_elements,
            reduction_degree,
            inner_range,
            input_smem_offset,
            output_smem_offset);
        cutlass::half_t *input_ptr =
            (cutlass::half_t *)(smem_buffer + input_smem_offset);
        cutlass::half_t *output_ptr =
            (cutlass::half_t *)(smem_buffer + output_smem_offset);

        yirage::threadblock::SimpleRedunctionExecutor<cutlass::half_t> executor(
            // new_params.operator_types[op],
            input_ptr,
            output_ptr,
            output_num_elements,
            reduction_degree,
            inner_range,
            threadIdx.x,
            blockDim.x);
        __syncthreads();
      } else if (op_type == yirage::type::TB_RMS_NORM_OP) {
        int output_num_elements, norm_size;
        int input_smem_offset, output_smem_offset;
        yirage::threadblock::deserialize_rms_norm_op_parameters(
            new_params.parameters,
            param_idx,
            output_num_elements,
            norm_size,
            input_smem_offset,
            output_smem_offset);
      } else if ((op_type >= yirage::type::TB_CONCAT_FIRST_OP_ID) &&
                 (op_type <= yirage::type::TB_CONCAT_LAST_OP_ID)) {
        int output_num_elements, A_concat_dim_size, B_concat_dim_size,
            inner_size;
        int A_smem_offset, B_smem_offset, output_smem_offset;
        yirage::threadblock::deserialize_concat_op_parameters(
            new_params.parameters,
            param_idx,
            output_num_elements,
            A_concat_dim_size,
            B_concat_dim_size,
            inner_size,
            A_smem_offset,
            B_smem_offset,
            output_smem_offset);
        // Do nothing since we can avoid concat mem copy by
        // updating the input tensors smem_offset
      } else {
        assert(false && "Unsupported threadblock operator");
      }
    }
  }
  // Save output
  int output_saver_start_idx =
      new_params.num_operators - new_params.num_dmem_outputs;
  for (int op = output_saver_start_idx; op < new_params.num_operators; op++) {
    assert(new_params.operator_types[op] == yirage::type::TB_OUTPUT_OP);
    char *dtensor_ptr =
        dmem_base_ptr +
        new_params.dmem_output_offsets[op - output_saver_start_idx];
    int3 output_matrix_row_offset_block_stride;
    int3 output_matrix_column_offset_block_stride;
    int output_matrix_row_offset_forloop_stride;
    int output_matrix_column_offset_forloop_stride;
    int3 global_offset_block_stride;
    int global_offset_forloop_stride;
    int2 dtensor_matrix_shape, stensor_matrix_shape;
    int input_smem_offset;
    yirage::layout::DmemLayout dtensor_layout;
    yirage::layout::SmemLayout stensor_layout;
    yirage::type::TBEpilogueType epilogue;
    yirage::threadblock::deserialize_output_saver_parameters(
        new_params.parameters,
        param_idx,
        output_matrix_row_offset_block_stride,
        output_matrix_column_offset_block_stride,
        output_matrix_row_offset_forloop_stride,
        output_matrix_column_offset_forloop_stride,
        global_offset_block_stride,
        global_offset_forloop_stride,
        dtensor_matrix_shape,
        stensor_matrix_shape,
        dtensor_layout,
        stensor_layout,
        input_smem_offset,
        epilogue);
    int tb_offset_row = blockIdx.x * output_matrix_row_offset_block_stride.x +
                        blockIdx.y * output_matrix_row_offset_block_stride.y +
                        blockIdx.z * output_matrix_row_offset_block_stride.z;
    int tb_offset_column =
        blockIdx.x * output_matrix_column_offset_block_stride.x +
        blockIdx.y * output_matrix_column_offset_block_stride.y +
        blockIdx.z * output_matrix_column_offset_block_stride.z;
    // calculate global offset beyond the last two dimensions
    // global_offset captures offsets caused by partitioning other dimensions
    // such as batch matmul
    // global_offset is directly added to dtensor_ptr by the output saver
    int global_offset = blockIdx.x * global_offset_block_stride.x +
                        blockIdx.y * global_offset_block_stride.y +
                        blockIdx.z * global_offset_block_stride.z;

    // FIXME: use cutlass prologue for loading data into shared memory
    // examples/13_two_tensor_op_fusion/threadblock/
    // b2b_mma_pipelined_smem_accumulator.h prologue iterators
    cutlass::MatrixCoord matrix_offset = {tb_offset_row, tb_offset_column};
    cutlass::half_t *stensor_ptr =
        (cutlass::half_t *)(smem_buffer + input_smem_offset);
    yirage::threadblock::GenericOutputSaver saver(dtensor_ptr,
                                                  stensor_ptr,
                                                  dtensor_matrix_shape,
                                                  stensor_matrix_shape,
                                                  dtensor_layout,
                                                  stensor_layout,
                                                  threadIdx.x,
                                                  blockDim.x,
                                                  matrix_offset,
                                                  global_offset);
    // No need to synchronize for output saver
    //__syncthreads();
  }
  assert(new_params.num_parameters == param_idx);
}

__global__ void compute_customizedop_fingerprint(
    yirage::threadblock::NewKernelParams new_params,
    int forloop_range,
    char *dmem_fp_ptr,
    char *stensor_fp_base_ptr,
    yirage::type::FPType *exp_lookup_table,
    yirage::type::FPType *div_p_lookup_table,
    yirage::type::FPType *div_q_lookup_table,
    yirage::type::FPType *sqrt_p_lookup_table,
    yirage::type::FPType *sqrt_q_lookup_table) {
  // since we are using cutlass, we group all threads within a threadblock
  // as a 1-D list of threads, therefore blockDim.y and blockDim.z must be
  // 1
  // extern __shared__ char smem_buffer[];
  int64_t thread_block_idx =
      blockIdx.x * gridDim.y * gridDim.z + blockIdx.y * gridDim.z + blockIdx.z;
  char *smem_buffer =
      stensor_fp_base_ptr + thread_block_idx * yirage::config::MAX_SMEM_FP_SIZE;
  assert(blockDim.y == 1);
  assert(blockDim.z == 1);

  int param_idx = 0;
  int output_saver_start_idx =
      new_params.num_operators - new_params.num_dmem_outputs;
  for (int i = 0; i < forloop_range; i++) {
    param_idx = 0;
    // start executing operators
    for (int op = 0; op < new_params.num_operators; op++) {
      bool skip_operator_after_forloop_accum = false;
      if (new_params.operator_after_accum[op] && (i < forloop_range - 1)) {
        // Only perform operators that are after forloop accum
        // in the last iteration (i.e., i == forloop_range - 1)
        // Skip the operator in other iterations
        skip_operator_after_forloop_accum = true;
      }
      switch (new_params.operator_types[op]) {
        case yirage::type::TB_INPUT_OP: {
          yirage::type::FPType *dtensor_ptr =
              (yirage::type::FPType *)(dmem_fp_ptr +
                                       new_params.dmem_input_offsets[op]);
          int3 input_matrix_row_offset_block_stride;
          int3 input_matrix_column_offset_block_stride;
          int input_matrix_row_offset_forloop_stride;
          int input_matrix_column_offset_forloop_stride;
          int3 global_offset_block_stride;
          int global_offset_forloop_stride;
          int2 dtensor_matrix_shape, stensor_matrix_shape;
          int input_smem_offset;
          yirage::layout::DmemLayout dtensor_layout;
          yirage::layout::SmemLayout stensor_layout;
          yirage::threadblock::deserialize_input_loader_parameters(
              new_params.parameters,
              param_idx,
              input_matrix_row_offset_block_stride,
              input_matrix_column_offset_block_stride,
              input_matrix_row_offset_forloop_stride,
              input_matrix_column_offset_forloop_stride,
              global_offset_block_stride,
              global_offset_forloop_stride,
              dtensor_matrix_shape,
              stensor_matrix_shape,
              dtensor_layout,
              stensor_layout,
              input_smem_offset);
          // input loader is always before forloop accum
          assert(!skip_operator_after_forloop_accum);
          // Note that input_matrix_offset_forloop_stride's x and y indicates
          // row and column
          int tb_offset_row =
              blockIdx.x * input_matrix_row_offset_block_stride.x +
              blockIdx.y * input_matrix_row_offset_block_stride.y +
              blockIdx.z * input_matrix_row_offset_block_stride.z +
              i * input_matrix_row_offset_forloop_stride;
          int tb_offset_column =
              blockIdx.x * input_matrix_column_offset_block_stride.x +
              blockIdx.y * input_matrix_column_offset_block_stride.y +
              blockIdx.z * input_matrix_column_offset_block_stride.z +
              i * input_matrix_column_offset_forloop_stride;
          int global_offset = blockIdx.x * global_offset_block_stride.x +
                              blockIdx.y * global_offset_block_stride.y +
                              blockIdx.z * global_offset_block_stride.z +
                              i * global_offset_forloop_stride;
          cutlass::MatrixCoord matrix_offset = {tb_offset_row,
                                                tb_offset_column};
          yirage::type::FPType *stensor_ptr =
              (yirage::type::FPType *)(smem_buffer + input_smem_offset);
          yirage::threadblock::TBInputLoaderFingerprinter fp(
              dtensor_ptr,
              stensor_ptr,
              dtensor_matrix_shape,
              stensor_matrix_shape,
              dtensor_layout,
              stensor_layout,
              threadIdx.x,
              blockDim.x,
              matrix_offset,
              global_offset);
          __syncthreads();
          break;
        }
        case yirage::type::TB_FORLOOP_ACCUM_NO_RED_OP:
        case yirage::type::TB_FORLOOP_ACCUM_RED_LD_SUM_OP:
        case yirage::type::TB_FORLOOP_ACCUM_RED_LD_MEAN_OP:
        case yirage::type::TB_FORLOOP_ACCUM_RED_LD_RMS_OP:
        case yirage::type::TB_FORLOOP_ACCUM_REDTOX_LD_SUM_OP: {
          int input_smem_offset, accum_smem_offset;
          int accum_num_elements, per_iter_reduction_degree, inner_range;
          yirage::threadblock::deserialize_forloop_accum_parameters(
              new_params.parameters,
              param_idx,
              accum_num_elements,
              per_iter_reduction_degree,
              inner_range,
              input_smem_offset,
              accum_smem_offset);
          // Forloop accum is NOT after forloop accum: since we should
          // accumulate in each iteration
          assert(!skip_operator_after_forloop_accum);
          yirage::type::FPType *input_stensor_ptr =
              (yirage::type::FPType *)(smem_buffer + input_smem_offset);
          yirage::type::FPType *accum_stensor_ptr =
              (yirage::type::FPType *)(smem_buffer + accum_smem_offset);
          bool reset_output = (i == 0);
          bool post_process = (i == (forloop_range - 1));
          yirage::threadblock::TBForloopAccumFingerprinter fp(
              new_params.operator_types[op],
              input_stensor_ptr,
              accum_stensor_ptr,
              div_p_lookup_table,
              div_q_lookup_table,
              sqrt_p_lookup_table,
              sqrt_q_lookup_table,
              accum_num_elements,
              per_iter_reduction_degree,
              inner_range,
              forloop_range,
              reset_output,
              post_process,
              threadIdx.x,
              blockDim.x);
          __syncthreads();
          break;
        }
        case yirage::type::TB_OUTPUT_OP: {
          int3 output_matrix_row_offset_block_stride;
          int3 output_matrix_column_offset_block_stride;
          int output_matrix_row_offset_forloop_stride;
          int output_matrix_column_offset_forloop_stride;
          int3 global_offset_block_stride;
          int global_offset_forloop_stride;
          int2 dtensor_matrix_shape, stensor_matrix_shape;
          int input_smem_offset;
          yirage::layout::DmemLayout dtensor_layout;
          yirage::layout::SmemLayout stensor_layout;
          yirage::type::TBEpilogueType epilogue;
          yirage::threadblock::deserialize_output_saver_parameters(
              new_params.parameters,
              param_idx,
              output_matrix_row_offset_block_stride,
              output_matrix_column_offset_block_stride,
              output_matrix_row_offset_forloop_stride,
              output_matrix_column_offset_forloop_stride,
              global_offset_block_stride,
              global_offset_forloop_stride,
              dtensor_matrix_shape,
              stensor_matrix_shape,
              dtensor_layout,
              stensor_layout,
              input_smem_offset,
              epilogue);
          // Skip the current operator's fingerprint calculation
          // since it is after forloop accum and we are not at the
          // last iteration yet
          if (skip_operator_after_forloop_accum) {
            continue;
          }
          bool non_zero_forloop_strides = false;
          if ((output_matrix_row_offset_forloop_stride > 0) ||
              (output_matrix_column_offset_forloop_stride > 0) ||
              (global_offset_forloop_stride > 0)) {
            non_zero_forloop_strides = true;
          }
          yirage::type::FPType *input_stensor_ptr =
              (yirage::type::FPType *)(smem_buffer + input_smem_offset);
          // Step 2: Save final output to dmem if (1) this is the last forloop
          // or (2) we don't accum output since the forloop strides are non-zero
          if ((i == forloop_range - 1) || non_zero_forloop_strides) {
            assert(op >= output_saver_start_idx);
            yirage::type::FPType *dtensor_ptr =
                (yirage::type::FPType
                     *)(dmem_fp_ptr +
                        new_params
                            .dmem_output_offsets[op - output_saver_start_idx]);
            int tb_offset_row =
                blockIdx.x * output_matrix_row_offset_block_stride.x +
                blockIdx.y * output_matrix_row_offset_block_stride.y +
                blockIdx.z * output_matrix_row_offset_block_stride.z +
                i * output_matrix_row_offset_forloop_stride;
            int tb_offset_column =
                blockIdx.x * output_matrix_column_offset_block_stride.x +
                blockIdx.y * output_matrix_column_offset_block_stride.y +
                blockIdx.z * output_matrix_column_offset_block_stride.z +
                i * output_matrix_column_offset_forloop_stride;
            // calculate global offset beyond the last two dimensions
            // global_offset captures offsets caused by partitioning other
            // dimensions such as batch matmul global_offset is directly added
            // to dtensor_ptr by the output saver
            int global_offset = blockIdx.x * global_offset_block_stride.x +
                                blockIdx.y * global_offset_block_stride.y +
                                blockIdx.z * global_offset_block_stride.z +
                                i * global_offset_forloop_stride;
            cutlass::MatrixCoord matrix_offset = {tb_offset_row,
                                                  tb_offset_column};
            yirage::threadblock::TBOutputSaverFingerprinter fp(
                dtensor_ptr,
                input_stensor_ptr,
                dtensor_matrix_shape,
                stensor_matrix_shape,
                dtensor_layout,
                stensor_layout,
                threadIdx.x,
                blockDim.x,
                matrix_offset,
                global_offset);
            // No need to syncthread when saving output to dmem
            __syncthreads();
          }
          break;
        }
        case yirage::type::TB_MATMUL_OP: {
          int m, n, k;
          int A_smem_offset, B_smem_offset, C_smem_offset;
          yirage::threadblock::deserialize_matmul_op_parameters(
              new_params.parameters,
              param_idx,
              m,
              n,
              k,
              A_smem_offset,
              B_smem_offset,
              C_smem_offset);
          // Skip the current operator's fingerprint calculation
          // since it is after forloop accum and we are not at the
          // last iteration yet
          if (skip_operator_after_forloop_accum) {
            continue;
          }
          yirage::type::FPType *A_ptr =
              (yirage::type::FPType *)(smem_buffer + A_smem_offset);
          yirage::type::FPType *B_ptr =
              (yirage::type::FPType *)(smem_buffer + B_smem_offset);
          yirage::type::FPType *C_ptr =
              (yirage::type::FPType *)(smem_buffer + C_smem_offset);

          yirage::threadblock::TBMatmulFingerprinter fp(
              A_ptr, B_ptr, C_ptr, m, n, k, threadIdx.x, blockDim.x);
          __syncthreads();
          break;
        }
        case yirage::type::TB_EXP_OP:
        case yirage::type::TB_SQUARE_OP:
        case yirage::type::TB_SQRT_OP:
        case yirage::type::TB_SILU_OP:
        case yirage::type::TB_GELU_OP:
        case yirage::type::TB_RELU_OP:
        case yirage::type::TB_CLAMP_OP: {
          int smem_offset, num_elements;
          yirage::threadblock::deserialize_elementunary_op_parameters(
              new_params.parameters, param_idx, smem_offset, num_elements);
          yirage::type::FPType *base_ptr =
              (yirage::type::FPType *)(smem_buffer + smem_offset);
          // Skip the current operator's fingerprint calculation
          // since it is after forloop accum and we are not at the
          // last iteration yet
          if (skip_operator_after_forloop_accum) {
            continue;
          }
          yirage::threadblock::TBElementUnaryFingerPrinter fp(
              new_params.operator_types[op],
              exp_lookup_table /*lookup_table*/,
              sqrt_p_lookup_table,
              sqrt_q_lookup_table,
              base_ptr,
              num_elements,
              threadIdx.x,
              blockDim.x);
          __syncthreads();
          break;
        }
        case yirage::type::TB_ADD_OP:
        case yirage::type::TB_MUL_OP:
        case yirage::type::TB_DIV_OP:
        case yirage::type::TB_POW_OP: {
          int3 input1_shape, input2_shape;
          int input1_smem_offset, input2_smem_offset, output_smem_offset;
          yirage::threadblock::deserialize_elementbinary_op_parameters(
              new_params.parameters,
              param_idx,
              input1_shape,
              input2_shape,
              input1_smem_offset,
              input2_smem_offset,
              output_smem_offset);
          yirage::type::FPType *input1_ptr =
              (yirage::type::FPType *)(smem_buffer + input1_smem_offset);
          yirage::type::FPType *input2_ptr =
              (yirage::type::FPType *)(smem_buffer + input2_smem_offset);
          yirage::type::FPType *output_ptr =
              (yirage::type::FPType *)(smem_buffer + output_smem_offset);
          // Skip the current operator's fingerprint calculation
          // since it is after forloop accum and we are not at the
          // last iteration yet
          if (skip_operator_after_forloop_accum) {
            continue;
          }
          yirage::threadblock::TBElementBinaryFingerPrinter fp(
              new_params.operator_types[op],
              div_p_lookup_table /*div_p_lookup*/,
              div_q_lookup_table /*div_q_lookup*/,
              input1_ptr,
              input2_ptr,
              output_ptr,
              input1_shape,
              input2_shape,
              threadIdx.x,
              blockDim.x);
          __syncthreads();
          break;
        }
        case yirage::type::TB_REDUCTION_0_OP:
        case yirage::type::TB_REDUCTION_1_OP:
        case yirage::type::TB_REDUCTION_2_OP:
        case yirage::type::TB_REDUCTION_0_TO_DIMX_OP:
        case yirage::type::TB_REDUCTION_1_TO_DIMX_OP:
        case yirage::type::TB_REDUCTION_2_TO_DIMX_OP: {
          int output_num_elements, reduction_degree, inner_range;
          int input_smem_offset, output_smem_offset;
          yirage::threadblock::deserialize_reduction_op_parameters(
              new_params.parameters,
              param_idx,
              output_num_elements,
              reduction_degree,
              inner_range,
              input_smem_offset,
              output_smem_offset);
          yirage::type::FPType *output_ptr =
              (yirage::type::FPType *)(smem_buffer + output_smem_offset);
          yirage::type::FPType *input_ptr =
              (yirage::type::FPType *)(smem_buffer + input_smem_offset);
          // Skip the current operator's fingerprint calculation
          // since it is after forloop accum and we are not at the
          // last iteration yet
          if (skip_operator_after_forloop_accum) {
            continue;
          }
          yirage::threadblock::TBReductionFingerprinter fp(
              new_params.operator_types[op],
              input_ptr,
              output_ptr,
              output_num_elements,
              reduction_degree,
              inner_range,
              threadIdx.x,
              blockDim.x);
          __syncthreads();
          break;
        }
        case yirage::type::TB_RMS_NORM_OP: {
          int output_num_elements, norm_size;
          int input_smem_offset, output_smem_offset;
          yirage::threadblock::deserialize_rms_norm_op_parameters(
              new_params.parameters,
              param_idx,
              output_num_elements,
              norm_size,
              input_smem_offset,
              output_smem_offset);
          yirage::type::FPType *output_ptr =
              (yirage::type::FPType *)(smem_buffer + output_smem_offset);
          yirage::type::FPType *input_ptr =
              (yirage::type::FPType *)(smem_buffer + input_smem_offset);
          yirage::threadblock::TBRmsNormFingerPrinter fp(input_ptr,
                                                         output_ptr,
                                                         div_p_lookup_table,
                                                         div_q_lookup_table,
                                                         sqrt_p_lookup_table,
                                                         sqrt_q_lookup_table,
                                                         output_num_elements,
                                                         norm_size,
                                                         threadIdx.x,
                                                         blockDim.x);
          __syncthreads();
          break;
        }
        case yirage::type::TB_CONCAT_0_OP:
        case yirage::type::TB_CONCAT_1_OP:
        case yirage::type::TB_CONCAT_2_OP: {
          int output_num_elements, A_concat_dim_size, B_concat_dim_size,
              inner_size;
          int A_smem_offset, B_smem_offset, output_smem_offset;
          yirage::threadblock::deserialize_concat_op_parameters(
              new_params.parameters,
              param_idx,
              output_num_elements,
              A_concat_dim_size,
              B_concat_dim_size,
              inner_size,
              A_smem_offset,
              B_smem_offset,
              output_smem_offset);
          yirage::type::FPType *A_ptr =
              (yirage::type::FPType *)(smem_buffer + A_smem_offset);
          yirage::type::FPType *B_ptr =
              (yirage::type::FPType *)(smem_buffer + B_smem_offset);
          yirage::type::FPType *output_ptr =
              (yirage::type::FPType *)(smem_buffer + output_smem_offset);
          // Skip the current operator's fingerprint calculation
          // since it is after forloop accum and we are not at the
          // last iteration yet
          if (skip_operator_after_forloop_accum) {
            continue;
          }
          yirage::threadblock::TBConcatFingerprinter fp(A_ptr,
                                                        B_ptr,
                                                        output_ptr,
                                                        output_num_elements,
                                                        A_concat_dim_size,
                                                        B_concat_dim_size,
                                                        inner_size,
                                                        threadIdx.x,
                                                        blockDim.x);
          __syncthreads();
          break;
        }
        default: {
          assert(false && "Unsupported threadblock operator");
        }
      }
    }
    assert(new_params.num_parameters == param_idx);
  }
}

void KNCustomizedOp::run() {
  yirage::kernel::DeviceMemoryManager *dmm =
      yirage::kernel::DeviceMemoryManager::get_instance();
  // yirage::threadblock::KernelParams params = bgraph.get_kernel_params();
  yirage::threadblock::NewKernelParams new_params =
      bgraph.get_new_kernel_params(false /*fingerprint_kernel*/);
  // Assume a single GPU for now
  assert(kgraph->gpu_dim.x == 1);
  int gpu_id = 0;
  if (!yirage::type::CLAMP_MIN_MAX.empty()) {
    float CLAMP_MIN_MAX_HOST[2] = {yirage::type::CLAMP_MIN_MAX["min_val"],
                                   yirage::type::CLAMP_MIN_MAX["max_val"]};
    cudaMemcpyToSymbol(
        CLAMP_MIN_MAX_DEVICE, CLAMP_MIN_MAX_HOST, sizeof(float) * 2);
  }
  customized_kernel_function<<<bgraph.grid_dim,
                               bgraph.block_dim,
                               bgraph.smem_offset>>>(
      new_params, bgraph.forloop_range, dmm->data_base_ptr[gpu_id]);
}

__global__ void
    compute_epilogue_fingerprint(yirage::utils::FpPointerList fp_ptr_list,
                                 yirage::type::TBEpilogueType type,
                                 int num_gpus,
                                 int num_elements) {
  if (type == yirage::type::TB_EPILOGUE_NONE) {
    // Do nothing
  } else if (type == yirage::type::TB_EPILOGUE_ALLREDUCE) {
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    if (i < num_elements) {
      FPType x = 0;
      for (int k = 0; k < num_gpus; k++) {
        x = utils::compute_add_fingerprint(x, fp_ptr_list.ptrs[k][i]);
      }
      for (int k = 0; k < num_gpus; k++) {
        fp_ptr_list.ptrs[k][i] = x;
      }
    }
  } else {
    assert(false && "Unsupported epilogue");
  }
}

bool KNCustomizedOp::fingerprint(void) {
  // yirage::threadblock::KernelParams params = bgraph.get_kernel_params();
  yirage::threadblock::NewKernelParams new_params =
      bgraph.get_new_kernel_params(true /*fingerprint_kernel*/);
  // assume that we only parallelize along the x dimension
  assert(kgraph->gpu_dim.y == 1);
  assert(kgraph->gpu_dim.z == 1);

  assert(bgraph.smem_offset <= yirage::config::MAX_SMEM_FP_SIZE);
  yirage::kernel::DeviceMemoryManager *dmm =
      yirage::kernel::DeviceMemoryManager::get_instance();

  // Make sure we don't launch more threadblocks than allowed
  assert(bgraph.grid_dim.x * bgraph.grid_dim.y * bgraph.grid_dim.z <=
         yirage::config::MAX_NUM_THREADBLOCKS_PER_KERNEL);

  for (int gpu_id = 0; gpu_id < kgraph->gpu_dim.x; gpu_id++) {
    compute_customizedop_fingerprint<<<bgraph.grid_dim, bgraph.block_dim>>>(
        new_params,
        bgraph.forloop_range,
        dmm->fp_base_ptr[gpu_id],
        dmm->stensor_fp_base_ptr,
        dmm->exp_lookup_table,
        dmm->div_p_lookup_table,
        dmm->div_q_lookup_table,
        dmm->sqrt_p_lookup_table,
        dmm->sqrt_q_lookup_table);
  }
  checkCUDA(cudaDeviceSynchronize());
  // Process epilogue
  for (auto const &op : bgraph.operators) {
    if (op->op_type == yirage::type::TB_OUTPUT_OP) {
      yirage::threadblock::TBOutputOp const *output_op =
          static_cast<yirage::threadblock::TBOutputOp const *>(op);
      if (output_op->epilogue != yirage::type::TB_EPILOGUE_NONE) {
        yirage::utils::FpPointerList fp_ptr_list;
        for (int gpu_id = 0; gpu_id < kgraph->gpu_dim.x; gpu_id++) {
          fp_ptr_list.ptrs[gpu_id] = reinterpret_cast<yirage::type::FPType *>(
              dmm->fp_base_ptr[gpu_id] + output_op->dtensor.fp_offset);
        }
        int num_elements = output_op->dtensor.num_elements();
        int const num_threads_per_blk = 1024;
        int num_blocks =
            (num_elements + num_threads_per_blk - 1) / num_threads_per_blk;
        compute_epilogue_fingerprint<<<num_blocks, num_threads_per_blk>>>(
            fp_ptr_list, output_op->epilogue, kgraph->gpu_dim.x, num_elements);
        checkCUDA(cudaDeviceSynchronize());
      }
    }
  }
  return true;
}

} // namespace kernel
} // namespace yirage
