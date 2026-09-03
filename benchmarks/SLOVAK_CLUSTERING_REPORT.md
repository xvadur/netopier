# Slovak clustering benchmark

Dataset: `slovak-live-title-clusters-2026-09-02` (22 public RSS titles)
Review status: **provisional**

| Method | Precision | Recall | F1 | False merges | False splits | Runtime ms |
|---|---:|---:|---:|---:|---:|---:|
| tfidf-dbscan@0.34 | 1.0000 | 0.5000 | 0.6667 | 0 | 3 | 0.775 |
| temporal-centroid@0.83 | 1.0000 | 0.8333 | 0.9091 | 0 | 1 | 0.271 |
| temporal-centroid@0.79 | 1.0000 | 0.8333 | 0.9091 | 0 | 1 | 0.173 |

Selected runtime setting: **temporal-centroid@0.83**.

The 0.83 result is the selected live title-plus-RSS-text vector path. The lexical baseline uses word unigram/bigram TF-IDF and DBSCAN with cosine distance, `min_samples=1`. The 0.79 run is the required parameter comparison.

Peak process RSS observed: 64.1 MiB.

## Evidence boundary

Labels are provisional and need Adam's editorial ratification. This window did not contain a verified article update-over-time example. The dataset stores only public titles and URLs; full RSS bodies and vectors remain in the ignored local database. False merges are treated as costlier than false splits.
