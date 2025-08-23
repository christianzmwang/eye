# Norwegian Companies Domain Finder

This project finds websites associated with the 1000 biggest Norwegian private companies by revenue, using data from BRREG (Brønnøysundregistrene - Norwegian Business Register).

## Features

- Fetches company data from BRREG's official API
- Filters companies by size and estimates revenue
- Discovers domains associated with each company
- Outputs organization number, business name, and unique domains
- Supports both JSON and CSV output formats
- Comprehensive logging and progress tracking

## Output

The tool provides:
- **Organization Number**: Norwegian organization number from BRREG
- **Business Name**: Official company name
- **Unique Domains**: List of domains associated with the company
- **Additional Data**: Revenue estimates, employee count, industry classification, etc.

## Installation

1. Clone or download this project
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main.py
```

This will:
- Fetch companies from BRREG
- Find the top 1000 companies by estimated revenue
- Discover domains for each company
- Save results to `norwegian_companies_domains.json`

### Advanced Usage

```bash
# Limit to top 500 companies
python main.py --max-companies 500

# Save as CSV instead of JSON
python main.py --output-format csv --output-file results.csv

# Filter for larger companies (minimum 50 employees)
python main.py --min-employees 50

# Custom output file
python main.py --output-file my_results.json
```

### Command Line Options

- `--max-companies`: Maximum number of companies to process (default: 1000)
- `--output-format`: Output format - 'json' or 'csv' (default: json)
- `--output-file`: Output file name (default: norwegian_companies_domains.json)
- `--min-employees`: Minimum employees to filter companies (default: 10)

## How It Works

### 1. Data Collection
The tool uses BRREG's public API to fetch Norwegian company data:
- Company names and organization numbers
- Employee counts
- Industry classifications (NACE codes)
- Business addresses
- Founding dates

### 2. Revenue Estimation
Since BRREG doesn't provide revenue data directly, the tool estimates revenue using:
- Employee count correlations
- Industry-specific multipliers
- Company size classifications

**Note**: Revenue estimates are approximations and should not be considered accurate financial data.

### 3. Domain Discovery
The tool finds domains using multiple approaches:
- Name-based domain guessing (company name variations)
- Common Norwegian TLD patterns (.no, .com, .org, .net)
- DNS verification to confirm domain accessibility
- Website content analysis for additional domains

### 4. Data Verification
- Verifies domains are accessible via DNS lookup
- Attempts HTTP/HTTPS connections to confirm websites
- Filters out invalid or inaccessible domains

## Project Structure

```
├── main.py                 # Main execution script
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── src/
    ├── __init__.py        # Package initialization
    ├── brreg_client.py    # BRREG API client
    ├── domain_finder.py   # Domain discovery logic
    └── company_analyzer.py # Company analysis and revenue estimation
```

## Output Format

### JSON Output
```json
{
  "metadata": {
    "generated_at": "2024-01-15T10:30:00",
    "total_companies": 1000,
    "total_domains": 2456
  },
  "companies": [
    {
      "organization_number": "123456789",
      "business_name": "Example Company AS",
      "unique_domains": ["example.no", "example.com"],
      "estimated_revenue": 50000000,
      "employees": 25,
      "industry": "manufacturing",
      "municipality": "Oslo",
      "founded": "2010-05-15",
      "nace_code": "25.11"
    }
  ]
}
```

### CSV Output
```csv
Organization Number,Business Name,Unique Domains,Domain Count,Estimated Revenue (NOK),Employees,Industry,Municipality,Founded,NACE Code
123456789,Example Company AS,"example.no; example.com",2,50000000,25,manufacturing,Oslo,2010-05-15,25.11
```

## Limitations

1. **Revenue Estimates**: The tool provides revenue estimates based on employee count, not actual financial data
2. **Domain Discovery**: May not find all domains associated with a company, especially:
   - Domains registered to subsidiaries
   - Domains registered to individuals rather than the company
   - Domains with non-obvious naming patterns
3. **API Rate Limits**: Respects BRREG API rate limits, which may slow processing
4. **Data Accuracy**: Results depend on data quality in BRREG and domain accessibility

## Legal and Ethical Considerations

- All data is sourced from public registers and APIs
- Respects website robots.txt and rate limiting
- No personal data is collected or stored
- Use responsibly and in compliance with applicable laws

## Technical Notes

### BRREG API
- Uses the official BRREG Enhetsregisteret API
- Endpoint: `https://data.brreg.no/enhetsregisteret/api/enheter`
- No API key required for basic usage
- Includes respectful rate limiting

### Domain Verification
- Uses DNS lookups to verify domain existence
- Attempts HTTP/HTTPS connections to confirm accessibility
- Timeout handling for unreachable domains

### Performance
- Processes companies in batches
- Includes progress logging
- Average processing time: ~2-5 seconds per company

## Troubleshooting

### Common Issues

1. **Network Timeouts**: Some domains may be slow to respond. The tool includes timeout handling.

2. **API Rate Limits**: If you encounter rate limiting, the tool includes automatic delays.

3. **Missing Domains**: Not all companies have discoverable domains. This is expected behavior.

### Log Files
The tool creates `norwegian_companies.log` with detailed execution information for debugging.

## Contributing

This is a specialized tool for Norwegian business research. Contributions welcome for:
- Improved domain discovery algorithms
- Additional data sources integration
- Performance optimizations
- Bug fixes

## License

This project is provided as-is for research and business intelligence purposes.
