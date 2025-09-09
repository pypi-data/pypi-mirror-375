"""
Pydantic Stack Core - Minimal library for stackable, renderable Pydantic models.

This library provides the foundation for creating structured string outputs
through composable Pydantic models. The core consists of:

1. RenderablePiece - Base class for any model that renders to string
2. MetaStack - Universal container for stacking any RenderablePiece models  
3. generate_output_from_metastack - Simple function to render stacks to final output

The magic happens when agents learn patterns by calling help() on user-defined
RenderablePiece subclasses and discover how to compose them into MetaStacks
for different output formats.

Example Usage:
    ```python
    from pydantic_stack_core import RenderablePiece, MetaStack, generate_output_from_metastack
    
    class Title(RenderablePiece):
        text: str
        level: int = 1
        
        def render(self) -> str:
            return f"{'#' * self.level} {self.text}"
    
    class Paragraph(RenderablePiece):
        content: str
        
        def render(self) -> str:
            return self.content
    
    # Create a stack
    stack = MetaStack(pieces=[
        Title(text="Hello World", level=1),
        Paragraph(content="This is a test paragraph.")
    ])
    
    # Generate final output
    output = generate_output_from_metastack(stack)
    print(output)
    # Output:
    # # Hello World
    # This is a test paragraph.
    ```
"""

from .core import RenderablePiece, MetaStack, generate_output_from_metastack

__version__ = "0.1.0"
__all__ = ["RenderablePiece", "MetaStack", "generate_output_from_metastack"]