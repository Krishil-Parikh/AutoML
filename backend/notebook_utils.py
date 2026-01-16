import json
import os


def _build_notebook_structure(log_steps):
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    def create_code_cell(source_lines):
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in source_lines],
        }

    def create_markdown_cell(text):
        return {"cell_type": "markdown", "metadata": {}, "source": [text]}

    imports = [
        "import pandas as pd",
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        "from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder",
        "%matplotlib inline",
        "import warnings",
        "warnings.filterwarnings('ignore')",
    ]
    notebook["cells"].append(create_code_cell(imports))

    for step_name, code_lines in log_steps:
        notebook["cells"].append(create_markdown_cell(f"### {step_name}"))
        notebook["cells"].append(create_code_cell(code_lines))

    return notebook


def save_to_ipynb(log_steps, filename="preprocessing_workflow.ipynb"):
    if not filename.endswith(".ipynb"):
        filename += ".ipynb"

    notebook = _build_notebook_structure(log_steps)

    try:
        with open(filename, "w") as f:
            json.dump(notebook, f, indent=4)
        print(f"\nSuccessfully generated notebook: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"Error saving notebook: {e}")


def notebook_bytes(log_steps):
    notebook = _build_notebook_structure(log_steps)
    return json.dumps(notebook, indent=4).encode("utf-8")
