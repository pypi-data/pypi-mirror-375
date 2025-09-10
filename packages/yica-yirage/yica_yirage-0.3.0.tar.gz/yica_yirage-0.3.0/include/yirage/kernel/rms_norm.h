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

class KNRMSNormOp : public yirage::kernel::KNOperator {
public:
  KNRMSNormOp(Graph *_graph,
              DTensor const &input,
              std::vector<int> const &normalized_shape);
  ~KNRMSNormOp();
  bool fingerprint(void) override;

  operator json() const override;

public:
  int normalized_size;
};

} // namespace kernel
} // namespace yirage
