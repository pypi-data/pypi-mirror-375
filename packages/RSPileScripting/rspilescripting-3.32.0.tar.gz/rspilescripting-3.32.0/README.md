# RSPile Python Library

## Introduction
This project is a Python library designed to interact with RSPile by Rocscience Inc. through scripting. It enables users to automate and control RSPile operations programmatically, facilitating more efficient workflows and enabling advanced automation.

### Goal
Each function provided by this library corresponds to an operation that can be performed through the RSPile user interface. The goal is to allow users to create, edit, and analyze models directly from Python without needing to manually interact with the UI. For details on what is currently supported, see [Exposed Functionality](#exposed-functionality).

### Python UI Equivalents
Actions performed in the RSPile UI have equivalents in this Python library. For every dialog box in the UI, there is a corresponding class with methods that mimic the behavior of that dialog. If a warning or error dialog would appear in the UI, the library will raise an exception or display a warning in Python. Entities in RSPile can be referenced and manipulated using identifiers, which the library will translate into objects that users can work with directly in Python.

### How it Works
The library functions as a wrapper around API calls to the RSPile application. Objects obtained through function calls often serve as proxies rather than containing data themselves. This design allows users to retrieve and interact with data within the application, although debugging may require additional steps to inspect data by assigning it to variables.

### Warnings
References to objects in RSPile can become invalid when those objects are destroyed or reloaded within the application. Users must monitor and refresh expired references to avoid crashes or incorrect results. Functions that may invalidate objects are marked with warnings, indicating which objects need to be reloaded.

## Exposed Functionality
The current set of functionality exposed is limited. With this version of the library, you can:  
- Open/Close RSPile Application
- Open/Save/Close Model
- Modify Soil properties
- Modify Pile Sections
- Modify Pile Types
- Compute Model
- Obtain tabular results data 
- Query results data for max/min values for specific piles or across all piles. 

## Getting Started

### Installation
 in [Build](#build).
To install the RSPile Python Library, run:
```bash
pip install RSPileScripting
```

### Getting Started Guide

**Getting Started**
https://www.rocscience.com/help/rspile/tutorials/tutorial-overview/19-getting-started-with-rspile-python-scripting

**First Tutorial**
https://www.rocscience.com/help/rspile/tutorials/tutorial-overview/20-lateral-pile-analysis-optimization

# For Contributors

## Build
To build the library, ensure Python is installed, then follow these steps:
1. Install the Python build module:
    ```bash
    python -m pip install --upgrade build
    ```
2. Build and reinstall the library:
    ```bash
    pip install dist/RSPileScripting-3.32.0-py3-none-any.whl --force-reinstall
    ```

To rebuild and reinstall the library after updates:
    ```bash
    ./update_generated_files.bat
    ```

## Unit Testing

To maintain code quality and ensure functionality, unit tests have been implemented using the `unittest` framework. See the official documentation for more details: [unittest documentation](https://docs.python.org/3/library/unittest.html).

### Creating Unit Tests
**Directory Structure:**  
- Add new test files to the `tests` directory.
- Store any necessary RSPile files in the `tests/resources` directory.

**Handling Test Resources:**  
Avoid modifying the base files directly. Instead, create copies during each test's setup and delete them during teardown to preserve the original files.

### Running Unit Tests
Before running tests, Build the RSPile library as described in the [Build](#build) section.

To run all tests:
```bash
python -m unittest discover -s tests
```

To run a specific test file:
```bash
python -m unittest discover -s tests -p "<testFile>.py"
```

For more verbose output:
```bash
python -m unittest discover -v -s tests
```

## Code Coverage
To measure the code coverage of your tests, you can use the coverage tool.

### Installing Coverage
To install the coverage tool, run:

```bash
pip install coverage
```

### Running Tests with Coverage
To run your tests with code coverage, use the following command:

```bash
coverage run --source=RSPileScripting -m unittest discover -s tests
```

### Generating a Coverage Report
To generate a coverage report, run:

```bash
coverage report
```
This will display a summary of the coverage data, including the percentage of code covered by your tests.

### Generating a Detailed Coverage Report
To generate a detailed coverage report, run:

```bash
coverage html
```
This will generate an HTML report showing the coverage data for each file.

## Documentation
The following steps can be taken to regenerate the RSPile Scripting Documentation:
1. Rebuild the RSPile library by following the [Build](#build) section.
2. Install the required packages.
```pip install -r requirements.txt```
1. To run all example files and generate the documentation run the following:  
```python generateAndBuildDocumentation.py```  

"examples.rst" and "index.rst" files are manually written and should be manually modified. "generateAndBuildDocumentation.py" will not overwrite them.

Rocscience logo is saved under _static folder.

### Adding To Documentation
The following steps can be taken to add a new object to the autogenerated documentation:
1. Ensure automatic generation of the documentation for the new object has been completed. 
2. To include an example code snippet, ensure a docstring is added at the top of the object ```.py``` file, which will link to the example.  
   See Below:    
   ```
	"""
	:ref:`Soil Example`
	"""
   ```
3. Add your example code snippet to ```\RSPile Python Client Library\docs\example_code```
4. Open examples.rst and following the format of the existing example links, add a link to your code example. Ensure that your link label matches the link label being generated in Step 2.  
   See Below:  
	```
	.. _Soil Example:
	```
5. Follow the steps in [Documentation](#documentation) to regenerate the new documentaiton.

## Contribution Guidelines
Contributions are welcomed to improve RSPile's Scripting Features. To make a contribution, follow the guidelines below:
1. **Make Changes:** Start by making the necessary changes to the relevant `.py` file(s) to address the task or implement new features.
2. **Install Dependencies:** Install the required dependencies specified in the `requirements.txt` file, as explained in the [Build](#build) section. It is recommended that these dependencies be installed within a virtual environment.
3. **Python Interpreter:** Select the same Python interpreter used to install the package. You can specify the interpreter in your virtual environment or project settings.
4. **Testing:** Thoroughly test your changes to ensure they meet the project's requirements and do not introduce regressions. Consult the [Unit Testing](#unit-testing) section for more information. Include additional test cases to cover modifications to the project.
5. **Pull Request:** After thorough testing and review, submit a pull request which describes the purpose of your changes. After review and approval, merge your changes into the main branch.