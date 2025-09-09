# Rhamaa CLI

Simple CLI tool for Wagtail development with prebuilt apps and project scaffolding.

## 🚀 Features

- **Quick Project Setup** - Create Wagtail projects instantly
- **Prebuilt Apps** - Install ready-to-use applications  
- **Simple Commands** - Just two main commands
- **Rich UI** - Beautiful terminal interface

## 📦 Available Apps

| App | Category | Description |
|-----|----------|-------------|
| **mqtt** | IoT | MQTT integration for real-time messaging |
| **users** | Auth | Advanced user management system |
| **articles** | Content | Blog and article management |
| **lms** | Education | Learning Management System |
| **ecommerce** | Commerce | E-commerce functionality |

## 🛠 Installation

```bash
pip install rhamaa
```

## 📖 Usage

### Create Project
```bash
rhamaa start MyProject
```

### Create Apps
```bash
# Minimal Django app (default)
rhamaa startapp blog

# Wagtail app with templates
rhamaa startapp pages --type wagtail

# Install prebuilt app
rhamaa startapp iot --prebuild mqtt

# List available prebuilt apps
rhamaa startapp --list
```

### Quick Start
```bash
# Create project
rhamaa start MyBlog
cd MyBlog

# Install blog functionality
rhamaa startapp articles --prebuild articles

# Add to INSTALLED_APPS and run migrations
python manage.py makemigrations
python manage.py migrate
```

## 🏗 Project Structure

```
rhamaa/
├── __init__.py             # Package initialization
├── cli.py                  # Main CLI entry point and help system
├── registry.py             # App registry management
├── utils.py                # Utility functions (download, extract)
└── commands/               # Command modules directory
    ├── __init__.py         # Commands package init
    ├── add.py              # 'add' command implementation
    ├── start.py            # 'start' command implementation
    └── registry.py         # 'registry' command implementation
```

## 🔧 Development

### Adding New Apps to Registry
Edit `rhamaa/registry.py`:
```python
APP_REGISTRY = {
    "your_app": {
        "name": "Your App Name",
        "description": "App description",
        "repository": "https://github.com/RhamaaCMS/your-app",
        "branch": "main",
        "category": "Category"
    }
}
```

### Testing Commands
```bash
# Test main command
rhamaa

# Test project creation
rhamaa start TestProject

# Test app installation
rhamaa add mqtt

# Test registry commands
rhamaa registry list
rhamaa registry info mqtt
```

### Building Distribution
```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Install from local build
pip install dist/rhamaa-*.whl
```

## 🎯 Use Cases

### For Wagtail Developers
- Quickly bootstrap new projects with proven architecture
- Add common functionality without writing from scratch
- Standardize project structure across team

### For Teams
- Consistent project setup across developers
- Reusable components and applications
- Faster development cycles

### For IoT Projects
- MQTT integration with `rhamaa add mqtt`
- Real-time data monitoring and management
- Wagtail admin integration for IoT devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the RhamaaCMS ecosystem.

## 🔗 Links

- **Documentation**: [GitHub Wiki](https://github.com/RhamaaCMS/RhamaaCLI/wiki)
- **Issues**: [GitHub Issues](https://github.com/RhamaaCMS/RhamaaCLI/issues)
- **RhamaaCMS**: [Main Repository](https://github.com/RhamaaCMS)

---

Made with ❤️ by the RhamaaCMS team
