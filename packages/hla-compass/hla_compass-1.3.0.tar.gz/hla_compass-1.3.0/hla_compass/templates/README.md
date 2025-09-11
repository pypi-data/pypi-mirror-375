# HLA-Compass Module Templates

This directory contains two main templates for developing HLA-Compass modules:

## 📱 UI Template (`ui-template/`)
For modules that need a user interface. Includes:
- **Backend**: Python module with UI-friendly response formatting
- **Frontend**: React/TypeScript UI with forms, tables, and data visualization
- **Styling**: Tailwind CSS + scientific design system matching the platform
- Input validation and error handling
- Results display with summary statistics
- Expandable detail views
- Consistent visual design with HLA-Compass platform

### When to use:
- Interactive data exploration
- User-driven analysis
- Visual results presentation
- Parameter configuration interfaces

### Key files:
- `backend/main.py` - Module logic with UI formatting
- `frontend/index.tsx` - React component with platform-matching design
- `frontend/styles.css` - Scientific styling system
- `frontend/tailwind.config.js` - Design system configuration

## 🔧 No-UI Template (`no-ui-template/`)
For backend-only modules without user interface. Includes:
- Batch processing capabilities
- API response formatting
- Data source flexibility (files, S3, direct input)
- Progress tracking
- Comprehensive error handling

### When to use:
- Automated workflows
- Batch data processing
- API integrations
- Scheduled jobs
- Pipeline components

### Key files:
- `backend/main.py` - Backend processing logic

## Quick Start

### 1. Choose your template:
```bash
# For UI modules
cp -r ui-template/ my-module/

# For backend-only modules
cp -r no-ui-template/ my-module/
```

### 2. Update the module:
- Replace TODOs with your implementation
- Update class names and descriptions
- Add your business logic
- Configure data sources

### 3. For UI modules - Setup frontend:
```bash
cd my-module/frontend/
npm install
npm run dev  # Development server
npm run build  # Production build
```

#### Available styling features:
- **Tailwind CSS**: Utility-first CSS framework
- **Scientific design system**: Colors and spacing optimized for data
- **Platform consistency**: Matches HLA-Compass main interface
- **Responsive design**: Mobile-friendly layouts
- **Accessibility**: Screen reader and keyboard navigation support

### 4. Key methods to implement:

#### `execute()` - Main processing function
```python
def execute(self, input_data, context):
    # Your core logic here
    return self.success(results=processed_data)
```

#### `_validate_input()` - Input validation
```python
def _validate_input(self, input_data):
    # Validate required fields and formats
    return {'valid': True}  # or {'valid': False, 'message': 'error'}
```

#### `_process_data()` - Core processing logic
```python
def _process_data(self, data):
    # Transform, analyze, or process data
    return results
```

## Available SDK Features

Both templates have access to:

### Data Access
- `self.peptides.search()` - Search peptide database
- `self.storage.save()` - Save to S3/filesystem
- `self.storage.load()` - Load from S3/filesystem

### Logging
- `self.logger.info()` - Information logs
- `self.logger.error()` - Error logs
- `self.logger.warning()` - Warning logs

### Response Helpers
- `self.success()` - Return success response
- `self.error()` - Return error response

## Testing Your Module

```python
# Local testing
module = YourModule()
result = module.execute(
    input_data={'param1': 'value'},
    context={'job_id': 'test-123'}
)
print(result)
```

## Deployment

Both templates include a `lambda_handler` function for AWS Lambda deployment:

```python
def lambda_handler(event, context):
    module = YourModule()
    return module.handle_lambda(event, context)
```

## Best Practices

1. **Always validate input** - Check types, ranges, and required fields
2. **Use batch processing** - Process large datasets in chunks
3. **Log important events** - Help with debugging and monitoring
4. **Handle errors gracefully** - Return meaningful error messages
5. **Document your code** - Update docstrings and comments
6. **Test thoroughly** - Include unit tests in your module

## Need Help?

- Check the existing templates for examples
- Review the SDK documentation
- Contact the platform team for support