# UC2 Setups Analysis Automation

This repository includes automated analysis of UC2 setup files using GitHub Actions.

## 🚀 How it Works

The GitHub Action automatically:

1. **Triggers on:**
   - Push to `main` or `master` branch (when JSON files in `setups/` or `analyze_setups.py` change)
   - Pull requests to `main` or `master` branch
   - Manual workflow dispatch

2. **Analysis Process:**
   - Sets up Python environment with pandas
   - Runs `analyze_setups.py` script
   - Generates/updates `setups_analysis.csv`

3. **Output:**
   - Commits updated CSV file back to repository (on push events)
   - Uploads analysis results as workflow artifact
   - Comments on PRs with analysis summary

## 📊 Analysis Output

The analysis creates a CSV database (`setups_analysis.csv`) containing:

- **Setup Metadata:** name, verification status, collection, author, GitHub link
- **Component Counts:** Usage count for each UC2 component file across all setups
- **Summary Statistics:** Total components, verification rates, top authors/collections

## 🔧 Manual Execution

You can also run the analysis manually:

```bash
# Install dependencies
pip install pandas

# Run analysis
python analyze_setups.py
```

## 📁 File Structure

```
├── .github/
│   └── workflows/
│       └── analyze-setups.yml    # GitHub Action workflow
├── setups/                       # JSON setup files
│   ├── setup-*.json
│   └── optikit-layout-*.json
├── analyze_setups.py            # Analysis script
├── setups_analysis.csv          # Generated database (auto-updated)
└── README.md
```

## 🔍 Workflow Status

[![Analyze UC2 Setups](https://github.com/beniroquai/openUC2-OptiKit-Store/actions/workflows/analyze-setups.yml/badge.svg)](https://github.com/beniroquai/openUC2-OptiKit-Store/actions/workflows/analyze-setups.yml)

## 📝 Notes

- The workflow includes `[skip ci]` in commit messages to prevent infinite loops
- Analysis results are retained as artifacts for 30 days
- Only changes to relevant files (JSON setups or analysis script) trigger the workflow
- The CSV file uses semicolon (`;`) as delimiter for better compatibility with Excel
