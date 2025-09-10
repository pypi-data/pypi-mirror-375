import os

import nbformat
import pytest
from attachments import Attachments
from attachments.core import Attachment
from attachments.pipelines.ipynb_processor import ipynb_loader, ipynb_match, ipynb_text_presenter

# Create a dummy IPYNB file for testing
DUMMY_IPYNB_CONTENT = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {},
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": "# Title"},
        {
            "cell_type": "code",
            "metadata": {},
            "execution_count": 1,
            "source": "print('Hello, World!')",
            "outputs": [{"output_type": "stream", "name": "stdout", "text": "Hello, World!\n"}],
        },
        {
            "cell_type": "code",
            "metadata": {},
            "execution_count": 2,
            "source": "1 + 1",
            "outputs": [
                {
                    "output_type": "execute_result",
                    "execution_count": 2,
                    "data": {"text/plain": "2"},
                    "metadata": {},
                }
            ],
        },
        {
            "cell_type": "code",
            "metadata": {},
            "execution_count": 3,
            "source": "raise ValueError('Test Error')",
            "outputs": [
                {
                    "output_type": "error",
                    "ename": "ValueError",
                    "evalue": "Test Error",
                    "traceback": ["Traceback (most recent call last)..."],
                }
            ],
        },
    ],
}

DUMMY_IPYNB_FILENAME = "dummy_notebook.ipynb"


@pytest.fixture(scope="module", autouse=True)
def create_dummy_ipynb():
    notebook_node = nbformat.from_dict(DUMMY_IPYNB_CONTENT)
    with open(DUMMY_IPYNB_FILENAME, "w", encoding="utf-8") as f:
        nbformat.write(notebook_node, f)
    yield
    os.remove(DUMMY_IPYNB_FILENAME)


def test_ipynb_match():
    """Test that ipynb_match correctly identifies IPYNB files."""
    att_ipynb = Attachment("test.ipynb")
    att_txt = Attachment("test.txt")
    assert ipynb_match(att_ipynb) is True
    assert ipynb_match(att_txt) is False


def test_ipynb_loader():
    """Test that ipynb_loader correctly loads and parses an IPYNB file."""
    att = Attachment(DUMMY_IPYNB_FILENAME)
    loaded_att = ipynb_loader(att)
    assert loaded_att._obj is not None
    assert isinstance(loaded_att._obj, nbformat.NotebookNode)
    assert len(loaded_att._obj.cells) == 4


def test_ipynb_presenter():
    """Test that the IPYNB presenter converts notebook content to text correctly."""
    att = Attachment(DUMMY_IPYNB_FILENAME)
    loaded_att = ipynb_loader(att)
    presented_att = ipynb_text_presenter(loaded_att, loaded_att._obj)

    expected_text = """\
# Title

```python
print('Hello, World!')
```
Output:
```
Hello, World!
```

```python
1 + 1
```
Output:
```
2
```

```python
raise ValueError('Test Error')
```
Error:
```
ValueError: Test Error
```"""
    assert presented_att.text.strip() == expected_text.strip()


def test_ipynb_processor_integration():
    """Test the full IPYNB processor pipeline."""
    attachments = Attachments(DUMMY_IPYNB_FILENAME)
    assert len(attachments) == 1
    att = attachments[0]
    assert att.path == DUMMY_IPYNB_FILENAME

    expected_text = """\
# Title

```python
print('Hello, World!')
```
Output:
```
Hello, World!
```

```python
1 + 1
```
Output:
```
2
```

```python
raise ValueError('Test Error')
```
Error:
```
ValueError: Test Error
```"""
    # Normalize whitespace for comparison
    processed_text_normalized = "\n".join(
        line.strip() for line in att.text.strip().splitlines() if line.strip()
    )
    expected_text_normalized = "\n".join(
        line.strip() for line in expected_text.strip().splitlines() if line.strip()
    )

    assert processed_text_normalized == expected_text_normalized


def test_ipynb_processor_with_empty_notebook():
    """Test the processor with an empty IPYNB file."""
    EMPTY_IPYNB_FILENAME = "empty_notebook.ipynb"
    empty_content = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": []}
    empty_notebook_node = nbformat.from_dict(empty_content)
    with open(EMPTY_IPYNB_FILENAME, "w", encoding="utf-8") as f:
        nbformat.write(empty_notebook_node, f)

    attachments = Attachments(EMPTY_IPYNB_FILENAME)
    assert len(attachments) == 1
    att = attachments[0]
    assert att.text == ""

    os.remove(EMPTY_IPYNB_FILENAME)


def test_ipynb_processor_with_markdown_only():
    """Test the processor with an IPYNB file containing only markdown."""
    MARKDOWN_ONLY_FILENAME = "markdown_only.ipynb"
    markdown_content = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": "## Section 1\nSome text here."},
            {"cell_type": "markdown", "metadata": {}, "source": "### Subsection 1.1\nMore text."},
        ],
    }
    markdown_notebook_node = nbformat.from_dict(markdown_content)
    with open(MARKDOWN_ONLY_FILENAME, "w", encoding="utf-8") as f:
        nbformat.write(markdown_notebook_node, f)

    attachments = Attachments(MARKDOWN_ONLY_FILENAME)
    assert len(attachments) == 1
    att = attachments[0]
    expected_text = "## Section 1\nSome text here.\n\n### Subsection 1.1\nMore text."
    assert att.text.strip() == expected_text.strip()

    os.remove(MARKDOWN_ONLY_FILENAME)


def test_ipynb_processor_with_code_only_no_output():
    """Test the processor with an IPYNB file containing only code cells without output."""
    CODE_ONLY_NO_OUTPUT_FILENAME = "code_only_no_output.ipynb"
    code_content = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": 1,
                "source": "x = 10\ny = 20",
                "outputs": [],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,  # Unexecuted cell
                "source": "print(x + y)",
                "outputs": [],
            },
        ],
    }
    code_notebook_node = nbformat.from_dict(code_content)
    with open(CODE_ONLY_NO_OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        nbformat.write(code_notebook_node, f)

    attachments = Attachments(CODE_ONLY_NO_OUTPUT_FILENAME)
    assert len(attachments) == 1
    att = attachments[0]
    expected_text = """\
```python
x = 10
y = 20
```

```python
print(x + y)
```"""
    assert att.text.strip() == expected_text.strip()

    os.remove(CODE_ONLY_NO_OUTPUT_FILENAME)
