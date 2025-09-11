from llm_fragments_repomix import repomix_loader
import pytest
from unittest.mock import patch, Mock, MagicMock
import subprocess
import tempfile
import pathlib


class TestRepomixLoader:
    """Test the repomix_loader function"""

    def test_invalid_url_formats(self):
        """Test that invalid URL formats raise ValueError"""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com/repo",
            "file://local/path",
            "http://example.com",  # No path
            "",  # Empty string
        ]
        
        for invalid_url in invalid_urls:
            with pytest.raises(ValueError) as ex:
                repomix_loader(invalid_url)
            assert "Repository URL must start with https://, ssh://, or git@" in str(ex.value)

    @patch('llm_fragments_repomix.shutil.which')
    def test_repomix_not_installed(self, mock_which):
        """Test error when repomix is not installed"""
        mock_which.return_value = None
        
        with pytest.raises(ValueError) as ex:
            repomix_loader("https://github.com/user/repo")
        assert "repomix command not found" in str(ex.value)
        assert "https://github.com/yamadashy/repomix" in str(ex.value)

    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_git_clone_failure(self, mock_run, mock_which):
        """Test handling of git clone failures"""
        mock_which.return_value = "/usr/bin/repomix"
        
        # Mock git clone failure
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["git", "clone"], stderr="Repository not found"
        )
        
        with pytest.raises(ValueError) as ex:
            repomix_loader("https://github.com/user/nonexistent")
        assert "Failed to clone repository" in str(ex.value)
        assert "Repository not found" in str(ex.value)

    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_repomix_failure(self, mock_run, mock_which):
        """Test handling of repomix execution failures"""
        mock_which.return_value = "/usr/bin/repomix"
        
        # Mock successful git clone, failed repomix
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                raise subprocess.CalledProcessError(
                    1, ["repomix"], stderr="Repomix error"
                )
        
        mock_run.side_effect = mock_run_side_effect
        
        with pytest.raises(ValueError) as ex:
            repomix_loader("https://github.com/user/repo")
        assert "Failed to run repomix" in str(ex.value)
        assert "Repomix error" in str(ex.value)

    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_successful_repomix_execution(self, mock_run, mock_which):
        """Test successful repomix execution"""
        mock_which.return_value = "/usr/bin/repomix"
        
        # Mock repomix output
        repomix_output = """
# Repository Structure

## File: main.py
```python
print("Hello, World!")
```

## File: README.md
```markdown
# Test Project
This is a test project.
```
"""
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                return Mock(stdout=repomix_output, stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        fragments = repomix_loader("https://github.com/user/repo")
        
        assert len(fragments) == 1
        assert str(fragments[0]) == repomix_output
        assert fragments[0].source == "repomix:https://github.com/user/repo"

    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_different_url_formats(self, mock_run, mock_which):
        """Test that different valid URL formats work"""
        mock_which.return_value = "/usr/bin/repomix"
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                return Mock(stdout="test output", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        valid_urls = [
            "https://github.com/user/repo",
            "https://git.sr.ht/~user/repo",
            "ssh://git@github.com:user/repo.git",
            "git@github.com:user/repo.git",
        ]
        
        for url in valid_urls:
            fragments = repomix_loader(url)
            assert len(fragments) == 1
            assert fragments[0].source == f"repomix:{url}"

    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_subprocess_calls(self, mock_run, mock_which):
        """Test that subprocess calls are made correctly"""
        mock_which.return_value = "/usr/bin/repomix"
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                return Mock(stdout="test output", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        repo_url = "https://github.com/user/repo"
        repomix_loader(repo_url)
        
        # Check git clone call
        git_call = mock_run.call_args_list[0]
        assert git_call[0][0][:3] == ["git", "clone", "--depth=1"]
        assert git_call[0][0][3] == repo_url
        assert git_call[1]["check"] is True
        assert git_call[1]["capture_output"] is True
        assert git_call[1]["text"] is True
        
        # Check repomix call
        repomix_call = mock_run.call_args_list[1]
        assert repomix_call[0][0][:2] == ["repomix", "--stdout"]
        assert repomix_call[1]["check"] is True
        assert repomix_call[1]["capture_output"] is True
        assert repomix_call[1]["text"] is True

    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_generic_exception_handling(self, mock_run, mock_which):
        """Test handling of generic exceptions"""
        mock_which.return_value = "/usr/bin/repomix"
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                raise OSError("Permission denied")
        
        mock_run.side_effect = mock_run_side_effect
        
        with pytest.raises(ValueError) as ex:
            repomix_loader("https://github.com/user/repo")
        assert "Error processing repository" in str(ex.value)
        assert "Permission denied" in str(ex.value)

    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    @patch('llm_fragments_repomix.tempfile.TemporaryDirectory')
    def test_temporary_directory_cleanup(self, mock_tempdir, mock_run, mock_which):
        """Test that temporary directory is properly cleaned up"""
        mock_which.return_value = "/usr/bin/repomix"
        
        # Create a mock context manager for TemporaryDirectory
        mock_context = MagicMock()
        mock_context.__enter__.return_value = "/tmp/test_dir"
        mock_context.__exit__.return_value = None
        mock_tempdir.return_value = mock_context
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                return Mock(stdout="test output", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        repomix_loader("https://github.com/user/repo")
        
        # Verify that the temporary directory context manager was used
        mock_tempdir.assert_called_once()
        mock_context.__enter__.assert_called_once()
        mock_context.__exit__.assert_called_once()


class TestRepomixArgumentParsing:
    """Test argument parsing for colon-separated options"""
    
    def test_parse_fragment_string_url_only(self):
        """Test parsing URL without arguments"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo")
        assert url == "https://github.com/user/repo"
        assert args == {}
    
    def test_parse_fragment_string_with_compress(self):
        """Test parsing URL with compress flag"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo:compress")
        assert url == "https://github.com/user/repo"
        assert args == {"compress": True}
    
    def test_parse_fragment_string_with_include_patterns(self):
        """Test parsing URL with include patterns"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo:include=*.ts,*.js")
        assert url == "https://github.com/user/repo"
        assert args == {"include": "*.ts,*.js"}
    
    def test_parse_fragment_string_with_ignore_patterns(self):
        """Test parsing URL with ignore patterns"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo:ignore=*.log,tmp/")
        assert url == "https://github.com/user/repo"
        assert args == {"ignore": "*.log,tmp/"}
    
    def test_parse_fragment_string_multiple_args(self):
        """Test parsing URL with multiple arguments"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo:compress:include=*.py:ignore=tests/")
        assert url == "https://github.com/user/repo"
        assert args == {
            "compress": True,
            "include": "*.py",
            "ignore": "tests/"
        }
    
    def test_parse_fragment_string_complex_patterns(self):
        """Test parsing with complex glob patterns"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo:include=src/**/*.ts,**/*.md:ignore=**/*.test.ts,node_modules/")
        assert url == "https://github.com/user/repo"
        assert args == {
            "include": "src/**/*.ts,**/*.md",
            "ignore": "**/*.test.ts,node_modules/"
        }
    
    def test_parse_fragment_string_boolean_flags(self):
        """Test parsing various boolean flags"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo:compress:remove-comments:remove-empty-lines")
        assert url == "https://github.com/user/repo"
        assert args == {
            "compress": True,
            "remove-comments": True,
            "remove-empty-lines": True
        }
    
    def test_parse_fragment_string_output_options(self):
        """Test parsing output-related options"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo:style=markdown:output-show-line-numbers")
        assert url == "https://github.com/user/repo"
        assert args == {
            "style": "markdown",
            "output-show-line-numbers": True
        }
    
    def test_parse_fragment_string_ssh_url(self):
        """Test parsing SSH URLs with arguments"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("git@github.com:user/repo.git:compress:include=*.py")
        assert url == "git@github.com:user/repo.git"
        assert args == {
            "compress": True,
            "include": "*.py"
        }
    
    def test_parse_fragment_string_ssh_protocol_url(self):
        """Test parsing SSH protocol URLs with arguments"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("ssh://git@github.com:user/repo.git:compress")
        assert url == "ssh://git@github.com:user/repo.git"
        assert args == {"compress": True}
    
    def test_parse_fragment_string_empty_args(self):
        """Test parsing with empty argument values"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo:include=")
        assert url == "https://github.com/user/repo"
        assert args == {"include": ""}
    
    def test_parse_fragment_string_duplicate_args(self):
        """Test parsing with duplicate arguments (last one wins)"""
        from llm_fragments_repomix import parse_fragment_string
        
        url, args = parse_fragment_string("https://github.com/user/repo:include=*.ts:include=*.js")
        assert url == "https://github.com/user/repo"
        assert args == {"include": "*.js"}
    
    def test_build_repomix_command_no_args(self):
        """Test building repomix command without arguments"""
        from llm_fragments_repomix import build_repomix_command
        
        cmd = build_repomix_command("/tmp/repo", {})
        assert cmd == ["repomix", "--stdout", "/tmp/repo"]
    
    def test_build_repomix_command_with_compress(self):
        """Test building repomix command with compress flag"""
        from llm_fragments_repomix import build_repomix_command
        
        cmd = build_repomix_command("/tmp/repo", {"compress": True})
        assert cmd == ["repomix", "--stdout", "--compress", "/tmp/repo"]
    
    def test_build_repomix_command_with_include(self):
        """Test building repomix command with include patterns"""
        from llm_fragments_repomix import build_repomix_command
        
        cmd = build_repomix_command("/tmp/repo", {"include": "*.ts,*.js"})
        assert cmd == ["repomix", "--stdout", "--include", "*.ts,*.js", "/tmp/repo"]
    
    def test_build_repomix_command_with_ignore(self):
        """Test building repomix command with ignore patterns"""
        from llm_fragments_repomix import build_repomix_command
        
        cmd = build_repomix_command("/tmp/repo", {"ignore": "*.log,tmp/"})
        assert cmd == ["repomix", "--stdout", "--ignore", "*.log,tmp/", "/tmp/repo"]
    
    def test_build_repomix_command_multiple_args(self):
        """Test building repomix command with multiple arguments"""
        from llm_fragments_repomix import build_repomix_command
        
        args = {
            "compress": True,
            "include": "*.py",
            "ignore": "tests/",
            "remove-comments": True
        }
        cmd = build_repomix_command("/tmp/repo", args)
        expected = ["repomix", "--stdout", "--compress", "--include", "*.py", "--ignore", "tests/", "--remove-comments", "/tmp/repo"]
        assert cmd == expected
    
    def test_build_repomix_command_with_style(self):
        """Test building repomix command with style option"""
        from llm_fragments_repomix import build_repomix_command
        
        cmd = build_repomix_command("/tmp/repo", {"style": "markdown"})
        assert cmd == ["repomix", "--stdout", "--style", "markdown", "/tmp/repo"]
    
    def test_build_repomix_command_boolean_flags(self):
        """Test building repomix command with various boolean flags"""
        from llm_fragments_repomix import build_repomix_command
        
        args = {
            "compress": True,
            "remove-comments": True,
            "remove-empty-lines": True,
            "output-show-line-numbers": True,
            "no-file-summary": True
        }
        cmd = build_repomix_command("/tmp/repo", args)
        expected = [
            "repomix", "--stdout",
            "--compress",
            "--remove-comments", 
            "--remove-empty-lines",
            "--output-show-line-numbers",
            "--no-file-summary",
            "/tmp/repo"
        ]
        assert cmd == expected
    
    def test_build_repomix_command_unsupported_arg(self):
        """Test that unsupported arguments are ignored"""
        from llm_fragments_repomix import build_repomix_command
        
        args = {
            "compress": True,
            "unsupported-option": "value",
            "include": "*.py"
        }
        cmd = build_repomix_command("/tmp/repo", args)
        expected = ["repomix", "--stdout", "--compress", "--include", "*.py", "/tmp/repo"]
        assert cmd == expected
    
    def test_build_repomix_command_empty_string_values(self):
        """Test that empty string values are handled correctly"""
        from llm_fragments_repomix import build_repomix_command
        
        args = {
            "include": "",
            "ignore": "*.log"
        }
        cmd = build_repomix_command("/tmp/repo", args)
        # Empty include should be ignored, ignore should be included
        expected = ["repomix", "--stdout", "--ignore", "*.log", "/tmp/repo"]
        assert cmd == expected


class TestRepomixIntegrationWithArguments:
    """Integration tests for repomix loader with arguments"""
    
    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_repomix_loader_with_compress(self, mock_run, mock_which):
        """Test repomix loader with compress argument"""
        mock_which.return_value = "/usr/bin/repomix"
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                # Verify compress flag is passed
                assert "--compress" in cmd
                return Mock(stdout="compressed output", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        fragments = repomix_loader("https://github.com/user/repo:compress")
        assert len(fragments) == 1
        assert str(fragments[0]) == "compressed output"
        assert fragments[0].source == "repomix:https://github.com/user/repo:compress"
    
    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_repomix_loader_with_include_patterns(self, mock_run, mock_which):
        """Test repomix loader with include patterns"""
        mock_which.return_value = "/usr/bin/repomix"
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                # Verify include patterns are passed
                assert "--include" in cmd
                include_idx = cmd.index("--include")
                assert cmd[include_idx + 1] == "*.ts,*.js"
                return Mock(stdout="filtered output", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        fragments = repomix_loader("https://github.com/user/repo:include=*.ts,*.js")
        assert len(fragments) == 1
        assert str(fragments[0]) == "filtered output"
    
    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_repomix_loader_with_multiple_args(self, mock_run, mock_which):
        """Test repomix loader with multiple arguments"""
        mock_which.return_value = "/usr/bin/repomix"
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                # Verify multiple arguments are passed
                assert "--compress" in cmd
                assert "--include" in cmd
                assert "--ignore" in cmd
                include_idx = cmd.index("--include")
                assert cmd[include_idx + 1] == "*.py"
                ignore_idx = cmd.index("--ignore")
                assert cmd[ignore_idx + 1] == "tests/"
                return Mock(stdout="multi-arg output", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        fragments = repomix_loader("https://github.com/user/repo:compress:include=*.py:ignore=tests/")
        assert len(fragments) == 1
        assert str(fragments[0]) == "multi-arg output"
    
    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_repomix_loader_with_ssh_url_and_args(self, mock_run, mock_which):
        """Test repomix loader with SSH URL and arguments"""
        mock_which.return_value = "/usr/bin/repomix"
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                assert "--compress" in cmd
                return Mock(stdout="ssh output", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        fragments = repomix_loader("git@github.com:user/repo.git:compress")
        assert len(fragments) == 1
        assert str(fragments[0]) == "ssh output"
        assert fragments[0].source == "repomix:git@github.com:user/repo.git:compress"
    
    @patch('llm_fragments_repomix.shutil.which')
    @patch('llm_fragments_repomix.subprocess.run')
    def test_repomix_loader_preserves_original_source(self, mock_run, mock_which):
        """Test that the original fragment string is preserved in source"""
        mock_which.return_value = "/usr/bin/repomix"
        
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == "git":
                return Mock(stdout="", stderr="")
            elif cmd[0] == "repomix":
                return Mock(stdout="test output", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        original_string = "https://github.com/user/repo:compress:include=*.ts,*.js:ignore=*.md"
        fragments = repomix_loader(original_string)
        assert fragments[0].source == f"repomix:{original_string}"