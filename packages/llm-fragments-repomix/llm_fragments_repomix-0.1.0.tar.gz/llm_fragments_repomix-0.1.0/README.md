# llm-fragments-repomix

A plugin for [LLM](https://llm.datasette.io/) that loads repository contents as fragments using [Repomix](https://github.com/yamadashy/repomix).

## Installation

First, install the plugin:

```bash
pip install llm-fragments-repomix
```

Make sure you have `repomix` installed:

```bash
npm install -g repomix
```

## Usage

Use the `repomix:` prefix with a full git repository URL:

```bash
llm -f repomix:https://git.sr.ht/~amolith/willow "Tell me about this project"
```

```bash
llm -f repomix:ssh://git.sr.ht:~amolith/willow "Analyze the code structure"
```

```bash
llm -f repomix:git@github.com:user/repo.git "Review this codebase"
```

### Arguments

You can pass arguments to repomix using colon-separated syntax:

```bash
# Basic compression
llm -f repomix:https://git.sr.ht/~amolith/willow:compress "Tell me about this project"

# Include specific file patterns
llm -f repomix:https://git.sr.ht/~amolith/willow:include=*.go,*.md "Analyze the Python and documentation files"

# Multiple arguments
llm -f repomix:https://git.sr.ht/~amolith/willow:compress:include=*.go:ignore=tests/ "Analyze Python files but skip tests"
```

#### Supported Arguments

- `compress` - Compress output to reduce token count
- `include=pattern` - Include files matching pattern (comma-separated)
- `ignore=pattern` - Ignore files matching pattern (comma-separated)
- `style=type` - Output style (xml, markdown, plain)
- `remove-comments` - Remove comments from code
- `remove-empty-lines` - Remove empty lines
- `output-show-line-numbers` - Add line numbers to output
- `no-file-summary` - Disable file summary section
- `no-directory-structure` - Disable directory structure section
- `no-files` - Disable file content output
- `header-text=text` - Custom header text
- `instruction-file-path=path` - Path to instruction file
- `include-empty-directories` - Include empty directories in output
- `no-git-sort-by-changes` - Don't sort files by git changes
- `include-diffs` - Include git diffs in output
- `no-gitignore` - Ignore .gitignore files
- `no-default-patterns` - Don't use default ignore patterns
- `no-security-check` - Disable security checks
- `token-count-encoding=encoding` - Token count encoding
- `top-files-len=N` - Number of top files to show
- `verbose` - Verbose output
- `quiet` - Quiet mode

For a complete list of supported arguments, refer to the [Repomix documentation](https://github.com/yamadashy/repomix).

## How It Works

The plugin will:
1. Parse the repository URL and any arguments
2. Clone the repository to a temporary directory
3. Run repomix on the cloned repository with the specified arguments
4. Return the repomix output as a single fragment
5. Clean up the temporary directory

## Requirements

- Python 3.9+
- `git` command available in PATH
- `repomix` command available in PATH
- LLM CLI tool installed

## License

Apache-2.0
