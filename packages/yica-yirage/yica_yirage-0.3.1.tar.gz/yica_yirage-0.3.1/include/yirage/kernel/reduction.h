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

#pragma once

#include "yirage/kernel/operator.h"

namespace yirage {
namespace kernel {

class KNReductionOp : public yirage::kernel::KNOperator {
public:
  KNReductionOp(Graph *_graph, DTensor const &input, int dim, int size);
  ~KNReductionOp();
  bool fingerprint(void) override;

  operator json() const override;

public:
  int reduction_dim_idx, reduction_dim_size;
};

} // namespace kernel
} // namespace yirage
