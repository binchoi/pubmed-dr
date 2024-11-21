import pandas as pd


def calc_embedding(path_tsv, path_out=None):
    path_out = path_out or path_tsv.replace('.raw', '.embedding')
    '''
    Calculate the embedding of the title + abstracts
    '''
    # load the df
    print('* loading df ...')
    df = pd.read_csv(
        path_tsv,
        sep='\t'
    )
    print('* loaded df %s' % len(df))

    # load the model
    from sentence_transformers import SentenceTransformer
    model_name = 'BAAI/bge-small-en-v1.5'
    model = SentenceTransformer(model_name)
    print('* loaded model %s' % model_name)

    # creating the text to be embedded
    print('* creating the text to be embedded ...')
    text_to_be_embedded = df.apply(
        lambda r: '%s - %s ' % (r.title, r.abstract),
        axis=1
    )
    print('* created the text to be embedded %s' % len(text_to_be_embedded))
    
    # encode the texts
    print("* encoding the texts ...")
    embeddings = model.encode(
        text_to_be_embedded,
        show_progress_bar=True,
    )

    # save the embeddings
    import joblib
    print("* saving the embeddings ...")
    joblib.dump(
        embeddings,
        path_out
    )
    print('* saved embeddings to %s' % path_out)
    return path_out



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Calc Embeddings from PubMed TSV file'
    )

    parser.add_argument('--path', default=None, type=str, help='TSV path')
    args = parser.parse_args()

    calc_embedding(args.path)
