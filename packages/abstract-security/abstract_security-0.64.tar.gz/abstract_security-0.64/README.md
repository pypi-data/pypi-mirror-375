## Abstract Security

The `abstract_security` module is a Python utility that provides functionality for managing environment variables and securely loading sensitive information from `.env` files. It is designed to simplify the process of accessing and managing environment variables within your Python applications.

## Table of Contents

- [Features](#features)
- [Installation](#installationn)
- [Usage](#usage)
- [Functions](#functions)
- [License](#license)
- [Contact](#contact)

### Features
- **Flexible `.env` File Location**: Searches for `.env` files in current working directory, home directory, and a special `.envy_all` directory within the home directory.
- **Clean and Secure Key Retrieval**: Offers functionality to cleanly split strings at equals signs and safely retrieve environment variable values.

## Installation

Install `abstract_security` using pip:

```bash
pip install abstract-security
```

## Usage

### Basic Usage
Here's a simple example to get started:

```python
from abstract_security import get_env_value

env_key = 'YOUR_ENV_VARIABLE_KEY'
value = get_env_value(key=env_key)
```

### Advanced Usage
The `AbstractEnv` class can be used for more advanced scenarios, including custom paths and file names for the `.env` file.

```python
from abstract_security import AbstractEnv

# Initialize with custom parameters
abstract_env = AbstractEnv(key='YOUR_ENV_VARIABLE_KEY', file_name='custom.env', path='/custom/path')
value = abstract_env.env_value
```

##Functions 

### `AbstractEnv` Class

The `AbstractEnv` class allows you to manage environment variables and securely load values from a `.env` file. Here's how to use it:

#### Initializing an `AbstractEnv` Object

```python
# Create an AbstractEnv object with default settings
abstract_env = AbstractEnv()
```

You can also customize the initialization by specifying the key, file name, and path as follows:

```python
# Custom initialization
abstract_env = AbstractEnv(key='MY_PASSWORD', file_name='.env', path='/path/to/.env')
```

#### Getting Environment Variable Values

You can retrieve the value of a specific environment variable using the `get_env_value` method of the `AbstractEnv` object:

```python
# Retrieve the value of a specific environment variable
value = abstract_env.get_env_value(key='YOUR_ENV_VARIABLE')
```

### `get_env_value` Function

Alternatively, you can use the `get_env_value` function to directly retrieve the value of an environment variable without creating an `AbstractEnv` object:

```python
from abstract_security import get_env_value

# Retrieve the value of a specific environment variable
value = get_env_value(key='YOUR_ENV_VARIABLE', path='/path/to/.env')
```

## API Reference

### `AbstractEnv` Class

#### `AbstractEnv(key='MY_PASSWORD', file_name='.env', path=os.getcwd())`

Initializes an `AbstractEnv` object to manage environment variables.

- `key` (str, optional): The key to search for in the `.env` file. Defaults to 'MY_PASSWORD'.
- `file_name` (str, optional): The name of the `.env` file. Defaults to '.env'.
- `path` (str, optional): The path where the `.env` file is located. Defaults to the current working directory.

#### `re_initialize(key='MY_PASSWORD', file_name='.env', path=os.getcwd())`

Re-initializes an `AbstractEnv` object with new settings.

- `key` (str, optional): The key to search for in the `.env` file. Defaults to 'MY_PASSWORD'.
- `file_name` (str, optional): The name of the `.env` file. Defaults to '.env'.
- `path` (str, optional): The path where the `.env` file is located. Defaults to the current working directory.

#### `get_env_value(key='MY_PASSWORD', path=os.getcwd(), file_name='.env')`

Retrieves the value of the specified environment variable.

- `key` (str): The key to search for in the `.env` file.
- `path` (str): The path to the environment file.
- `file_name` (str): The name of the environment file.

### `get_env_value` Function

#### `get_env_value(key=None, path=None, file_name=None)`

Retrieves the value of a specified environment variable from a `.env` file.

- `key` (str, optional): The key to search for in the `.env` file. Defaults to None.
- `path` (str, optional): The path to the `.env` file. Defaults to None.
- `file_name` (str, optional): The name of the `.env` file. Defaults to None.

## License

This module is distributed under the [MIT License](LICENSE).

---

For more information and usage examples, please refer to the [GitHub repository](https://github.com/AbstractEndeavors/abstract_security) and [PyPI package](https://pypi.org/project/abstract-security/).

If you encounter any issues or have questions, feel free to open an issue on GitHub or contact the author, putkoff, for assistance.
## Contact

**Author**: putkoff  
**Email**: partners@abstractendeavors.com  
**Project Link**: [https://github.com/AbstractEndeavors/abstract_security](https://github.com/AbstractEndeavors/abstract_security)

