import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.tools import BaseTool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
import requests

# Load environment variables
load_dotenv()

# Set OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API Key is not set. Please check your .env file.")
    st.stop()

os.environ["OPENAI_API_KEY"] = api_key

# BridgeDB API Wrapper
class BridgeDbAPI:
    BASE_URL = "https://webservice.bridgedb.org"

    @staticmethod
    def map_identifier(species, source_ds, identifier):
        url = f"{BridgeDbAPI.BASE_URL}/{species}/xrefs/{source_ds}/{identifier}"
        response = requests.get(url)
        if response.status_code == 200:
            return [line.split('\t') for line in response.text.strip().split('\n')]
        else:
            return f"Error: {response.status_code} - {response.reason}"

# IdentifierMappingTool
class IdentifierMappingTool(BaseTool):
    name = "identifier_mapping"
    description = """Useful for mapping identifiers between different biological databases. 
    Input can be in the following formats:
    1. 'species, source_ds, identifier' (e.g., 'Homo sapiens, Ensembl, ENSG00000139618')
    2. 'source_ds, identifier' (e.g., 'Cpc, 2478')
    3. Just the identifier or gene/chemical name (e.g., 'ENSG00000139618' or 'BRCA2' or 'Busulfan')"""

    def _run(self, query: str) -> str:
        parts = [p.strip() for p in query.split(",")]
        
        if len(parts) == 1:
            return self._flexible_mapping(parts[0])
        elif len(parts) == 2:
            source_ds, identifier = parts
            return self._map_identifier("Human", source_ds, identifier)
        elif len(parts) == 3:
            species, source_ds, identifier = parts
            return self._map_identifier(species, source_ds, identifier)
        else:
            return "Error: Invalid query format."

    def _flexible_mapping(self, query):
        # Try mapping as Ensembl gene ID
        result = self._map_identifier("Human", "En", query)
        if "Error" not in result:
            return result

        # Try mapping as HGNC ID
        if query.startswith("HGNC:"):
            result = self._map_identifier("Human", "H", query)
            if "Error" not in result:
                return result

        # Try mapping as gene symbol
        result = self._map_identifier("Human", "H", query)
        if "Error" not in result:
            return result

        # Try mapping as PubChem compound ID
        result = self._map_identifier("Human", "Cpc", query)
        if "Error" not in result:
            return result

        # If it fails, assume it's a chemical name and try to find its PubChem ID
        pubchem_id = self._get_pubchem_id(query)
        if pubchem_id:
            return self._map_identifier("Human", "Cpc", pubchem_id)
        
        return f"Error: Unable to map identifier or find compound: {query}"

    def _map_identifier(self, species, source_ds, identifier):
        url = f"https://bridgedb.cloud.vhp4safety.nl/{species}/xrefs/{source_ds}/{identifier}"
        response = requests.get(url)
        if response.status_code == 200:
            mappings = [line.split('\t') for line in response.text.strip().split('\n')]
            if mappings:
                formatted_result = ""
                for item in mappings:
                    if item[1] == "GeneOntology":
                        formatted_result += f"- Gene Ontology term: {item[0]} (Look up at http://geneontology.org/)\n"
                    elif item[1] == "UCSC Genome Browser":
                        formatted_result += f"- UCSC Genome Browser identifier: {item[0]} (Use gene name or genomic location to search)\n"
                    else:
                        formatted_result += f"- {item[0]}\t{item[1]}\n"
                return f"Mapped identifiers for {identifier} from {source_ds}:\n{formatted_result}"
            else:
                return f"No mappings found for {identifier} from {source_ds}"
        else:
            return f"Error: Failed to retrieve mappings. Status code: {response.status_code}"

    def _get_pubchem_id(self, chemical_name):
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/cids/TXT"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        return None

    async def _arun(self, query: str) -> str:
        return self._run(query)

# Create BridgeDB Agent
def create_bridgedb_agent():
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [IdentifierMappingTool()]
    memory = MemorySaver()
    agent_executor = create_react_agent(model, tools, checkpointer=memory)
    return agent_executor

bridgedb_agent = create_bridgedb_agent()

# Streamlit App
st.title("BridgeDB Interaction Tool")

st.write("""
This tool allows you to interact with the BridgeDB API using natural language queries. It helps you find and map identifiers across various biological and chemical databases.

What you can do:
1. Map gene identifiers: Find corresponding IDs for genes across different databases (e.g., Ensembl, HGNC, RefSeq).
2. Look up chemical compounds: Get identifiers for chemicals in databases like PubChem, ChEBI, or DrugBank.
3. Cross-reference identifiers: Translate IDs between different biological databases.

How to use:
- Enter a gene name, chemical compound, or specific identifier.
- Ask for mappings between different databases.
- Use natural language to inquire about biological entities.

Examples:
- "What are the identifiers for the TP53 gene?"
- "Find mappings for the chemical compound Aspirin"
- "Map the Ensembl ID ENSG00000139618 to other databases"

Note:
- Gene Ontology (GO) terms represent biological concepts and can be looked up at http://geneontology.org/
- UCSC Genome Browser identifiers are internal; use the gene name or genomic location when searching at https://genome.ucsc.edu/

Start by typing your query in the box below!rching the UCSC Genome Browser.
""")

query = st.text_input("Enter your query here:")

if query:
    st.write("Processing your query...")
    config = {"configurable": {"thread_id": "bridgedb_conversation"}}
    response = ""
    for chunk in bridgedb_agent.stream(
        {"messages": [HumanMessage(content=query)]},
        config
    ):
        if 'agent' in chunk and 'messages' in chunk['agent']:
            for message in chunk['agent']['messages']:
                if hasattr(message, 'content') and message.content:
                    response += message.content + "\n"
    
    st.write("Response:")
    st.write(response)

st.write("""
Example queries:
- What are the mappings for the compound with PubChem ID 2478?
- Find mappings for Busulfan
- Map the gene ENSG00000139618 from Ensembl to other databases
""")