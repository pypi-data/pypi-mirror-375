# Git LFS Advisor

A simple command-line tool to scan a Git repository, find files suitable for Git LFS, and generate the necessary configuration commands.

This tool helps you quickly set up Git LFS for a new or existing project without manually checking every file.

## ✨ Features

- **Repository Scan**: Scans the entire Git repository to find large or binary files.
- **Custom Rules**: Define scanning rules based on file size or file extension.
- **Command Generation**: Automatically generates `git lfs track` and `git lfs migrate` commands for you to copy and execute.
- **Cross-Platform**: Built with Python, it runs on Windows, macOS, and Linux.

## 📋 What It Does

1. **Scans** your repository for large files and binary assets
2. **Analyzes** file patterns, sizes, and repository structure
3. **Recommends** which files should be tracked by Git LFS
4. **Generates** `.gitattributes` configuration automatically
5. **Provides** migration commands and best practices

## 🎯 Use Cases

- Setting up LFS for new repositories
- Optimizing existing repositories with large files
- Migrating from regular Git to Git LFS
- Repository cleanup and size optimization
- CI/CD pipeline integration

## 📊 Example Output

```txt
🔍 Scanning repository...
📁 Found 1,247 files (Total: 2.3 GB)

💡 LFS Recommendations:
  • *.psd files (127 files, 890 MB) → Track with LFS
  • *.mp4 files (23 files, 1.2 GB) → Track with LFS
  • *.zip files (8 files, 156 MB) → Track with LFS

📝 Generated .gitattributes:
  *.psd filter=lfs diff=lfs merge=lfs -text
  *.mp4 filter=lfs diff=lfs merge=lfs -text
  *.zip filter=lfs diff=lfs merge=lfs -text

💾 Potential space savings: ~2.1 GB in Git history
```

## 🛠️ Installation

```bash
pip install git-lfs-advisor-cli
```

## 🤝 Contributing

Contributions are welcome!

## ⭐ Show Your Support

If this tool helps you manage your Git LFS setup, please give it a star! ⭐

---

**Made with ❤️ for better Git workflows**
