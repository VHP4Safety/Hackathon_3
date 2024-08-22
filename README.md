# Hackathon_3
Repository to prepare for the Hackathon 3 - Using LLMs

# BridgeDB Agent Interaction Tool

## Description
The BridgeDB Interaction Tool is a Streamlit-based web application that allows users to interact with the BridgeDB API using natural language queries. It facilitates the mapping of identifiers across various biological and chemical databases, making it easier for researchers and bioinformaticians to cross-reference and retrieve information about genes, proteins, and chemical compounds.

## Features
- Map gene identifiers across different databases (e.g., Ensembl, HGNC, RefSeq)
- Look up chemical compounds in databases like PubChem, ChEBI, or DrugBank
- Cross-reference identifiers between different biological databases
- Natural language interface for easy querying
- Informative responses with links to relevant resources

## Installation

### Prerequisites
- Python 3.7+
- pip

### Steps
1. Clone the repository
2. Create a virtual environment (optional but recommended)
3.  Install the required packages
4. Set up your OpenAI API key:
- Create a `.env` file in the project root
- Add your OpenAI API key to the file:

  ```
  OPENAI_API_KEY=your_api_key_here
  ```

## Usage
1. Run the Streamlit app:
2. 2. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`)

3. Enter your query in the text box and press Enter

4. View the results displayed on the page

## Example Queries
- "What are the identifiers for the TP53 gene?"
- "Find mappings for the chemical compound Aspirin"
- "Map the Ensembl ID ENSG00000139618 to other databases"

## Project Structure
- `bridgedb_app.py`: Main Streamlit application
- `BridgeDB_API_Integration.ipynb`: Jupyter notebook with development process and additional examples
- `requirements.txt`: List of Python package dependencies
- `.env`: File for storing the OpenAI API key (not tracked in git)

## Contributing
Contributions to improve the BridgeDB Interaction Tool are welcome. Please feel free to submit a Pull Request.

## Acknowledgements
- BridgeDB API
- OpenAI for providing the language model capabilities
- Streamlit for the web application framework
