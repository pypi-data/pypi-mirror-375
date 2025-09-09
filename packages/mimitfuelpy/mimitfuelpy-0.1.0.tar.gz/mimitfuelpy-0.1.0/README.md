# mimitFuelPy

A Python library for accessing the Mimit Fuel Prices API. This library provides a clean, object-oriented interface for searching fuel stations and retrieving fuel pricing data in Italy.

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [API Coverage](#api-coverage)
- [Documentation](#documentation)
- [Examples](#examples)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Installation

Install mimitfuelpy using pip:

```bash
pip install mimitfuelpy
```

## Quick Start

```python
from mimitfuelpy import Client
from mimitfuelpy.models import FuelType, ServiceType, SearchByBrandCriteria

# Initialize the client
client = Client()

# Search for fuel stations
criteria = SearchByBrandCriteria(
    province="MI",  # Milan
    priceOrder="asc",
    fuelType=FuelType.PETROL.value,
    serviceType=ServiceType.SELF.value
)

results = client.search.byBrand(criteria)
for station in results.results:
    print(f"{station.name}: {station.address}")
```

## Features

- 🚗 **Station Search**: Find fuel stations by location, brand, highway, or zone
- 💰 **Price Data**: Get current fuel prices with filtering options
- 🗺️ **Geographic Data**: Access regions, provinces, towns, and highways
- 📊 **Flexible Filtering**: Filter by fuel type and service type
- 🏢 **Service Areas**: Detailed service area information with facilities
- 🔍 **Easy Integration**: Simple, intuitive API design

## API Coverage

### Registry Operations
- Get all brands and their logos
- Get highways information
- Get regions, provinces, and towns hierarchy
- Get detailed service area information with services and hours

### Search Operations
- Search by geographic zone
- Search by administrative area (province)
- Search by highway
- Search by brand with comprehensive filtering criteria

## Documentation

📖 **Complete documentation is available at: [https://fpetranzan.github.io/mimitFuelPy/](https://fpetranzan.github.io/mimitFuelPy/)**

The documentation includes:

- **[Installation Guide](https://fpetranzan.github.io/mimitFuelPy/installation/)** - Detailed installation instructions
- **[Quick Start Guide](https://fpetranzan.github.io/mimitFuelPy/quick-start/)** - Get up and running quickly
- **[API Reference](https://fpetranzan.github.io/mimitFuelPy/api/)** - Complete API documentation
- **[Examples](https://fpetranzan.github.io/mimitFuelPy/examples/)** - Code examples and use cases
- **[Guides](https://fpetranzan.github.io/mimitFuelPy/guides/)** - In-depth guides and best practices

### Documentation Development

The documentation is built using Jekyll with the "just-the-docs" theme and is automatically deployed to GitHub Pages.

#### Local Documentation Development

```bash
# Install Ruby dependencies
bundle install

# Serve documentation locally
bundle exec jekyll serve

# View at http://localhost:4000
```

#### Documentation Structure

```
docs/
├── index.md              # Homepage
├── installation.md       # Installation guide
├── quick-start.md        # Quick start guide
├── api/                  # API Reference
│   ├── index.md
│   ├── client.md
│   ├── registry.md
│   └── models.md
├── examples/             # Code examples
│   ├── index.md
│   └── basic-usage.md
└── guides/               # In-depth guides
    ├── index.md
    └── getting-started.md
```

## Examples

### Basic Usage

```python
from mimitfuelpy import Client

client = Client()

# Get all brands
brands = client.registry.brands()
print(f"Found {len(brands)} fuel brands")

# Get regions
regions = client.registry.regions()
print(f"Italy has {len(regions)} regions")
```

### Advanced Search

```python
from mimitfuelpy.models import SearchByBrandCriteria, FuelType

# Find cheapest diesel stations in Rome
criteria = SearchByBrandCriteria(
    province="RM",  # Rome
    fuelType=FuelType.DIESEL.value,
    priceOrder="asc"  # Cheapest first
)

results = client.search.byBrand(criteria)
if results.success:
    print(f"Found {len(results.results)} diesel stations")
    for station in results.results[:5]:
        print(f"- {station.name}: {station.address}")
```

See the [`examples/`](examples/) directory and [online documentation](https://fpetranzan.github.io/mimitFuelPy/examples/) for more detailed usage examples.

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/fpetranzan/mimitFuelPy.git
cd mimitFuelPy

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/mimitfuelpy --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Project Structure

```
mimitFuelPy/
├── src/mimitfuelpy/          # Main package
│   ├── api/                  # API modules
│   ├── models/               # Data models
│   ├── utils/                # Utilities
│   └── client.py             # Main client
├── tests/                    # Test suite
├── examples/                 # Usage examples
├── docs/                     # Documentation
└── .github/workflows/        # CI/CD workflows
```

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `pytest tests/`
5. **Format your code**: `black src/ tests/`
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Guidelines

- Write tests for new features
- Follow PEP 8 style guidelines
- Update documentation for API changes
- Ensure all tests pass before submitting

### Reporting Issues

Please use the [GitHub Issues](https://github.com/fpetranzan/mimitFuelPy/issues) page to report bugs or request features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Links:**
- 📦 [PyPI Package](https://pypi.org/project/mimitfuelpy/)
- 📖 [Documentation](https://fpetranzan.github.io/mimitFuelPy/)
- 🐛 [Issue Tracker](https://github.com/fpetranzan/mimitFuelPy/issues)