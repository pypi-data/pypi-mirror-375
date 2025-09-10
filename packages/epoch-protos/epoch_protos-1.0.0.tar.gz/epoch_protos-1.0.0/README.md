# EpochProtos

Protocol Buffer definitions for EpochFolio - generates C++, Python, and TypeScript code.

## Quick Start

### Build Everything
```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### Deploy to Local Projects
```bash
# Build and copy C++ headers + library (recommended)
./scripts/build_and_copy.sh

# Or just copy (requires build first)
./scripts/copy_to_local.sh

# Quick headers only
./quick-deploy
```

### What You Get
- **C++**: Static library in `build/generated/cpp/`
- **Python**: Package in `build/generated/python/`
- **TypeScript**: Package in `build/generated/typescript/`

## Usage

### C++
```cpp
#include "common.pb.h"
#include "chart_def.pb.h"

epoch_proto::ChartDef chart;
chart.set_id("my_chart");
chart.set_type(epoch_proto::EpochFolioDashboardWidget::Lines);
```

### Python
```python
import common_pb2
import chart_def_pb2

chart = chart_def_pb2.ChartDef()
chart.id = "my_chart"
chart.type = common_pb2.EpochFolioDashboardWidget.Lines
```

### TypeScript
```typescript
import { ChartDef, EpochFolioDashboardWidget } from './chart_def';

const chart = new ChartDef();
chart.setId("my_chart");
chart.setType(EpochFolioDashboardWidget.Lines);
```

## Deployment

### C++ Local Copy (No vcpkg needed)
```bash
# Build and copy headers + library to EpochFolio (recommended)
./scripts/build_and_copy.sh

# Or just copy (requires build first)
./scripts/copy_to_local.sh

# Quick C++ headers only
./quick-deploy
```

### Python Local Install
```bash
./scripts/python_publish.sh install-local
```

### TypeScript Local Install
```bash
./scripts/typescript_publish.sh install-local
```

### Deploy Everything
```bash
./scripts/deploy.sh all
```

## Integration

### C++ Project
```cmake
# After running copy_to_local.sh
add_subdirectory(/path/to/epoch_protos)
target_link_libraries(your_target PRIVATE epoch::proto)
```

### Python Project
```bash
cd build/generated/python
pip install .
```

### TypeScript Project
```bash
cd build/generated/typescript
npm install
```

## Proto Files
- `common.proto` - Basic types and enums
- `chart_def.proto` - Chart definitions
- `table_def.proto` - Table definitions  
- `tearsheet.proto` - Dashboard tearsheet structure

## Testing
```bash
cd test
g++ -std=c++20 -I../build -o test_cpp test_cpp.cpp ../build/generated/cpp/libepoch_protos_cpp.a -lprotobuf
./test_cpp

python3 test_python.py
```