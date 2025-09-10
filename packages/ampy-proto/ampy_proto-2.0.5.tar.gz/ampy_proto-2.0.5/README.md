# ampy-proto

<div align="center">

**Canonical Protocol Buffer schemas for the AmpyFin trading system**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/Go-1.23+-blue.svg)](https://golang.org/)
[![Python Version](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org/)
[![C++ Standard](https://img.shields.io/badge/C%2B%2B-17+-red.svg)](https://en.cppreference.com/w/cpp/17)
[![Protocol Buffers](https://img.shields.io/badge/Protocol%20Buffers-v3.21+-orange.svg)](https://developers.google.com/protocol-buffers)
[![Buf](https://img.shields.io/badge/Buf-CLI-purple.svg)](https://buf.build/)

[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/yeonholee50/ampy-proto/actions)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](https://github.com/yeonholee50/ampy-proto/actions)
[![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)](https://github.com/yeonholee50/ampy-proto/actions)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A-brightgreen.svg)](https://github.com/yeonholee50/ampy-proto/actions)

[![Release](https://img.shields.io/badge/Release-v2.0.5-blue.svg)](https://github.com/yeonholee50/ampy-proto/releases)
[![Downloads](https://img.shields.io/badge/Downloads-1k%2B-blue.svg)](https://github.com/yeonholee50/ampy-proto/releases)
[![Last Commit](https://img.shields.io/badge/Last%20Commit-Recent-green.svg)](https://github.com/yeonholee50/ampy-proto/commits/main)

</div>

---

## 📋 Table of Contents

- [🎯 What We're Solving](#-what-were-solving)
- [⚡ Quick Start](#-quick-start)
- [📊 Available Schemas](#-available-schemas)
- [🏗️ Key Design Principles](#️-key-design-principles)
- [🛠️ Development](#️-development)
- [📈 Versioning](#-versioning)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [💬 Support](#-support)

## 🎯 What We're Solving

AmpyFin is building a self-learning, modular trading system that needs to handle data from multiple sources (DataBento, Tiingo, yfinance, etc.) across different languages (Go, Python, C++). This project provides:

- 🎯 **Unified schemas** for all financial data (bars, ticks, fundamentals, news, etc.)
- 🌐 **Cross-language compatibility** with generated code for Go, Python, and C++
- 🎯 **Precision guarantees** using scaled decimal types instead of floating-point
- ⏰ **Time discipline** with UTC timestamps and clear event/ingest time separation
- 🔄 **Versioned contracts** that evolve safely without breaking consumers

## ⚡ Quick Start

### 🐍 Python

```bash
# Install from PyPI (when published)
pip install ampy-proto

# Or install locally
pip install -e .
```

```python
from ampy.bars.v1 import bars_pb2
from ampy.common.v1 import common_pb2

# Create a bar
bar = bars_pb2.Bar()
bar.security.symbol = "AAPL"
bar.security.mic = "XNAS"
bar.open.scaled = 1923450
bar.open.scale = 4
bar.high.scaled = 1925600
bar.high.scale = 4
bar.low.scaled = 1922200
bar.low.scale = 4
bar.close.scaled = 1924100
bar.close.scale = 4
bar.volume = 184230

print(f"AAPL bar: ${bar.close.scaled / (10 ** bar.close.scale):.2f}")
```

### 🐹 Go

```bash
# Install all ampy-proto packages at once
go get github.com/AmpyFin/ampy-proto/v2@v2.0.5

# Or install specific packages only
go get github.com/AmpyFin/ampy-proto/v2/gen/go/ampy/bars/v1@v2.0.5
```

```go
package main

import (
    "fmt"
    barspb "github.com/AmpyFin/ampy-proto/v2/gen/go/ampy/bars/v1"
)

func main() {
    bar := &barspb.Bar{}
    bar.Security = &barspb.Security{
        Symbol: "AAPL",
        Mic:    "XNAS",
    }
    bar.Open = &barspb.Decimal{
        Scaled: 1923450,
        Scale:  4,
    }
    bar.High = &barspb.Decimal{
        Scaled: 1925600,
        Scale:  4,
    }
    bar.Low = &barspb.Decimal{
        Scaled: 1922200,
        Scale:  4,
    }
    bar.Close = &barspb.Decimal{
        Scaled: 1924100,
        Scale:  4,
    }
    bar.Volume = 184230

    fmt.Printf("AAPL bar: $%.2f\n", float64(bar.Close.Scaled)/float64(1e4))
}
```

### ⚡ C++

```bash
# Build the library
cd gen/cpp
mkdir build && cd build
cmake .. && make
```

```cpp
#include <iostream>
#include "ampy/bars/v1/bars.pb.h"

int main() {
    ampy::bars::v1::Bar bar;
    bar.mutable_security()->set_symbol("AAPL");
    bar.mutable_security()->set_mic("XNAS");
    bar.mutable_open()->set_scaled(1923450);
    bar.mutable_open()->set_scale(4);
    bar.mutable_high()->set_scaled(1925600);
    bar.mutable_high()->set_scale(4);
    bar.mutable_low()->set_scaled(1922200);
    bar.mutable_low()->set_scale(4);
    bar.mutable_close()->set_scaled(1924100);
    bar.mutable_close()->set_scale(4);
    bar.set_volume(184230);

    std::cout << "AAPL bar: $" 
              << (bar.close().scaled() / std::pow(10, bar.close().scale()))
              << std::endl;
    return 0;
}
```

## 📊 Available Schemas

| 🏷️ Domain | 📝 Purpose | 🔑 Key Messages |
|-----------|------------|-----------------|
| 📈 **bars** | OHLCV price bars | `Bar`, `BarBatch` |
| 📊 **ticks** | Trade and quote data | `Tick`, `TickBatch` |
| 📋 **fundamentals** | Financial statements | `Fundamental`, `FundamentalBatch` |
| 📰 **news** | Market news and sentiment | `NewsItem` |
| 💱 **fx** | Foreign exchange rates | `FxRate` |
| 🏢 **corporate_actions** | Splits, dividends | `CorporateAction` |
| 🌍 **universe** | Tradable securities lists | `Universe` |
| 🎯 **signals** | Model outputs and signals | `Signal` |
| 📋 **orders** | Order management | `Order`, `OrderRequest` |
| ✅ **fills** | Trade executions | `Fill` |
| 💼 **positions** | Portfolio positions | `Position` |
| 📊 **metrics** | Operational metrics | `Metric` |
| 🔧 **common** | Shared types | `Decimal`, `Money`, `Security`, `Meta` |

## 🏗️ Key Design Principles

### 1. 🎯 Precision with Scaled Decimals
Instead of floating-point numbers, we use scaled decimals:
```protobuf
message Decimal {
  int64 scaled = 1;  // The actual value
  int32 scale = 2;   // Decimal places (e.g., 4 = 4 decimal places)
}
```

Example: `scaled: 1923450, scale: 4` represents `192.3450`

### 2. ⏰ Time Discipline
All timestamps are UTC with clear semantics:
- 🕐 `event_time`: When the market event actually happened
- 📥 `ingest_time`: When our system received it
- 🎯 `as_of`: Logical timestamp for downstream processing

### 3. 🏷️ Security Identification
Use proper security identifiers, not just tickers:
```protobuf
message Security {
  string symbol = 1;    // e.g., "AAPL"
  string mic = 2;       // Market identifier code, e.g., "XNAS"
  string figi = 3;      // Financial Instrument Global Identifier (optional)
  string isin = 4;      // International Securities Identification Number (optional)
}
```

### 4. 🔍 Metadata for Traceability
Every message includes metadata for lineage:
```protobuf
message Meta {
  string run_id = 1;           // Unique run identifier
  string source = 2;           // Data source (e.g., "yfinance-go")
  string producer = 3;         // Producer instance ID
  string schema_version = 4;   // Schema version used
  string checksum = 5;         // Optional message checksum
}
```

## 🛠️ Development

### 📋 Prerequisites
- 🔧 [Buf](https://buf.build/docs/installation) for protobuf management
- 🐹 [Go](https://golang.org/) 1.23+ for Go code generation
- 🐍 [Python](https://python.org/) 3.9+ for Python code generation
- ⚡ [CMake](https://cmake.org/) and C++17 compiler for C++ code generation

### 🔨 Building

```bash
# Generate code for all languages
buf generate proto

# Lint protobuf files
buf lint proto

# Check for breaking changes
buf breaking proto --against '.git#branch=main'

# Build Python package
python -m build

# Build C++ library
cd gen/cpp && mkdir build && cd build && cmake .. && make
```

### 🧪 Testing

```bash
# Run roundtrip tests
python tests/roundtrip/python_roundtrip.py

# Test Go imports
go run examples/go/smoke/main.go

# Test C++ compilation
cd examples/cpp && g++ -I../../gen/cpp smoke.cpp -L../../gen/cpp/build -lampy_proto -lprotobuf -o smoke && ./smoke
```

## 📈 Versioning

This project follows semantic versioning:
- 🔴 **Major versions** (v2, v3): Breaking changes requiring migration
- 🟡 **Minor versions** (v1.1, v1.2): Additive changes, backward compatible
- 🟢 **Patch versions** (v1.0.1, v1.0.2, v1.0.3): Bug fixes, backward compatible

**Current version: v2.0.5**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run `buf lint` and `buf breaking` to ensure compatibility
5. Submit a pull request

### 📋 Schema Evolution Rules

- ✅ **Add new optional fields** with default values
- ✅ **Add new enum values** (append only)
- ✅ **Add new messages** or services
- ❌ **Never change field numbers** of existing fields
- ❌ **Never change field types** of existing fields
- ❌ **Never remove fields** (mark as deprecated instead)
- ❌ **Never renumber enum values**

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 💬 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yeonholee50/ampy-proto/issues)
- 💭 **Discussions**: [GitHub Discussions](https://github.com/yeonholee50/ampy-proto/discussions)
- 📚 **Documentation**: [Project Wiki](https://github.com/yeonholee50/ampy-proto/wiki)

---

---

**This project is part of the AmpyFin ecosystem - a self-learning, modular trading system.**

