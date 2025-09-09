# Pydantic Stack Core

Minimal library for creating stackable, renderable Pydantic models that compose into structured string outputs.

## Overview

Pydantic Stack Core provides a simple foundation for building composable models that render to strings. Perfect for generating structured text, documentation, code, or any format where you need systematic composition.

## Key Concepts

- **RenderablePiece**: Base class for any model that renders to string
- **MetaStack**: Universal container for stacking RenderablePiece models  
- **generate_output_from_metastack**: Function to render stacks to final output

## Installation

[Installation instructions pending PyPI publication]

## Quick Start

```python
from pydantic_stack_core import RenderablePiece, MetaStack, generate_output_from_metastack

# Define custom pieces
class Title(RenderablePiece):
    text: str
    level: int = 1
    
    def render(self) -> str:
        return f"{'#' * self.level} {self.text}"

class Paragraph(RenderablePiece):
    content: str
    
    def render(self) -> str:
        return self.content

class CodeBlock(RenderablePiece):
    code: str
    language: str = "python"
    
    def render(self) -> str:
        return f"```{self.language}\n{self.code}\n```"

# Create a stack
stack = MetaStack(pieces=[
    Title(text="Getting Started", level=1),
    Paragraph(content="Here's how to use our library:"),
    CodeBlock(code="print('Hello, World!')"),
    Paragraph(content="That's it!")
])

# Generate output
output = generate_output_from_metastack(stack)
print(output)
```

Output:
```
# Getting Started
Here's how to use our library:
```python
print('Hello, World!')
```
That's it!
```

## Advanced Usage

### Custom Separators

```python
# Control spacing between pieces
stack = MetaStack(
    pieces=[...],
    separator="\n\n"  # Double newline between pieces
)
```

### Nested Stacks

Since MetaStack is also a RenderablePiece, you can nest them:

```python
section1 = MetaStack(pieces=[
    Title(text="Section 1", level=2),
    Paragraph(content="Section content...")
])

section2 = MetaStack(pieces=[
    Title(text="Section 2", level=2), 
    Paragraph(content="More content...")
])

document = MetaStack(pieces=[
    Title(text="Main Document", level=1),
    section1,
    section2
])
```

### Custom Rendering Logic

```python
class NumberedList(RenderablePiece):
    items: List[str]
    
    def render(self) -> str:
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(self.items))

class BulletList(RenderablePiece):
    items: List[str]
    
    def render(self) -> str:
        return "\n".join(f"• {item}" for item in self.items)
```

## Use Cases

- **Documentation Generation**: Create structured docs from data
- **Code Generation**: Build source code from templates  
- **Report Creation**: Compose complex reports from components
- **Template Systems**: Build flexible, reusable content templates
- **Agent Outputs**: Systematic text generation for AI agents

## Integration with HEAVEN Ecosystem

Pydantic Stack Core integrates with:
- **Payload Discovery**: For systematic content generation workflows
- **Powerset Agents**: For structured agent outputs
- **MetaStack Powerset Agent**: For learning and applying stacking patterns

## Development

```bash
# Clone and install for development
git clone https://github.com/sancovp/pydantic-stack-core
cd pydantic-stack-core
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .
```

## Why Stack-Based?

The stack metaphor makes composition intuitive:
1. **Sequential**: Pieces render in order
2. **Nestable**: Stacks can contain other stacks
3. **Separable**: Control spacing between pieces
4. **Extensible**: Easy to add new piece types

This approach scales from simple text formatting to complex document generation while keeping the API minimal and predictable.

## License

MIT License - see LICENSE file for details.

## Part of HEAVEN Ecosystem

This library is part of the HEAVEN (Hierarchical Event-based Agent-Versatile Environment Network) ecosystem for AI agent development.