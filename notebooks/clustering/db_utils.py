import pandas as pd


def _get_points_df(
        self,
        path_tsv,
        delimiter,
        points,
    ):
        df = pd.read_csv(
            path_tsv,
            sep=delimiter
        )
        print("* loaded df")

        # merge embds
        df['x'] = points[:, 0]
        df['y'] = points[:, 1]
        
        # drop unnecessary columns
        df.drop(columns=['title', 'journal', 'year', 'abstract'], inplace=True)  

        print('* merged embds to df')
        return df

