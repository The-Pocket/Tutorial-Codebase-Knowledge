import pytest
from pydantic import ValidationError
# Adjust the import path based on how you would run pytest.
# If running pytest from project root:
from webapp.main_web import TutorialRequest

def test_tutorial_request_valid_data():
    data = {
        "repo_url": "https://github.com/user/repo",
        "project_name": "Test Project",
        "language": "english",
        "include_patterns": ["*.py"],
        "exclude_patterns": ["tests/*"],
        "max_file_size": 50000,
        "max_abstractions": 5,
        "github_token": "test_token_123",
        "use_cache": False
    }
    req = TutorialRequest(**data)
    assert req.repo_url == data["repo_url"]
    assert req.project_name == data["project_name"]
    assert req.use_cache == False
    assert req.include_patterns == ["*.py"]

def test_tutorial_request_missing_required_field():
    data = {"project_name": "Test Project"} # Missing repo_url
    with pytest.raises(ValidationError):
        TutorialRequest(**data)

def test_tutorial_request_invalid_type():
    data = {
        "repo_url": "https://github.com/user/repo",
        "max_file_size": "not_an_integer" # Invalid type
    }
    with pytest.raises(ValidationError):
        TutorialRequest(**data)

def test_tutorial_request_default_values():
    data = {"repo_url": "https://github.com/user/repo"}
    req = TutorialRequest(**data)
    assert req.language == "english" # Default
    assert req.max_file_size == 100000 # Default
    assert req.max_abstractions == 10 # Default
    assert req.use_cache is True # Default
    assert req.include_patterns is None # Default (Pydantic model will have None)
    assert req.exclude_patterns is None # Default
