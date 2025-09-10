
<div align="center">

<!-- Logo -->
<p align="center">
  <img src="https://github.com/HzaCode/OneCite/raw/master/logo_.jpg" alt="OneCite Logo" width="140" />
</p>

# OneCite 
### The Universal Citation & Academic Reference Toolkit
![Downloads](https://static.pepy.tech/badge/onecite)
[![PyPI version](https://img.shields.io/pypi/v/onecite.svg)](https://pypi.org/project/onecite/)
[![Python Version](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Project Status](https://img.shields.io/badge/Status-Alpha-orange.svg)]()

**Effortlessly convert messy, unstructured references into perfectly formatted, standardized citations.**

OneCite is a powerful command-line tool and Python library designed to automate the tedious process of citation management. Feed it anything—DOIs, paper titles,arXiv IDs, or even a mix—and get clean, accurate bibliographic entries in return.

> **🚀 OneCite for Web is coming.**
>
> Dropping soon at **[hezhiang.com/onecite](http://hezhiang.com/onecite)**.

[✨ Features](#-features) • [🚀 Quick Start](#-quick-start) • [📖 Advanced Usage](#-advanced-usage) • [🤖 AI Integration](#-ai-assistant-integration-mcp) • [⚙️ Configuration](#️-configuration) • [🤝 Contributing](#-contributing)

---

</div>

## ✨ Features

OneCite is packed with features to streamline your entire academic workflow, from initial search to final formatting.

- 🔍 **Smart Recognition**: Utilizes fuzzy matching against CrossRef and Google Scholar APIs to find the correct reference even from incomplete or slightly inaccurate information.
- 📚 **Universal Format Support**: Accepts `.txt` and `.bib` inputs and can output to **BibTeX**, **APA**, and **MLA** formats, adapting to any project's requirements.
- 🎯 **High-Accuracy Refinement**: A 4-stage processing pipeline cleans, queries, validates, and formats your entries to ensure the highest quality output.
- 🤖 **Intelligent Auto-Completion**: Automatically discovers and fills in missing bibliographic data like journal, volume, pages, and author lists.
- 🎛️ **Interactive Mode**: When multiple potential matches are found, an interactive prompt lets you choose the correct entry, giving you full control over ambiguous references.
- ⚙️ **Customizable Templates**: A flexible YAML-based template system allows for complete control over the output fields and their priority.
- 🎓 **Broad Paper Type Support**: Natively understands and processes journal articles, conference papers (NIPS, CVPR, ICML, etc.), and arXiv preprints with ease.
- 📄 **Seamless arXiv & URL Integration**: Automatically fetches metadata for arXiv IDs and can extract identifiers directly from `arxiv.org` or `doi.org` URLs.

## 🚀 Quick Start

Get up and running with OneCite in under a minute.

### Installation

```bash
# Recommended: Install from PyPI
pip install onecite

# Or, install from source for the latest version
git clone https://github.com/HzaCode/OneCite.git
cd OneCite
pip install -e .
```

### Basic Usage

1.  **Create an input file** (`references.txt`):

    ```text
    10.1038/nature14539
    
    Attention is all you need
    Vaswani et al.
    NIPS 2017
    ```

2.  **Run the command**:

    ```bash
    onecite process references.txt -o results.bib --quiet
    ```

3.  **Get perfectly formatted output** (`results.bib`):

    ```bibtex
    @article{LeCun2015Deep,
      doi = "10.1038/nature14539",
      title = "Deep learning",
      author = "LeCun, Yann and Bengio, Yoshua and Hinton, Geoffrey",
      journal = "Nature",
      year = 2015,
      volume = 521,
      number = 7553,
      pages = "436-444",
      publisher = "Springer Science and Business Media LLC",
      url = "https://doi.org/10.1038/nature14539",
    }
    
    @inproceedings{Vaswani2017Attention,
      arxiv = "1706.03762",
      title = "Attention Is All You Need",
      author = "Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, Lukasz and Polosukhin, Illia",
      booktitle = "Advances in Neural Information Processing Systems",
      year = 2017,
      url = "https://arxiv.org/abs/1706.03762",
    }
    ```

## 📖 Advanced Usage

<details>
<summary><strong>🎨 Multiple Output Formats (APA, MLA)</strong></summary>

```bash
# Generate APA formatted citations
onecite process refs.txt --output-format apa
# → LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. Nature, 521(7553), 436-444.
# → Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... & Polosukhin, I. (2017). Attention is all you need. In Advances in Neural Information Processing Systems.

# Generate MLA formatted citations
onecite process refs.txt --output-format mla
# → LeCun, Yann, Yoshua Bengio, and Geoffrey Hinton. "Deep Learning." Nature 521.7553 (2015): 436-444.
# → Vaswani, Ashish, et al. "Attention Is All You Need." Advances in Neural Information Processing Systems. 2017.
```
</details>

<details>
<summary><strong>🤖 Interactive Disambiguation</strong></summary>

For ambiguous entries, use the `--interactive` flag to ensure accuracy.

**Command**:
```bash
onecite process ambiguous.txt --interactive
```

**Example Interaction**:
```Found multiple possible matches for "Deep learning Hinton":
1. Deep learning
   Authors: LeCun, Yann; Bengio, Yoshua; Hinton, Geoffrey
   Journal: Nature
   Year: 2015
   Match Score: 92.5
   DOI: 10.1038/nature14539

2. Deep belief networks
   Authors: Hinton, Geoffrey E.
   Journal: Scholarpedia
   Year: 2009
   Match Score: 78.3
   DOI: 10.4249/scholarpedia.5947

Please select (1-2, 0=skip): 1
✅ Selected: Deep learning
```
</details>

<details>
<summary><strong>🐍 Use as a Python Library</strong></summary>

Integrate OneCite's processing power directly into your Python scripts.

```python
from onecite import process_references

# Define a callback for non-interactive selection (e.g., always choose the best match)
def auto_select_callback(candidates):
    return 0

result = process_references(
    input_content="Deep learning review\nLeCun, Bengio, Hinton\nNature 2015",
    input_type="txt",
    output_format="bibtex",
    interactive_callback=auto_select_callback
)

print(result['output_content'])
```
</details>

<details>
<summary><strong>📑 Supported Input Types</strong></summary>

OneCite is designed to be flexible and understands various common academic identifiers.

-   **DOI**: `10.1038/nature14539`
-   **Conference Papers**: `Attention is all you need, Vaswani et al., NIPS 2017`
-   **arXiv ID**: `1706.03762`
-   **URLs**: `https://arxiv.org/abs/1706.03762`

</details>


## 🤖 AI Assistant Integration (MCP)

OneCite provides complete Model Context Protocol (MCP) support, enabling AI assistants to directly use all of OneCite's functionality for literature search, processing, and formatting.

### ✨ Available Functions

- **`cite`** - Generate single academic citations
  - Supports DOI, paper titles, arXiv IDs, and other input types
  - Supports APA, MLA, BibTeX, and other output formats
- **`batch_cite`** - Batch citation generation
  - Process multiple literature sources at once
  - Automatically handle different input types
- **`search`** - Academic literature search
  - Search for relevant literature based on keywords
  - Return structured literature information

### 🚀 Quick Start

1. **Install OneCite** (if not already installed):
   ```bash
   pip install onecite
   ```

2. **Test MCP server**:
   ```bash
   onecite-mcp
   ```

3. **Configure AI assistant**:
   Add to `settings.json` in MCP-supported editors:
   ```json
   {
     "mcpServers": {
       "onecite": {
         "command": "onecite-mcp",
         "args": [],
         "env": {}
       }
     }
   }
   ```

4. **Restart your editor**, and the AI assistant will have access to OneCite's complete functionality!

### 📊 Test Status

✅ **Server Startup** - MCP server starts and responds normally  
✅ **Citation Function** - DOI parsing and formatting work correctly  
✅ **Batch Processing** - Multi-source batch processing works normally  
✅ **Search Function** - Literature search functionality works correctly  
✅ **Command Line Tool** - `onecite-mcp` command is available

### 💡 Usage Examples

After configuration, you can directly tell your AI assistant:
- "Generate an APA format citation for this DOI: 10.1038/nature14539"
- "Batch process these references and generate BibTeX format"
- "Search for the latest papers on machine learning"

The AI assistant will automatically call OneCite's corresponding functions and return results.

## ⚙️ Configuration

<details>
<summary><strong>📋 Command Line Options</strong></summary>

| Option          | Description                               | Default                |
| --------------- | ----------------------------------------- | ---------------------- |
| `--input-type`  | Input format (`txt`, `bib`)               | `txt`                  |
| `--output-format` | Output format (`bibtex`, `apa`, `mla`)    | `bibtex`               |
| `--template`    | Specify a custom template YAML to use     | `journal_article_full` |
| `--interactive` | Enable interactive mode for disambiguation| `False`                |
| `--quiet`       | Suppress verbose logging                  | `False`                |
| `--output`, `-o`| Path to the output file                   | `stdout`               |
</details>

<details>
<summary><strong>🎨 Custom Templates</strong></summary>

Define custom output formats using a simple YAML template.

**Example `my_template.yaml`**:
```yaml
name: my_template
entry_type: "@article"
fields:
  - name: author
    required: true
  - name: title  
    required: true
  - name: journal
    required: true
  - name: year
    required: true
  - name: doi
    required: false
    source_priority: [crossref_api]
```

**Usage**:`
``bash
onecite process refs.txt --template my_template.yaml```
</details>

## 🔄 Core Processing Pipeline

OneCite ensures high accuracy and quality through a sophisticated four-stage processing pipeline. The diagram below shows the complete workflow from raw input to final formatted output.

> 💡 **MCP Integration**: Through Model Context Protocol, AI assistants can directly invoke this complete processing pipeline without requiring users to manually operate the command line.

```mermaid
graph TD
    %% Input Layer - Multiple Entry Points
    A1["CLI Input<br/>onecite process"] --> A["Input Content"]
    A2["Python API<br/>process_references()"] --> A
    A3["MCP Server<br/>AI Assistant Integration"] --> A
    A4["Batch Processing<br/>Multiple Sources"] --> A
    
    A --> B["Stage 1: Parsing Module<br/>ParserModule"]
    
    B --> B1{"Input Type?"}
    B1 -->|TXT| B2["Parse Text<br/>- Split entries by double newlines<br/>- Extract DOIs and URLs<br/>- Generate query strings"]
    B1 -->|BIB| B3["Parse BibTeX<br/>- Parse existing entries<br/>- Extract metadata"]
    B2 --> C["Raw Entry List<br/>List[RawEntry]<br/>- id, raw_text, doi, url, query_string"]
    B3 --> C
    
    C --> D["Stage 2: Identification Module<br/>IdentifierModule"]
    D --> D0["Parallel Processing<br/>Each entry processed independently"]
    D0 --> D1{"DOI exists?"}
    
    D1 -->|Yes| D2["Validate DOI format<br/>Regex matching"]
    D2 --> D3["Verify DOI via CrossRef API"]
    D3 --> D4{"DOI exists and valid?"}
    
    D4 -->|Yes| D5["Get metadata from CrossRef<br/>Status: identified"]
    D4 -->|No| D6["DOI format valid but not found<br/>Continue fuzzy search"]
    
    D1 -->|No| D7["Check arXiv ID in URL"]
    D7 --> D8{"Found arXiv ID?"}
    D8 -->|Yes| D9["Extract arXiv ID<br/>Continue processing"]
    D8 -->|No| D10["Check well-known papers<br/>Built-in paper database"]
    
    D6 --> D11["Intelligent Search Strategy<br/>Auto-fallback mechanism"]
    D9 --> D11
    D10 --> D11
    
    D11 --> D11A["Primary: CrossRef Search<br/>Fast and accurate"]
    D11 --> D11B["Fallback: Google Scholar<br/>When CrossRef fails"]
    D11A --> D12["Score candidate results<br/>Fuzzy matching algorithm"]
    D11B --> D12
    
    D12 --> D13{"Match confidence?"}
    D13 -->|">80%"| D14["Auto-select best match<br/>Status: identified"]
    D13 -->|"70-80%"| D15["Interactive selection<br/>User/AI chooses from candidates"]
    D13 -->|"<70%"| D16["Mark as identification failed<br/>Status: identification_failed"]
    
    D15 --> D17["Selection result<br/>Status: identified"]
    D5 --> E["Identified Entry List<br/>List[IdentifiedEntry]<br/>- id, raw_text, doi, arxiv_id, metadata, status"]
    D14 --> E
    D16 --> E
    D17 --> E
    
    E --> F["Stage 3: Enrichment Module<br/>EnricherModule"]
    F --> F0["Parallel Enrichment<br/>Each entry processed independently"]
    F0 --> F1{"Entry status?"}
    F1 -->|identified| F2["Enrich metadata<br/>Template-driven completion"]
    F1 -->|failed| F3["Skip enrichment<br/>Status: enrichment_failed"]
    
    F2 --> F4{"Data source type?"}
    F4 -->|DOI| F5["Get complete metadata from CrossRef<br/>Full bibliographic data"]
    F4 -->|"arXiv ID"| F6["Get metadata from arXiv API<br/>Preprint information"]
    F4 -->|"Search result"| F7["Convert search metadata format<br/>Normalize data structure"]
    
    F5 --> F8["Generate BibTeX key<br/>FirstAuthorYearTitle format"]
    F6 --> F8
    F7 --> F8
    
    F8 --> F9["Complete missing fields<br/>Template priority rules"]
    F9 --> F10["Determine entry type<br/>@article vs @inproceedings"]
    F10 --> F11["Status: completed"]
    
    F3 --> G["Completed Entry List<br/>List[CompletedEntry]<br/>- id, doi, status, bib_key, bib_data"]
    F11 --> G
    
    G --> H["Stage 4: Formatting Module<br/>FormatterModule"]
    H --> H1{"Output format?"}
    
    H1 -->|BibTeX| H2["Format as BibTeX<br/>- Generate @entry format<br/>- Include all required fields"]
    H1 -->|APA| H3["Format as APA style<br/>- Author-date format<br/>- Standard punctuation"]
    H1 -->|MLA| H4["Format as MLA style<br/>- Author-page format<br/>- Specific citation rules"]
    
    H2 --> I["Final Output<br/>List[str] formatted citations"]
    H3 --> I
    H4 --> I
    
    I --> J["Processing Report<br/>- total: int<br/>- succeeded: int<br/>- failed_entries: List[Dict]"]
    
    %% MCP Integration Details
    MCP["MCP Functions"] --> MCP1["cite(source, style, format)<br/>Single citation generation"]
    MCP --> MCP2["batch_cite(sources, style)<br/>Batch processing"]
    MCP --> MCP3["search(query, limit)<br/>Literature search"]
    MCP1 --> A3
    MCP2 --> A3
    MCP3 --> A3
    
    %% Error handling and resilience
    D3 -.->|"API timeout/error"| D11
    F5 -.->|"API error"| F3
    F6 -.->|"API error"| F3
    H2 -.->|"Format error"| H5["Add to failed entries"]
    H3 -.->|"Format error"| H5
    H4 -.->|"Format error"| H5
    H5 --> J
    
    %% Template system
    T["Template System<br/>TemplateLoader"] --> F9
    T --> T1["journal_article_full.yaml<br/>Complete journal template"]
    T --> T2["conference_paper.yaml<br/>Conference template"]
    T1 --> T3["Field Configuration<br/>- Required/optional fields<br/>- Data source priority<br/>- Validation rules"]
    T2 --> T3
    
    %% External data sources with smart strategy
    DS["External Data Sources<br/>Smart API Management"] --> D3
    DS --> F5
    DS --> F6
    DS --> DS1["CrossRef API<br/>- DOI validation & metadata<br/>- Rate limiting & caching<br/>- Error handling"]
    DS --> DS2["arXiv API<br/>- Preprint metadata<br/>- PDF information<br/>- ID extraction"]
    DS --> DS3["Google Scholar<br/>- Fuzzy search fallback<br/>- Citation data<br/>- Timeout protection"]
    
    %% Performance optimizations
    PERF["Performance Features"] --> PERF1["Parallel Processing<br/>Independent entry handling"]
    PERF --> PERF2["Smart Caching<br/>Avoid duplicate API calls"]
    PERF --> PERF3["Graceful Degradation<br/>Fallback strategies"]
    PERF1 --> D0
    PERF1 --> F0
    
    %% Style definitions
    classDef stageBox fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef decisionBox fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef processBox fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef outputBox fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef systemBox fill:#fafafa,stroke:#424242,stroke-width:2px
    classDef mcpBox fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    classDef inputBox fill:#fff8e1,stroke:#ff8f00,stroke-width:2px
    classDef perfBox fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    
    class B,D,F,H stageBox
    class B1,D1,D4,D8,D13,F1,F4,H1 decisionBox
    class B2,B3,D2,D3,D5,D6,D7,D9,D10,D11,D11A,D11B,D12,D14,D15,D16,D17,F2,F3,F5,F6,F7,F8,F9,F10,F11,H2,H3,H4,H5,D0,F0 processBox
    class C,E,G,I,J outputBox
    class T,T1,T2,T3,DS,DS1,DS2,DS3 systemBox
    class A1,A2,A3,A4 inputBox
    class MCP,MCP1,MCP2,MCP3 mcpBox
    class PERF,PERF1,PERF2,PERF3 perfBox
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and instructions on how to submit pull requests.

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---
<div align="center">

**OneCite** - Simple, Accurate, and Powerful Citation Management ✨

[⭐ Star on GitHub](https://github.com/HzaCode/OneCite) • [🚀 Try the Web App](http://hezhiang.com/onecite) • [📖 Read the Docs](https://onecite.readthedocs.io) • [🐛 Report an Issue](https://github.com/HzaCode/OneCite/issues) • [💬 Start a Discussion](https://github.com/HzaCode/OneCite/discussions)

</div>
