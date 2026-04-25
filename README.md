# Architecture Tutor 🏗️

[![PyPI version](https://img.shields.io/pypi/v/architecture-tutor.svg)](https://pypi.org/project/architecture-tutor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

**Architecture Tutor** is a static analysis tool designed to bridge the gap between high-level software design and actual implementation. By programmatically analyzing Python source code, it identifies and validates the use of common software design patterns.

## 🎯 Project Overview
In many software projects, "architectural drift" occurs when the implementation deviates from the intended design. This project provides a programmatic way to detect patterns and ensure structural integrity. It serves as both a developer tool for code reviews and an educational resource for students mastering software architecture.

## 🚀 Key Features
* **AST-Based Analysis:** Utilizes Python’s `ast` (Abstract Syntax Trees) module to perform deep structural analysis without code execution.
* **Pattern Recognition:** Detects core Creational, Structural, and Behavioral patterns (e.g., Singleton, Factory, Strategy).
* **Automated Reporting:** Generates summaries highlighting pattern compliance and structural violations.
* **Ready for Production:** Available as a published PyPI module for easy integration into dev workflows.

## 🛠️ Technical Deep Dive
The tool operates by parsing source code into an **Abstract Syntax Tree (AST)** and applying heuristic "Fingerprints" to identify patterns:

1.  **Parsing:** Source code is transformed into a hierarchical tree of nodes.
2.  **Traversal:** A custom `NodeVisitor` traverses the tree to inspect class definitions, inheritance chains, and method signatures.
3.  **Pattern Matching:** It identifies specific structural markers. For instance, to detect a **Singleton**, it searches for private constructors combined with a static instance access method.

## 📦 Installation
Install the module directly via pip:
```bash
pip install architecture-tutor

