from datetime import datetime
import subprocess
from typing import Dict

"""
Command example:
    ```
    python ./script/get_pubmed_xml.py --pm_query "working memory"
    ```

Pre-requisite: Install ncbi-entrez-direct
    (Dockerfile-syntax) script
    ```
    RUN apt-get update && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y gcc perl wget rsync libfftw3-dev && \
        sh -c "$(wget -q https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -O -)"
    RUN rsync -a /root/edirect/ /usr/local/edirect/ && rm -rf /root/edirect
    ENV PATH="/usr/local/edirect:$PATH"
    ```
"""

def get_pubmed_xml(query: str) -> str:
    xml_path = f"./dataset/pubmed_{datetime.now().strftime('%Y%m%d')}_{query.split()[0]}.xml"
    print(f"* pubmed_xml_path: {xml_path}")

    cmd = get_pubmed_xml_command(query, xml_path)
    
    print(f"* downloading XML; cmd: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise ValueError(f"Failed to download XML: {result}")
    
    print('* downloaded XML to %s' % xml_path)
    return xml_path


def get_pubmed_xml_command(query: str, xml_path: str) -> str:
    if query == '':
        raise ValueError("PubMed query is empty")
    
    print(f"* pubmed query found: {query}")
    
    _query = query.replace('"', '\"')  # TODO: need to strengthen robustness
    cmd = f"""esearch -db pubmed -query '{_query}' | \
efetch -format xml > {xml_path}
    """
    return cmd


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Get PubMed XML file for given query'
    )

    parser.add_argument('--pm_query', default=None, type=str, help='Pubmed query')
    args = parser.parse_args()

    get_pubmed_xml(args.pm_query)
