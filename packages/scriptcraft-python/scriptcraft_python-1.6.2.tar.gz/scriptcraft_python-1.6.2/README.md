# ScriptCraft Python Package

A comprehensive Python package for data processing and quality control tools designed for research workflows, particularly in the field of Huntington's Disease research.

## 🚀 Features

- **Data Processing Tools**: Automated data cleaning, validation, and transformation
- **Quality Control**: Comprehensive validation frameworks with plugin support
- **Research Workflows**: Specialized tools for clinical and biomarker data
- **Release Management**: Automated PyPI and Git release workflows
- **Pipeline Orchestration**: Multi-step workflow automation
- **Extensible Architecture**: Plugin-based system for custom validations
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📦 Installation

```bash
pip install scriptcraft
```

## 🛠️ Quick Start

### Basic Usage

```python
import scriptcraft
import scriptcraft.common as cu

# Use common utilities
data = cu.load_data("your_data.csv")
cu.log_and_print("✅ Data loaded successfully")
```

### Using Tools

```python
# Import tools directly
from scriptcraft.tools.automated_labeler import AutomatedLabeler
from scriptcraft.tools.data_content_comparer import DataContentComparer

# Create and use tools
labeler = AutomatedLabeler()
comparer = DataContentComparer()

# Run tools with arguments
labeler.run(
    input_paths=["data.csv"],
    output_dir="output",
    mode="labeling"
)
```

### CLI Usage

```bash
# List available tools and pipelines
scriptcraft list

# Run specific tools
scriptcraft rhq_form_autofiller
scriptcraft data_content_comparer

# Run pipelines
scriptcraft data_quality
scriptcraft dictionary_pipeline

# Use release management CLI
scriptcraft-release pypi-test
scriptcraft-release git-sync
scriptcraft-release full-release

# Use release manager directly (RECOMMENDED for version bumps)
python -c "from scriptcraft.tools.release_manager import ReleaseManager; ReleaseManager().run(mode='python_package', version_type='patch', auto_push=True)"

# Run specific tools via console scripts
rhq-autofiller --help
data-comparer --help
auto-labeler --help
function-auditor --help

# Or run tools directly
python -m scriptcraft.tools.rhq_form_autofiller --help
python -m scriptcraft.tools.data_content_comparer --help
```

## 🧰 Available Tools

### Data Processing
- **AutomatedLabeler**: Automated data labeling and classification
- **DataContentComparer**: Compare datasets for consistency
- **SchemaDetector**: Automatic schema detection and validation
- **DateFormatStandardizer**: Standardize date formats across datasets
- **DictionaryCleaner**: Clean and validate dictionary files

### Quality Control
- **DictionaryDrivenChecker**: Validation using predefined dictionaries
- **DictionaryValidator**: Validate dictionary structures
- **MedVisitIntegrityValidator**: Validate medical visit data integrity
- **ScoreTotalsChecker**: Validate score calculations
- **FeatureChangeChecker**: Detect changes in data features

### Automation
- **RHQFormAutofiller**: Automated form filling for research questionnaires
- **DictionaryWorkflow**: Complete dictionary processing workflows

### Release Management
- **PyPIReleaseTool**: Automated PyPI package testing and release
- **GitWorkspaceTool**: Git repository management and operations
- **GitSubmoduleTool**: Git submodule synchronization and management
- **GenericReleaseTool**: Flexible release workflow orchestration

## 🔧 Development

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/scriptcraft-python.git
cd scriptcraft-python

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
```

## 📚 Documentation

For comprehensive documentation, examples, and advanced usage:

- **Main Documentation**: [ScriptCraft Workspace](https://github.com/yourusername/ScriptCraft-Workspace)
- **Tool Documentation**: See individual tool README files
- **API Reference**: Available in the main workspace documentation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/yourusername/ScriptCraft-Workspace/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/scriptcraft-python/issues)
- **Documentation**: [ScriptCraft Workspace](https://github.com/yourusername/ScriptCraft-Workspace)
- **Email**: scriptcraft@example.com

## 🙏 Acknowledgments

- Built for the Huntington's Disease research community
- Developed with support from research institutions
- Thanks to all contributors and users

---

**ScriptCraft Python Package** - Making research data processing easier, one tool at a time. 