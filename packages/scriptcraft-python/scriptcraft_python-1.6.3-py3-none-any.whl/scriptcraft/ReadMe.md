# ScriptCraft Python Package

A comprehensive Python package for data processing and quality control tools designed for research workflows.

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install scriptcraft-python

# Install from GitHub (development)
pip install git+https://github.com/mcusac/ScriptCraft-Workspace.git#subdirectory=implementations/python-package

# Install in development mode (from workspace)
cd implementations/python-package
pip install -e .
```

### Basic Usage

```python
# Import the package
import scriptcraft
import scriptcraft.common as cu

# Check version
print(f"ScriptCraft version: {scriptcraft.__version__}")

# Use common utilities
data = cu.load_data("your_data.csv")
cu.log_and_print("✅ Data loaded successfully")
```

## 🛠️ Tool Usage Patterns

### Pattern 1: Direct Tool Import (Recommended)

```python
from scriptcraft.tools.automated_labeler import AutomatedLabeler
from scriptcraft.tools.data_content_comparer import DataContentComparer

# Create and use tools
labeler = AutomatedLabeler()
comparer = DataContentComparer()

# Run with arguments
labeler.run(
    input_paths=["data.csv"],
    output_dir="output",
    mode="labeling"
)
```

### Pattern 2: Tool Discovery

```python
from scriptcraft.tools import get_available_tools

# Get all available tools
tools = get_available_tools()
print("Available tools:", list(tools.keys()))

# Use a tool dynamically
tool_class = tools["automated_labeler"]
tool_instance = tool_class()
```

### Pattern 3: Common Utilities

```python
import scriptcraft.common as cu

# Create a custom tool
class MyTool(cu.BaseTool):
    def __init__(self):
        super().__init__(
            name="My Tool",
            description="Custom tool description",
            tool_name="my_tool"
        )
    
    def run(self, input_paths, output_dir=None, **kwargs):
        # Your logic here
        cu.log_and_print("🚀 Processing data...")
        # Process data
        cu.log_and_print("✅ Processing complete")
```

## 🧰 Available Tools

### Data Processing
- **AutomatedLabeler**: Automated data labeling and classification
- **DataContentComparer**: Compare datasets for consistency
- **SchemaDetector**: Automatic schema detection and validation
- **DateFormatStandardizer**: Standardize date formats across datasets

### Validation & Quality Control
- **DictionaryDrivenChecker**: Validation using predefined dictionaries
- **DictionaryValidator**: Validate dictionary structures
- **FeatureChangeChecker**: Detect changes in data features
- **MedVisitIntegrityValidator**: Validate medical visit data integrity
- **ScoreTotalsChecker**: Validate score calculations

### Data Transformation
- **DictionaryCleaner**: Clean and validate dictionary files
- **DictionaryWorkflow**: Complete dictionary processing workflows

### Automation
- **RHQFormAutofiller**: Automated form filling for research questionnaires

### Development Tools
- **FunctionAuditor**: Audit unused functions in codebases
- **ReleaseManager**: Automated release management

## 🔧 CLI Usage

### Console Scripts

```bash
# Available console scripts
rhq-autofiller --help
data-comparer --help
auto-labeler --help
function-auditor --help
scriptcraft --help
```

### Direct Module Execution

```bash
# Run tools directly
python -m scriptcraft.tools.rhq_form_autofiller --help
python -m scriptcraft.tools.data_content_comparer --help
python -m scriptcraft.tools.automated_labeler --help
```

## 📚 Common Utilities

### Data Operations

```python
import scriptcraft.common as cu

# Load data
data = cu.load_data("file.csv")

# Save data
cu.save_data(data, "output.xlsx")

# Compare dataframes
result = cu.compare_dataframes(df1, df2)
```

### Logging

```python
# Setup logger
logger = cu.setup_logger("my_tool")

# Log with emojis
cu.log_and_print("🚀 Starting process")
cu.log_and_print("✅ Process completed")
cu.log_and_print("❌ Error occurred", level="error")
```

### Configuration

```python
# Load configuration
config = cu.Config.from_yaml("config.yaml")

# Get tool configuration
tool_config = config.get_tool_config("my_tool")
```

## 🔄 Pipeline Usage

```python
from scriptcraft.pipelines import BasePipeline, PipelineStep

# Create a pipeline
pipeline = BasePipeline(config, "My Pipeline")

# Add steps
step = PipelineStep(
    name="validation",
    log_filename="validation.log",
    qc_func=my_validation_function,
    input_key="raw_data"
)
pipeline.add_step(step)

# Run pipeline
pipeline.run()
```

## 🧪 Testing

```python
# Test imports
import scriptcraft
import scriptcraft.common as cu
from scriptcraft.tools import get_available_tools

# Test tool discovery
tools = get_available_tools()
assert len(tools) > 0

# Test specific tool
from scriptcraft.tools.automated_labeler import AutomatedLabeler
tool = AutomatedLabeler()
assert tool.name == "Automated Labeler"
```

## 📖 Advanced Usage

### Custom Tool Creation

```python
import scriptcraft.common as cu

class CustomTool(cu.BaseTool):
    def __init__(self):
        super().__init__(
            name="Custom Tool",
            description="My custom tool",
            tool_name="custom_tool",
            requires_dictionary=True
        )
    
    def run(self, input_paths, output_dir=None, **kwargs):
        # Your custom logic here
        pass

# Use the tool
tool = CustomTool()
tool.run(input_paths=["data.csv"], output_dir="output")
```

### Plugin System

```python
from scriptcraft.common.registry import register_tool_decorator

@register_tool_decorator("my_plugin_tool")
class PluginTool(cu.BaseTool):
    def run(self, **kwargs):
        # Plugin logic
        pass
```

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the correct directory or have installed the package
2. **Tool Not Found**: Check that the tool name matches exactly (use underscores, not hyphens)
3. **Configuration Issues**: Ensure `config.yaml` exists or use environment variables

### Getting Help

```python
# Check available tools
from scriptcraft.tools import get_available_tools
tools = get_available_tools()
print("Available tools:", list(tools.keys()))

# Get tool help
from scriptcraft.tools.automated_labeler import AutomatedLabeler
tool = AutomatedLabeler()
print(tool.description)
```

---

**ScriptCraft Python Package** - Making research data processing easier, one tool at a time.
