import requests
import argparse
import urllib

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def parse_args():
    """
    Returns:
        arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--search_term", type=str, required=True)
    parser.add_argument("--search_ligand", type=str, required=True)
    parser.add_argument("--output_folder", type=str, required=True)

    args = parser.parse_args()
    return args

def download_file(url, file_name, output_folder):
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open('{}/{}.sdf'.format(output_folder, file_name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()

def main():
    ### !!!
    #candidate_list = ["remdesivir", "ribavirin", "favipiravir", "galidesivir"]

    args = parse_args()
    
    api_url = 'http://best.korea.ac.kr'
    search_term = urllib.quote(args.search_term)
    search_ligand = args.search_ligand
    output_folder = args.output_folder
    
    drug_list = []
    if search_ligand == "":
        # query first time to get cnt
        print("Searching drugs...")
        response = requests.get("{}/s?otype=5&q={}&t=l&wt=xml&tr=l.xsl&start=0&rows=1".format(api_url, search_term))
        root = ET.fromstring(response.text)
        result = root.find('.//result')
        cnt = result.attrib['numFound']
        print("Found {} different drugs".format(cnt))
        
        # query second time to get all drug
        print("Getting all drugs...")
        response = requests.get("{}/s?otype=5&q={}&t=l&wt=xml&tr=l.xsl&start=0&rows={}".format(api_url, search_term, cnt))
        root = ET.fromstring(response.text)
        results = root.findall('.//result/object')
        drug_list = [term.attrib['oname'] for term in results]
    else:
        drug_list = search_ligand.split(",")
    
    # download each drug SDF file
    print("Downloading sdf file from PubChem...")
    for drug in drug_list:    
        print("---{}".format(drug))
        api_url = 'https://pubchem.ncbi.nlm.nih.gov'
        url = '{}/rest/pug/compound/name/{}/record/SDF'.format(api_url, drug)
        try:
            download_file(url, drug, output_folder)
        except:
            print("download error: {}".format(drug))

if __name__ == "__main__":
    main()
