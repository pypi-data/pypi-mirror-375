def as_details(summary, content):
    """
    ```python
    >>> as_details("summary", "content")
    '<details class="example" style="border: none;"><summary>summary</summary>content</details>'

    ```
    """
    return f"""<details class="example" style="border: none;">
<summary>{summary}</summary>
{content}</details>""".replace("\n", "")


def markdown_escape_square_braces(text):
    """
    ```python
    >>> print(markdown_escape_square_braces("[h1]h1[/h1]"))
    \\[h1\\]h1\\[/h1\\]

    ```
    """

    return text.replace("[", "\\[").replace("]", "\\]")
