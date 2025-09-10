import argparse
import numpy as np
import pandas as pd
import torch
from sklearn.metrics.pairwise import cosine_similarity, pairwise_distances
from sklearn.decomposition import PCA
from sklearn.manifold import SpectralEmbedding
import matplotlib.pyplot as plt

# デフォルトパラメータ
DEFAULT_PARAMS = {
    "n_components": 2,
    "steps": 300,
    "k": 5,
    "alpha1": 5.0,
    "alpha2": 1.0,
    "a": 1.0,
    "b": 1.0,
    "alpha_mix": 0.5,
    "tau": 0.5,
    "lambda_repel": 5.0,
    "gamma": 30.0,
    "init_mode": "spectral",  # "random", "pca", "spectral"
    "device": "cpu"
}

# ペア抽出
def extract_mutual_pairs(X, k, alpha1, alpha2):
    cos_sim = cosine_similarity(X)
    eu_dist = pairwise_distances(X)
    W = np.exp(-alpha1 * (1 - cos_sim)**2 - alpha2 * eu_dist**2)
    topk = np.argsort(-W, axis=1)[:, :k]
    mutual = [(i, j) for i in range(len(W)) for j in topk[i] if i != j and i in topk[j]]
    return W, np.array(mutual)

# 初期埋め込み
def spectral_init(X, n_components):
    embedder = SpectralEmbedding(n_components=n_components)
    return embedder.fit_transform(X)

# 距離カーネルの混合
def combined_q_ij(d_ij, a, b, alpha_mix):
    q_std = 1 / (1 + a * d_ij ** (2 * b))
    q_gauss = torch.exp(-a * d_ij ** (2 * b))
    return alpha_mix * q_std + (1 - alpha_mix) * q_gauss

# repel付き損失関数
def loss_with_repel(Y, W, i_idx, j_idx, a, b, tau, gamma, lambda_repel, alpha_mix):
    dist = torch.cdist(Y, Y)
    d_ij = dist[i_idx, j_idx]
    q_ij = combined_q_ij(d_ij, a, b, alpha_mix)
    w_ij = W[i_idx, j_idx]
    L_attr = torch.sum(w_ij * (q_ij - 1)**2)
    repel = torch.sigmoid((d_ij - tau) * gamma)
    L_repel = torch.sum(w_ij * repel * d_ij**2)
    return L_attr + lambda_repel * L_repel

# 最適化
def optimize(Y, loss_fn, steps):
    optimizer = torch.optim.Adam([Y], lr=0.02)
    for _ in range(steps):
        loss = loss_fn(Y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return Y.detach().cpu().numpy()

# 散布図保存
def scatter_by_label(Y, labels, title="Embedding", filename="embedding_result.png"):
    if Y.shape[1] != 2:
        print(" Scatter plot skipped because the data is not two-dimensional.")
        return
    plt.figure(figsize=(5, 4))
    for lbl in sorted(set(labels)):
        idx = labels == lbl
        plt.scatter(Y[idx, 0], Y[idx, 1], label=lbl, s=10, alpha=0.7)
    plt.title(title)
    plt.legend(fontsize=8, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f" Saved scatter plot to {filename}")

# 埋め込み結果保存
def save_embedding_csv(Y, labels, filename="embedding.csv"):
    df_out = pd.DataFrame(Y, columns=[f"dim{i+1}" for i in range(Y.shape[1])])
    df_out["label"] = labels
    df_out.to_csv(filename, index=False)
    print(f" Saved embedding to {filename}")

# 実行部
def run_embedding(input_csv, output_csv="embedding.csv", plot_file="embedding_result.png", **params):
    df = pd.read_csv(input_csv)
    X = df.select_dtypes(include=[np.number]).values.astype(np.float32)
    labels = df["label"].astype(str).values if "label" in df.columns else np.array(["unlabeled"] * len(df))

    W, pairs = extract_mutual_pairs(X, params["k"], params["alpha1"], params["alpha2"])

    if params["init_mode"] == "pca":
        init_Y = PCA(n_components=params["n_components"]).fit_transform(X)
    elif params["init_mode"] == "spectral":
        init_Y = spectral_init(X, params["n_components"])
    else:
        init_Y = np.random.normal(0, 1, size=(len(X), params["n_components"]))

    Y = torch.tensor(init_Y, requires_grad=True, device=params["device"])
    W_t = torch.tensor(W, device=params["device"])
    i_idx = torch.tensor(pairs[:, 0], device=params["device"])
    j_idx = torch.tensor(pairs[:, 1], device=params["device"])

    Y_embed = optimize(
        Y,
        lambda Y: loss_with_repel(Y, W_t, i_idx, j_idx,
                                  params["a"], params["b"], params["tau"],
                                  params["gamma"], params["lambda_repel"], params["alpha_mix"]),
        params["steps"]
    )

    save_embedding_csv(Y_embed, labels, output_csv)
    scatter_by_label(Y_embed, labels, filename=plot_file)

# CLI対応
def main():
    parser = argparse.ArgumentParser(description="Custom Embedding Tool")
    parser.add_argument("input_csv", help="Path to input CSV file")
    parser.add_argument("--output_csv", default="embedding.csv", help="Output CSV file")
    parser.add_argument("--plot_file", default="embedding_result.png", help="Scatter plot image file")

    # DEFAULT_PARAMS に基づいて引数を自動追加
    for key, val in DEFAULT_PARAMS.items():
        parser.add_argument(f"--{key}", type=type(val), default=val, help=f"{key} (default: {val})")

    args = parser.parse_args()
    params = {key: getattr(args, key) for key in DEFAULT_PARAMS}

    run_embedding(args.input_csv, args.output_csv, args.plot_file, **params)

if __name__ == "__main__":
    main()