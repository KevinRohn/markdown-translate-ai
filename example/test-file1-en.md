# Guide to Using Markdown for Documentation

Markdown is a lightweight markup language that is widely used for formatting text. It is simple to learn and allows you to create well-structured documents with ease. Below is a guide to some of the most commonly used Markdown syntax.

## Headings

Headings are created using the `#` symbol. The number of `#` symbols indicates the level of the heading. For example:

# Heading 1
## Heading 2
### Heading 3

Text Formatting
You can format text using the following syntax:

Bold: **bold text**

Italic: *italic text*

~~Strikethrough~~: ~~strikethrough text~~

## Lists

Markdown supports both ordered and unordered lists.

**Unordered List**

- Item 1
- Item 2
  - Subitem 2.1
  - Subitem 2.2

**Ordered List**

1. First item
2. Second item
   1. Subitem 2.1
   2. Subitem 2.2

## Links and Images

You can add links and images using the following syntax:

Link: [Google](https://www.google.com)
Image: ![Alt text](https://www.google.de/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png)

## Code Blocks

To display code, use triple backticks (```) or indent the code with four spaces:

```py
def hello_world():
    print("Hello, World!")
```


## Tables

Tables can be created using pipes `(|)` and hyphens `(-)`:

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Row 1    | Data 1   | Data 2   |
| Row 2    | Data 3   | Data 4   |

## Blockquotes

Blockquotes are created using the `>` symbol:

> This is a blockquote.
> It can span multiple lines.

## Horizontal Rules

You can create a horizontal rule using three or more hyphens, asterisks, or underscores:

```
---
```