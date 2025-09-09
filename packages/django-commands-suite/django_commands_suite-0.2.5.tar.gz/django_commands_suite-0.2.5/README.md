# Django Commands Suite (DCS)

**Django Commands Suite** is a Django app that provides a **powerful suite of management commands** for your projects.  
It helps automate repetitive tasks such as:

- Database backup
- Creating superusers quickly
- Seeding fake data
- Cache management
- Logging command executions
- Running custom commands via Web Terminal

---

## Installation

Install via pip:

```bash
pip install django-commands-suite
```

Add it to `INSTALLED_APPS` in your Django settings:

```python
INSTALLED_APPS = [
    ...
    'django_commands_suite',
]
```

Run migrations to create necessary tables:

```bash
python manage.py makemigrations django_commands_suite
python manage.py migrate
```

---

## Usage

### 1. Django Commands

View all DCS commands:

```bash
python manage.py dcs_help
```

Create a superuser quickly:

```bash
python manage.py quick_superuser
```

Backup your database:

```bash
python manage.py backup_db
```

Seed fake data for a model:

```bash
python manage.py dummy_data --model myapp.MyModel --count 10
```

---

### 2. Web Terminal

DCS provides a **Web Terminal** to run commands from the browser:

- URL: `/dcs/terminal/`
- Supports custom DCS commands  
- Example commands :

```text
quick_superuser # Creates a superuser
```

---

## Logging

All commands run via DCS (CLI or Web Terminal) are logged automatically using `CommandLog`.  
This allows you to keep track of:

- Who ran a command
- When it was run
- Output and status (success or error)

Example usage of logging in a custom command:

```python
from django_commands_suite.utils import log_command

log_command("my_command", {"option": "value"}, "success", "Command output here")
```

---

## Custom DCS Commands

You can define your own commands prefixed with `dcs_` for Web Terminal usage.  
Example:

```python
from django.core.management.base import BaseCommand
from django_commands_suite.utils import log_command

class Command(BaseCommand):
    help = "Say hello"

    def handle(self, *args, **kwargs):
        msg = "Hello from DCS!"
        self.stdout.write(msg)
        log_command("dcs_hello", {}, "success", msg)
```

---

## Utility Function: `run_command`

`run_command` allows you to run any Django management command from code and automatically logs its output and status in `CommandLog`.

### Signature

```python
run_command(command_name: str, *args, **kwargs)
```

### Parameters

- `command_name` (str): Django command name (`"quick_superuser"`, etc.)
- `*args`: Positional arguments for the command
- `**kwargs`: Keyword arguments/options for the command

### Example Usage

```python
from django_commands_suite.utils import run_command

# Run quick_superuser
output = run_command("quick_superuser")
print(output)

```

This function is great for **automation scripts**, **seeders**, or **custom management tasks** in Django projects.

---





## Contributing

Contributions are welcome!  
Feel free to:

- Open issues
- Submit pull requests
- Suggest new commands

---

## License

MIT License

