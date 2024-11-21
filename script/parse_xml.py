import os
import subprocess
import tempfile

import pandas as pd


def parse_xml(path_xml, path_out=None):
    '''
    Parse a XML file of pubmed data
    '''
    all_paths = []
    path_out = path_out or path_xml.replace('.xml', '.raw')

    # second, get the title
    with tempfile.NamedTemporaryFile(delete=False) as f: path_title = f.name
    all_paths.append(path_title)
    xtract_title(path_xml, path_title)

    # third, get the journal
    with tempfile.NamedTemporaryFile(delete=False) as f: path_journal = f.name
    all_paths.append(path_journal)
    xtract_journal(path_xml, path_journal)

    # then, get year
    with tempfile.NamedTemporaryFile(delete=False) as f: path_year = f.name
    all_paths.append(path_year)
    xtract_year(path_xml, path_year)

    # then, get abstract
    with tempfile.NamedTemporaryFile(delete=False) as f: path_abstract = f.name
    all_paths.append(path_abstract)
    xtract_abstract(path_xml, path_abstract)

    # then, get mesh terms
    with tempfile.NamedTemporaryFile(delete=False) as f: path_mesh_terms = f.name
    all_paths.append(path_mesh_terms)
    xtract_mesh_terms(path_xml, path_mesh_terms)

    # then, get mesh topics
    with tempfile.NamedTemporaryFile(delete=False) as f: path_mesh_topics = f.name
    xtract_mesh_topics(path_xml, path_mesh_topics)
    all_paths.append(path_mesh_topics)

    # then, get conclusions
    # with tempfile.NamedTemporaryFile(delete=False) as f: path_conclusions = f.name
    # all_paths.append(path_conclusions)
    # xtract_conclusions(path_xml, path_conclusions)

    df = pd.read_csv(
        all_paths[0],
        sep='\t'
    )
    
    print('* found %s rows in the first df' % len(df))
    for path in all_paths[1:]:
        df_tmp = pd.read_csv(
            path,
            sep='\t'
        )
        df = pd.merge(df, df_tmp, on="pmid")
        print('* merged df(%s) + %s(%s)' % (len(df), path, len(df_tmp)))

    # make sure the year is int
    # if year is na, just assume it is 2000
    df['year'].fillna(2000, inplace=True)
    df['year'] = df['year'].astype(int)

    # save the final df to given path
    df.to_csv(
        path_out,
        sep='\t',
        index=False
    )
    print('* saved the final df to %s' % path_out)

    # finally, delete all tmp files
    for path in all_paths:
        try:
            os.remove(path)
            print('* removed tmp file %s' % path)
        except Exception as err:
            print('* ERROR when removing %s' % path)

    return path_out



def xtract_title(path_xml, path_out):
    '''Extract title from a given XML
    '''
    cmd = f"""cat {path_xml} | \
    xtract -pattern PubmedArticle \
        -element MedlineCitation/PMID,ArticleTitle | \
    (echo "pmid\ttitle"; cat) > {path_out}
    """
    print("* xtracting title ...")
    print(cmd)
    result = subprocess.run(cmd, shell=True)
    return result
    

def xtract_journal(path_xml, path_out):
    '''Extract journal from a given XML
    '''
    cmd = f"""cat {path_xml} | \
    xtract -pattern PubmedArticle \
        -element MedlineCitation/PMID,Journal/Title | \
    (echo "pmid\tjournal"; cat) > {path_out}
    """
    print("* xtracting journal ...")
    print(cmd)
    result = subprocess.run(cmd, shell=True)
    return result
    

def xtract_year(path_xml, path_out):
    '''Extract year from a given XML
    '''
    cmd = f"""cat {path_xml} | \
    xtract -pattern PubmedArticle \
        -element MedlineCitation/PMID,PubDate/Year | \
    (echo "pmid\tyear"; cat) > {path_out}
    """
    print("* xtracting year ...")
    print(cmd)
    result = subprocess.run(cmd, shell=True)
    return result
    

def xtract_abstract(path_xml, path_out):
    '''Extract abstract from a given XML
    '''
    cmd = f"""cat {path_xml} | \
    xtract -pattern PubmedArticle \
        -element MedlineCitation/PMID \
        -block Abstract -sep " " -element AbstractText | \
    (echo "pmid\tabstract"; cat) > {path_out}
    """
    print("* xtracting abstract ...")
    print(cmd)
    result = subprocess.run(cmd, shell=True)
    return result
    

def xtract_mesh_terms(path_xml, path_out):
    '''Extract mesh terms from a given XML
    '''
    cmd = f"""cat {path_xml} | \
    xtract -pattern PubmedArticle \
        -element MedlineCitation/PMID \
        -block MeshHeadingList -sep ";" -element DescriptorName | \
    (echo "pmid\tmesh_terms"; cat) > {path_out}
    """
    print("* xtracting mesh_terms")
    print(cmd)
    result = subprocess.run(cmd, shell=True)
    return result
    

def xtract_mesh_topics(path_xml, path_out):
    '''Extract mesh_topics from a given XML
    '''
    cmd = f"""cat {path_xml} | \
    xtract -pattern PubmedArticle \
        -element MedlineCitation/PMID \
        -block MeshHeadingList -sep ";" -element QualifierName | \
    (echo "pmid\tmesh_topics"; cat) > {path_out}
    """
    print("* xtracting mesh_topics")
    print(cmd)
    result = subprocess.run(cmd, shell=True)
    return result


def xtract_conclusions(path_xml, path_out):
    '''Extract conclusions from a given XML
    '''
    print("* xtracting conclusions by ET ...")
    parser = ET.XMLParser(recover=True)
    tree = ET.parse(path_xml, parser=parser)

    # with open(path_xml, 'r') as f:
    #     tree = ET.parse(f)
    root = tree.getroot()

    pubmed_data = []
    pubmed_articles = root.findall(".//PubmedArticle")
    print('* found %s pubmed_articles' % (len(pubmed_articles)))

    for pubmed_article in tqdm(pubmed_articles):
        pmid = pubmed_article.findtext(".//PMID")
        pubmed_entry = {
            'pmid': pmid,
            'conclusions': ''
        }

        abst_elements = pubmed_article.findall(".//AbstractText")
        conclusions = []
        for abst in abst_elements:
            if abst.get('NlmCategory') == 'CONCLUSIONS':
                conclusions.append(abst.text)

        pubmed_entry["conclusions"] = ' '.join(conclusions)

        # ok, we have got the information for this paper
        pubmed_data.append(pubmed_entry)

    # convert to df
    df = pd.DataFrame(pubmed_data)
    df.to_csv(
        path_out,
        sep='\t',
        index=False
    )
    print('* extracted conclusions into %s' % path_out)
    
    return df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Parse PubMed XML file at given path'
    )

    parser.add_argument('--path', default=None, type=str, help='Pubmed XML path')
    args = parser.parse_args()

    parse_xml(args.path)

