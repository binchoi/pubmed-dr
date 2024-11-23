import joblib
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import umap # you may need to pip install umap-learn
import os


def reduce_dim(path_embedding, method='opentsne', n_jobs=8):
    '''
    Reduce the dim of the embeddings
    '''
    path_embd = path_embedding.replace('.embedding', '.embd.npy')

    # load the embeddings
    embeddings = joblib.load(path_embedding)

    if method == 'opentsne':

        # reduce the dim by opentsne
        tsne = TSNE(
            perplexity=30,
            metric="cosine",
            n_jobs=n_jobs,
            verbose=2 # more verbose than using True
        )

        # reduce the dim
        embds_coordinates = tsne.fit_transform(embeddings)

    elif method == 'umap':
        reducer = umap.UMAP()
        embds_coordinates = reducer.fit_transform(embeddings)

    elif method == 'pca':
        reducer = PCA(n_components=2)
        embds_coordinates = reducer.fit_transform(embeddings)

    else:
        raise ValueError('unknown method %s' % method)
    
    print('* printing head of coordniates')
    print(embds_coordinates[:5])

    np.save(path_embd, embds_coordinates)

    if os.path.exists(path_embd):
        print('* saved embds to %s' % path_embd)
    else:
        print('* error saving embds to %s' % path_embd)

    return path_embd


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Reduce dimensions of embeddings at given path'
    )

    parser.add_argument('--path', default=None, type=str, help='Embeddings joblib dump file path')
    parser.add_argument('--n_jobs', default=6, type=int, help='Number of CPU cores for t-SNE')
    args = parser.parse_args()

    reduce_dim(args.path)
