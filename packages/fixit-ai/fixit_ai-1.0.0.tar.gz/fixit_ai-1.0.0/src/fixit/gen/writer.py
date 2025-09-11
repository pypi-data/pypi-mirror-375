"""
Writer module for generating test files from TestPlan.

This module provides functionality to:
- Generate pytest test files from TestPlan objects
- Split tests by tags into separate files
- Ensure deterministic file naming and structure
- Manage proper imports and file organization
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from jinja2 import Environment, FileSystemLoader, Template
from dataclasses import dataclass

from .cases import TestPlan, TestCase


@dataclass
class GeneratedFile:
    """Represents a generated test file."""
    path: str
    content: str
    tag: str
    test_case_count: int
    spec_hash: str
    plan_hash: str


@dataclass
class WriteResult:
    """Result of writing test files."""
    files: List[GeneratedFile]
    output_dir: Path
    total_test_cases: int
    tags: Set[str]


class TestFileWriter:
    """Writes test files from TestPlan objects."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize the test file writer.
        
        Args:
            template_dir: Directory containing Jinja2 templates.
                         Defaults to src/fixit/gen/templates/
        """
        if template_dir is None:
            # Default to the templates directory relative to this file
            current_dir = Path(__file__).parent
            template_dir = current_dir / "templates"
        
        self.template_dir = Path(template_dir)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Load the pytest template
        self.pytest_template = self.jinja_env.get_template("pytest_endpoint.j2")
    
    def write_test_files(
        self,
        test_plan: TestPlan,
        output_dir: Path,
        file_prefix: str = "test_",
        split_by_tags: bool = True
    ) -> WriteResult:
        """
        Write test files from a TestPlan.
        
        Args:
            test_plan: The TestPlan to generate files from
            output_dir: Directory to write test files to
            file_prefix: Prefix for generated test file names
            split_by_tags: Whether to split tests by tags into separate files
            
        Returns:
            WriteResult with information about generated files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        all_tags = set()
        total_test_cases = len(test_plan.test_cases)
        
        if split_by_tags:
            # Group test cases by tags
            test_cases_by_tag = self._group_by_tags(test_plan.test_cases)
            
            for tag, tag_test_cases in test_cases_by_tag.items():
                all_tags.add(tag)
                
                # Create a test plan for this tag
                tag_test_plan = TestPlan(
                    title=f"{test_plan.title} - {tag}",
                    spec_hash=test_plan.spec_hash,
                    plan_hash=test_plan.plan_hash,
                    base_url=test_plan.base_url,
                    framework=test_plan.framework,
                    security_schemes=test_plan.security_schemes,
                    test_cases=tag_test_cases
                )
                
                # Generate file for this tag
                file_content = self._render_template(tag_test_plan)
                file_name = self._generate_filename(
                    file_prefix, tag, test_plan.spec_hash
                )
                file_path = output_dir / file_name
                
                # Write file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                
                generated_file = GeneratedFile(
                    path=str(file_path),
                    content=file_content,
                    tag=tag,
                    test_case_count=len(tag_test_cases),
                    spec_hash=test_plan.spec_hash,
                    plan_hash=test_plan.plan_hash
                )
                generated_files.append(generated_file)
        
        else:
            # Single file for all test cases
            all_tags = self._extract_all_tags(test_plan.test_cases)
            tag_name = "all"
            
            file_content = self._render_template(test_plan)
            file_name = self._generate_filename(
                file_prefix, tag_name, test_plan.spec_hash
            )
            file_path = output_dir / file_name
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            generated_file = GeneratedFile(
                path=str(file_path),
                content=file_content,
                tag=tag_name,
                test_case_count=total_test_cases,
                spec_hash=test_plan.spec_hash,
                plan_hash=test_plan.plan_hash
            )
            generated_files.append(generated_file)
        
        return WriteResult(
            files=generated_files,
            output_dir=output_dir,
            total_test_cases=total_test_cases,
            tags=all_tags
        )
    
    def _group_by_tags(self, test_cases: List[TestCase]) -> Dict[str, List[TestCase]]:
        """Group test cases by their tags."""
        test_cases_by_tag = {}
        
        for test_case in test_cases:
            # Use 'default' tag if no tags specified
            tags = test_case.tags or ['default']
            
            for tag in tags:
                if tag not in test_cases_by_tag:
                    test_cases_by_tag[tag] = []
                test_cases_by_tag[tag].append(test_case)
        
        return test_cases_by_tag
    
    def _extract_all_tags(self, test_cases: List[TestCase]) -> Set[str]:
        """Extract all unique tags from test cases."""
        all_tags = set()
        
        for test_case in test_cases:
            tags = test_case.tags or ['default']
            all_tags.update(tags)
        
        return all_tags
    
    def _render_template(self, test_plan: TestPlan) -> str:
        """Render the pytest template with the test plan."""
        return self.pytest_template.render(test_plan=test_plan)
    
    def _generate_filename(
        self,
        prefix: str,
        tag: str,
        spec_hash: str
    ) -> str:
        """
        Generate a deterministic filename for a test file.
        
        Format: {prefix}{tag}_{short_hash}.py
        """
        # Sanitize tag name for filename
        safe_tag = tag.lower().replace(' ', '_').replace('-', '_')
        safe_tag = ''.join(c for c in safe_tag if c.isalnum() or c == '_')
        
        # Use first 8 characters of spec hash for uniqueness
        short_hash = spec_hash[:8]
        
        return f"{prefix}{safe_tag}_{short_hash}.py"
    
    def cleanup_old_files(
        self,
        output_dir: Path,
        current_spec_hash: str,
        file_prefix: str = "test_"
    ) -> List[str]:
        """
        Clean up old test files that don't match the current spec hash.
        
        Args:
            output_dir: Directory to clean up
            current_spec_hash: Current spec hash to preserve
            file_prefix: Prefix of test files to clean up
            
        Returns:
            List of paths of deleted files
        """
        output_dir = Path(output_dir)
        if not output_dir.exists():
            return []
        
        deleted_files = []
        current_short_hash = current_spec_hash[:8]
        
        # Find all test files with the prefix
        for file_path in output_dir.glob(f"{file_prefix}*.py"):
            filename = file_path.name
            
            # Check if this file has a different spec hash
            if '_' in filename and filename.endswith('.py'):
                # Extract hash from filename (last part before .py)
                name_parts = filename[:-3].split('_')  # Remove .py extension
                if len(name_parts) >= 2:
                    file_hash = name_parts[-1]
                    
                    # If this file has a different hash, delete it
                    if file_hash != current_short_hash:
                        file_path.unlink()
                        deleted_files.append(str(file_path))
        
        return deleted_files
    
    def generate_conftest_py(
        self,
        output_dir: Path,
        test_plan: TestPlan,
        additional_fixtures: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a conftest.py file with common fixtures and configuration.
        
        Args:
            output_dir: Directory to write conftest.py to
            test_plan: TestPlan to extract configuration from
            additional_fixtures: Additional fixture code to include
            
        Returns:
            Path to the generated conftest.py file
        """
        output_dir = Path(output_dir)
        conftest_path = output_dir / "conftest.py"
        
        # Base conftest content
        conftest_content = f'''"""
pytest configuration and fixtures for API tests.

Generated from OpenAPI specification.
Spec Hash: {test_plan.spec_hash}
Plan Hash: {test_plan.plan_hash}
"""

import pytest
import requests
import os
from typing import Dict, Any, Optional


@pytest.fixture(scope="session")
def base_url():
    """Base URL for API tests."""
    return os.getenv("API_BASE_URL", "{test_plan.base_url}")


@pytest.fixture(scope="session")
def api_timeout():
    """Timeout for API requests."""
    return int(os.getenv("API_TIMEOUT", "30"))


@pytest.fixture(scope="session")
def verify_ssl():
    """Whether to verify SSL certificates."""
    return os.getenv("VERIFY_SSL", "true").lower() == "true"


@pytest.fixture
def http_session(api_timeout, verify_ssl):
    """HTTP session with common configuration."""
    session = requests.Session()
    session.timeout = api_timeout
    session.verify = verify_ssl
    yield session
    session.close()


# Authentication fixtures
'''
        
        # Add authentication fixtures based on security schemes
        for scheme_name, scheme in test_plan.security_schemes.items():
            fixture_name = f"{scheme_name.lower()}_auth"
            
            if scheme.type == "apiKey" and hasattr(scheme, 'location') and scheme.location == "header":
                conftest_content += f'''
@pytest.fixture(scope="session")
def {fixture_name}():
    """API key for {scheme_name} authentication."""
    return os.getenv("{scheme_name.upper()}_API_KEY")
'''
            
            elif scheme.type == "http" and scheme.scheme == "bearer":
                conftest_content += f'''
@pytest.fixture(scope="session")
def {fixture_name}():
    """Bearer token for {scheme_name} authentication."""
    return os.getenv("{scheme_name.upper()}_TOKEN")
'''
            
            elif scheme.type == "http" and scheme.scheme == "basic":
                conftest_content += f'''
@pytest.fixture(scope="session")
def {fixture_name}():
    """Basic auth credentials for {scheme_name} authentication."""
    username = os.getenv("{scheme_name.upper()}_USERNAME")
    password = os.getenv("{scheme_name.upper()}_PASSWORD")
    if username and password:
        return (username, password)
    return None
'''
        
        # Add additional fixtures if provided
        if additional_fixtures:
            conftest_content += "\n\n# Additional fixtures\n"
            for fixture_name, fixture_code in additional_fixtures.items():
                conftest_content += f"\n{fixture_code}\n"
        
        # Write conftest.py
        with open(conftest_path, 'w', encoding='utf-8') as f:
            f.write(conftest_content)
        
        return str(conftest_path)


def write_tests(test_plan: TestPlan, output_dir: Path) -> int:
    """
    Convenience function to write test files from a TestPlan.
    
    Args:
        test_plan: The TestPlan to generate files from
        output_dir: Directory to write test files to
        
    Returns:
        Number of test cases written
    """
    writer = TestFileWriter()
    result = writer.write_test_files(test_plan, output_dir)
    return result.total_test_cases
