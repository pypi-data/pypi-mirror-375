
# cruise-toolkit

**cruise-toolkit** is a unified Python toolkit that integrates barcode splitting, CB/UMI correction, counting, and CR/UR alignment steps commonly used in single-cell and spatial transcriptomics pipelines.  

It provides a **single command-line entry point** — `cruise-toolkit` — wrapping your original `cruise.py` workflow script, while preserving argument compatibility.

---

## 🔧 Installation

From source (development mode):

```bash
git clone https://github.com/dawangran/cruise-toolkit.git
cd cruise-toolkit
pip install -e .
```

In the future, installation from PyPI will be supported:

```bash
pip install cruise-toolkit
```

---

## 🚀 Quick Start

Run the main workflow (arguments are fully compatible with your original `cruise.py` script):

```bash
cruise-toolkit \
  --bam input.bam \
  --fastqs fq1.fastq.gz,fq2.fastq.gz \
  --valid-cell valid.cell.tsv \
  --adapt CTACGATCCGACTTTCTGCG \
  --model BBBBBBBBBBCCTTCCBBBBBBBBBBCGATGUUUUUUUUUUTTTT \
  --threads 16 \
  --cb-tags CC,CB \
  --umi-tag UB \
  --outdir cruise_out
```

---

## 🖥️ CLI Usage

Show help:

```bash
cruise-toolkit -h
cruise-toolkit --help
```

This will display the **native arguments of `cruise.py`**, including `--bam`, `--fastqs`, `--adapt`, `--model`, `--cb-tags`, `--umi-tag`, etc.  

Global options (apply to all runs):  
- `--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}`  
  Set global logging level (default: INFO)  
- `--log-file run.log`  
  Save logs to file  
- `--version`  
  Show version  

Example:

```bash
cruise-toolkit --log-level DEBUG --log-file run.log \
  --bam input.bam --fastqs fq1.fq.gz,fq2.fq.gz --outdir cruise_out
```

---

## 📜 Common Arguments

| Argument | Description |
|----------|-------------|
| `--bam` | Input BAM file |
| `--fastqs` | Comma-separated list of FASTQ files |
| `--valid-cell` | File with valid cell barcodes |
| `--adapt` | Adapter sequence |
| `--model` | CB/UMI model string |
| `--threads` | Number of threads |
| `--cb-tags` | Cell barcode tags (e.g., `CC,CB`) |
| `--umi-tag` | UMI tag (e.g., `UB`) |
| `--outdir` | Output directory |
| `--keep-sample-tmp` / `--no-keep-sample-tmp` | Whether to keep intermediate files |

> All argument definitions remain identical to the original `cruise.py`.  
> Use `cruise-toolkit --help` to view the full parameter list.

---

## 📝 Logging System

All runs can be configured with global logging options:

```bash
cruise-toolkit --log-level INFO --log-file pipeline.log \
  --bam input.bam --fastqs fq1.fq.gz,fq2.fq.gz ...
```

Logs are printed to stderr and optionally written to a file.

---

## 🧪 Development & Testing

```bash
# Install dev dependencies
pip install -e .[dev]

# Run tests
pytest -q
```

---

## 👤 Author

- Dawn 

---

## 📄 License

MIT License
