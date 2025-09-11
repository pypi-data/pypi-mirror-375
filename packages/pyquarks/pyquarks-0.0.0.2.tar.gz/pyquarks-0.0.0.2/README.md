# PyQuarks

**PyQuarks** is a compact, modular collection of Python algorithms built for general-purpose data manipulation. Whether you're sorting, searching, transforming, or analyzing, PyQuarks provides a clear and reliable foundation for working with data.

This project is a curated library of reusable logic—organized for clarity, built for simplicity. While currently focused on core algorithmic tools, the long-term goal is to evolve PyQuarks into a lightweight framework for structured data workflows.

## Features

- **Core Modules**: Covers essential algorithms for data handling, including sorting, searching, filtering, and transformation.
- **Minimal Dependencies**: Built entirely with standard Python, so no external libraries required.
- **Clean Structure**: Files and functions are logically grouped for easy access and reuse.
- **Scalable Design**: Written with future extensibility in mind, should it grow into a framework.

## Use Cases

- Quick prototyping of algorithmic logic
- Educational reference for learning or teaching Python algorithms
- Lightweight utilities for data manipulation tasks
- Foundation for future framework development

## Roadmap

- CLI for running selected modules
- Optional configuration system for chaining operations
- Initial framework scaffolding (when time permits)

## Vision

PyQuarks is about clarity, utility, and control. It’s a personal project built under constraints, with the goal of creating something useful, maintainable, and expandable.

## Getting Started

To start using PyQuarks, simply clone the repository and explore the available [modules](./MODULES.md).

```bash
git clone https://github.com/Prospy006/pyquarks.git
cd pyquarks
```

### Example usage:

```py
import linked_lists

# Create a linked list
ll = LinkedList()

# Insert values
ll.insert(420)
ll.insert(69)
ll.insert(6)

# Display list
ll.display() # output: [420, 69, 6]

# Delete byval or byind
ll.delete_byval(6) # deletes last value
ll.delete_byind(0) # deletes first value
ll.display() # output: [69]
```