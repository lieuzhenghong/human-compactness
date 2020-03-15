import numpy as np
import pandas as pd


df = pd.read_csv('./40_docs/data.csv')
print(df.to_latex())


def big_positives(row):
    if (row['pct_variance']) < 0 and row['p-value'] < 0.01:
        return row
    else:
        return None


def big_negs(row):
    print(row)
    if (row['pct_variance']) < -5:
        return row
    return None


big_mags = (df.apply(big_positives, axis=1)).dropna()
print(big_mags)
# big_mags.groupby('metric').count()

print(big_mags.groupby('metric').count())
