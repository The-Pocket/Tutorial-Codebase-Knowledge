import tiktoken
from typing import Dict, List, Tuple, Any
import os

class TokenManager:
    def __init__(self, model_name: str = "gpt-4", max_tokens: int = 128000):
        """Initialize the token manager.
        
        Args:
            model_name: The name of the model to use for token counting
            max_tokens: Maximum tokens allowed in context
        """
        self.encoder = tiktoken.encoding_for_model(model_name)
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.content_tokens: Dict[str, int] = {}

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text."""
        return len(self.encoder.encode(text))

    def add_content(self, key: str, content: str) -> bool:
        """Add content to the token manager.
        
        Returns:
            bool: True if content was added, False if it would exceed token limit
        """
        tokens = self.count_tokens(content)
        if self.current_tokens + tokens > self.max_tokens:
            return False
        
        self.content_tokens[key] = tokens
        self.current_tokens += tokens
        return True

    def remove_content(self, key: str) -> None:
        """Remove content from the token manager."""
        if key in self.content_tokens:
            self.current_tokens -= self.content_tokens[key]
            del self.content_tokens[key]

    def get_available_tokens(self) -> int:
        """Get the number of tokens still available."""
        return self.max_tokens - self.current_tokens

    def create_hierarchical_context(self, files_data: List[Tuple[str, str]], 
                                  max_files_per_level: int = 50) -> Dict[str, Any]:
        """Create a hierarchical context from files data.
        
        Args:
            files_data: List of (path, content) tuples
            max_files_per_level: Maximum number of files to include at each level
        
        Returns:
            Dict containing hierarchical context information
        """
        # Group files by directory level
        hierarchy: Dict[str, List[Tuple[str, str]]] = {}
        
        for path, content in files_data:
            depth = len(os.path.normpath(path).split(os.sep))
            if depth not in hierarchy:
                hierarchy[depth] = []
            hierarchy[depth].append((path, content))

        # Process each level
        context = {
            "levels": {},
            "file_summaries": {},
            "total_files": len(files_data)
        }

        for depth in sorted(hierarchy.keys()):
            level_files = hierarchy[depth]
            
            # Sort files by size and importance (e.g., prioritize non-test files)
            level_files.sort(key=lambda x: (
                "test" in x[0].lower(),  # Deprioritize test files
                -len(x[1])  # Prioritize larger files
            ))

            # Take top N files for this level
            selected_files = level_files[:max_files_per_level]
            
            level_context = []
            for path, content in selected_files:
                # Try to add full content
                if self.add_content(f"full_{path}", content):
                    level_context.append({
                        "path": path,
                        "type": "full",
                        "content": content
                    })
                else:
                    # If full content doesn't fit, add a summary
                    summary = self._create_file_summary(path, content)
                    if self.add_content(f"summary_{path}", summary):
                        level_context.append({
                            "path": path,
                            "type": "summary",
                            "content": summary
                        })
            
            if level_context:
                context["levels"][depth] = level_context

        return context

    def _create_file_summary(self, path: str, content: str) -> str:
        """Create a summary of a file's content."""
        # Basic summary: first few lines and size info
        lines = content.split('\n')[:10]  # First 10 lines
        summary = f"File: {path}\n"
        summary += f"Size: {len(content)} chars\n"
        summary += f"Preview:\n{''.join(lines)}\n..."
        return summary
