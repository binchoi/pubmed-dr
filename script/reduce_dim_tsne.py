import joblib
import numpy as np
from sklearn.manifold import TSNE
import umap # you may need to pip install umap-learn


def reduce_dim(path_embedding, method='opentsne'):
    '''
    Reduce the dim of the embeddings
    '''
    path_embd = path_embd or path_embedding.replace('.embedding', '.embd.npy')

    # load the embeddings
    embeddings = joblib.load(path_embedding)

    if method == 'opentsne':

        # reduce the dim by opentsne
        tsne = TSNE(
            perplexity=30,
            metric="cosine",
            n_jobs=8,
            verbose=True
        )

        # reduce the dim
        embds = tsne.fit(embeddings)

        embds_coordinates = embds[:, :2]

    elif method == 'umap':
        reducer = umap.UMAP()
        embds_coordinates = reducer.fit_transform(embeddings)

    else:
        raise ValueError('unknown method %s' % method)
    
    print('* printing head of coordniates')
    print(embds_coordinates[:5])

    np.save(path_embd, embds_coordinates)

    print('* saved embds to %s' % path_embd)
    return path_embd


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Reduce dimensions of embeddings at given path'
    )

    parser.add_argument('--path', default=None, type=str, help='Embeddings joblib dump file path')
    args = parser.parse_args()

    reduce_dim(args.path)
