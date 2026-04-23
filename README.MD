# LLM-Generated Phishing Email Detection

**Todd Watkins** - **Student Number: 23010802**  
**UFCE8A-30-3 Cyber Security Project** - BSc Cyber Security & Digital Forensics  
University of the West of England (UWE)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Project Summary

**Problem**: Do modern email filters catch **LLM-generated phishing emails** as effectively as traditional phishing?

**Applied Project** testing **4 LLMs** vs **4 providers**.

**Key Finding**: **95-100% evasion rate**. Legacy AOL: **63.67% detection**.

## Results

### Contingency Table
| Round | TP (Detected) | FN (Missed) | Total |
|-------|---------------|-------------|-------|
| **1** | **160**       | **40**      | 200   |
| **2** | **15**        | **176**     | 191   |
| **3** | **2**         | **189**     | 191   |
| **4** | **0**         | **191**     | 191   |

### Overall χ² Test
| Metric | Value |
|--------|-------|
| **χ²** | **502.24** |
| **p-value** | **0.000001** |

### Pairwise Tests
| Comparison | χ² | p-value | Significant |
|------------|----|---------|-------------|
| R1 vs R2 | 202.77 | 0.000 | **YES** |
| R1 vs R4 | 255.34 | 0.000 | **YES** |

<img src="DataScience\Notebooks\Plots\radar_chart.png" width="450" alt="Spam Rate Evolution">

## Quick Start

## Setup

This project uses **uv** for dependency management.

```bash
git clone https://github.com/ToddWatkinsDev/Cyber-Security-Project
cd Cyber-Security-Project

uv sync
```

If you need to run scripts:

```bash
uv run python SendEmails/sendingemails.py
uv run jupyter notebook
```

## License

[MIT](LICENSE) © 2026 Todd Watkins
