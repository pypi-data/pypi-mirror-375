#!/usr/bin/env python3
"""
NSeekFS Fair Cosine Similarity Benchmark
========================================

Comparação justa de pesquisa vetorial exata (cosine) entre:
- NSeekFS (Rust exact)
- FAISS (IndexFlatIP)
- scikit-learn (NearestNeighbors, brute, cosine)
- NumPy (dot/argpartition baseline)
- SciPy (cdist cosine)
- PyTorch (matmul)

Notas:
- Todos os vetores e queries são NORMALIZADOS antes do build/query.
- As medições usam time.perf_counter no nível Python.
- NSeekFS também reporta o tempo interno do engine (query_detailed).
"""

import time
import numpy as np
import argparse
import sys
import warnings
warnings.filterwarnings('ignore')

AVAILABLE_LIBS = {}

# FAISS
try:
    import faiss  # type: ignore
    AVAILABLE_LIBS['faiss'] = True
except Exception:
    AVAILABLE_LIBS['faiss'] = False

# Annoy (ANN) — deixado opcional e desligado por defeito
try:
    import annoy  # type: ignore  # noqa
    AVAILABLE_LIBS['annoy'] = True
except Exception:
    AVAILABLE_LIBS['annoy'] = False

# scikit-learn
try:
    from sklearn.neighbors import NearestNeighbors  # type: ignore
    AVAILABLE_LIBS['sklearn'] = True
except Exception:
    AVAILABLE_LIBS['sklearn'] = False

# SciPy
try:
    from scipy.spatial.distance import cdist  # type: ignore
    AVAILABLE_LIBS['scipy'] = True
except Exception:
    AVAILABLE_LIBS['scipy'] = False

# PyTorch
try:
    import torch  # type: ignore
    AVAILABLE_LIBS['torch'] = True
except Exception:
    AVAILABLE_LIBS['torch'] = False

AVAILABLE_LIBS['numpy'] = True


def print_section(title: str):
    print(f"\n{'='*60}\n{title}\n{'='*60}")


def normalize_rows(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return x / n.astype(np.float32)


class FairBenchmark:
    """Benchmark de cosine similarity com bibliotecas de pesquisa exata."""

    def benchmark_nseekfs(self, vectors_norm, queries_norm, top_k: int):
        try:
            import nseekfs
        except ImportError:
            return {'success': False, 'error': 'NSeekFS not available'}

        build_start = time.perf_counter()
        index = nseekfs.from_embeddings(vectors_norm, normalized=True, verbose=False)
        build_time = (time.perf_counter() - build_start) * 1000.0

        # warm-up
        index.query(queries_norm[0], top_k=top_k)

        q_times, d_times = [], []
        for q in queries_norm:
            t0 = time.perf_counter()
            index.query(q, top_k=top_k)
            q_times.append((time.perf_counter() - t0) * 1000.0)

            d = index.query_detailed(q, top_k=top_k)
            d_times.append(d.query_time_ms)

        return {
            'success': True,
            'build_time_ms': build_time,
            'avg_time_ms': float(np.mean(q_times)),
            'p95_time_ms': float(np.percentile(q_times, 95)),
            'qps': 1000.0 / float(np.mean(q_times)),
            'all_times': q_times,
            'internal_avg_ms': float(np.mean(d_times)),
            'internal_p95_ms': float(np.percentile(d_times, 95)),
        }

    def benchmark_faiss(self, vectors_norm, queries_norm, top_k: int):
        if not AVAILABLE_LIBS['faiss']:
            return {'success': False, 'error': 'FAISS not available'}
        import faiss

        d = vectors_norm.shape[1]
        build_start = time.perf_counter()
        index = faiss.IndexFlatIP(d)
        index.add(vectors_norm)
        build_time = (time.perf_counter() - build_start) * 1000.0

        q_times = []
        for q in queries_norm:
            t0 = time.perf_counter()
            index.search(q.reshape(1, -1), top_k)
            q_times.append((time.perf_counter() - t0) * 1000.0)

        return {
            'success': True,
            'build_time_ms': build_time,
            'avg_time_ms': float(np.mean(q_times)),
            'p95_time_ms': float(np.percentile(q_times, 95)),
            'qps': 1000.0 / float(np.mean(q_times)),
            'all_times': q_times,
        }

    # ANN (opcional) — NÃO é exact search
    def benchmark_annoy(self, vectors_norm, queries_norm, top_k: int):
        if not AVAILABLE_LIBS['annoy']:
            return {'success': False, 'error': 'Annoy not available'}
        import annoy
        d = vectors_norm.shape[1]

        build_start = time.perf_counter()
        index = annoy.AnnoyIndex(d, 'angular')
        for i, v in enumerate(vectors_norm):
            index.add_item(i, v.tolist())
        index.build(50)
        build_time = (time.perf_counter() - build_start) * 1000.0

        q_times = []
        for q in queries_norm:
            t0 = time.perf_counter()
            index.get_nns_by_vector(q.tolist(), top_k, search_k=-1)
            q_times.append((time.perf_counter() - t0) * 1000.0)

        return {
            'success': True,
            'build_time_ms': build_time,
            'avg_time_ms': float(np.mean(q_times)),
            'p95_time_ms': float(np.percentile(q_times, 95)),
            'qps': 1000.0 / float(np.mean(q_times)),
            'all_times': q_times,
        }

    def benchmark_sklearn(self, vectors_norm, queries_norm, top_k: int):
        if not AVAILABLE_LIBS['sklearn']:
            return {'success': False, 'error': 'scikit-learn not available'}
        from sklearn.neighbors import NearestNeighbors

        build_start = time.perf_counter()
        nn = NearestNeighbors(n_neighbors=top_k, metric='cosine', algorithm='brute')
        nn.fit(vectors_norm)
        build_time = (time.perf_counter() - build_start) * 1000.0

        q_times = []
        for q in queries_norm:
            t0 = time.perf_counter()
            nn.kneighbors([q])
            q_times.append((time.perf_counter() - t0) * 1000.0)

        return {
            'success': True,
            'build_time_ms': build_time,
            'avg_time_ms': float(np.mean(q_times)),
            'p95_time_ms': float(np.percentile(q_times, 95)),
            'qps': 1000.0 / float(np.mean(q_times)),
            'all_times': q_times,
        }

    def benchmark_numpy(self, vectors_norm, queries_norm, top_k: int):
        q_times = []
        for q in queries_norm:
            t0 = time.perf_counter()
            sims = np.dot(vectors_norm, q)  # já normalizado → cosine = dot
            np.argpartition(-sims, top_k)[:top_k]
            q_times.append((time.perf_counter() - t0) * 1000.0)

        return {
            'success': True,
            'build_time_ms': 0.0,
            'avg_time_ms': float(np.mean(q_times)),
            'p95_time_ms': float(np.percentile(q_times, 95)),
            'qps': 1000.0 / float(np.mean(q_times)),
            'all_times': q_times,
        }

    def benchmark_scipy(self, vectors_norm, queries_norm, top_k: int):
        if not AVAILABLE_LIBS['scipy']:
            return {'success': False, 'error': 'SciPy not available'}
        from scipy.spatial.distance import cdist

        q_times = []
        for q in queries_norm:
            t0 = time.perf_counter()
            # cosine distance = 1 - cosine similarity; como já está normalizado,
            # isto é equivalente ao dot, mas via SciPy (mais overhead)
            dists = cdist(vectors_norm, q.reshape(1, -1), metric='cosine').ravel()
            # top-k menores dists = top-k maiores sims
            np.argpartition(dists, top_k)[:top_k]
            q_times.append((time.perf_counter() - t0) * 1000.0)

        return {
            'success': True,
            'build_time_ms': 0.0,
            'avg_time_ms': float(np.mean(q_times)),
            'p95_time_ms': float(np.percentile(q_times, 95)),
            'qps': 1000.0 / float(np.mean(q_times)),
            'all_times': q_times,
        }

    def benchmark_torch(self, vectors_norm, queries_norm, top_k: int):
        if not AVAILABLE_LIBS['torch']:
            return {'success': False, 'error': 'PyTorch not available'}
        import torch

        device = torch.device("cpu")  # CPU-only para comparação justa
        V = torch.from_numpy(vectors_norm).to(device)
        q_times = []

        for q in queries_norm:
            q_t = torch.from_numpy(q).to(device)
            t0 = time.perf_counter()
            sims = torch.mv(V, q_t)  # dot por ser normalizado
            _ = torch.topk(sims, k=top_k)
            q_times.append((time.perf_counter() - t0) * 1000.0)

        return {
            'success': True,
            'build_time_ms': 0.0,
            'avg_time_ms': float(np.mean(q_times)),
            'p95_time_ms': float(np.percentile(q_times, 95)),
            'qps': 1000.0 / float(np.mean(q_times)),
            'all_times': q_times,
        }

    # -------------------------
    # Runner
    # -------------------------

    def run_dataset(self, name: str, n_vectors: int, dims: int, n_queries: int, top_k: int = 10, include_ann: bool = False):
        print_section(f"DATASET {name.upper()}: {n_vectors} × {dims}, {n_queries} queries")

        # dados reprodutíveis
        rng = np.random.default_rng(42)
        vectors = rng.standard_normal((n_vectors, dims), dtype=np.float32)
        queries = rng.standard_normal((n_queries, dims), dtype=np.float32)

        # normalização única para todos (fair)
        vectors_norm = normalize_rows(vectors)
        queries_norm = normalize_rows(queries)

        results = {}
        libs = [
            ("nseekfs", self.benchmark_nseekfs),
            ("faiss",   self.benchmark_faiss),
            # ("annoy",   self.benchmark_annoy),  # ANN — opcional
            ("sklearn", self.benchmark_sklearn),
            ("scipy",   self.benchmark_scipy),
            ("numpy",   self.benchmark_numpy),
            ("torch",   self.benchmark_torch),
        ]
        if include_ann:
            libs.insert(2, ("annoy", self.benchmark_annoy))

        for lib, func in libs:
            print(f"Testing {lib.upper()}...")
            try:
                res = func(vectors_norm, queries_norm, top_k)
                results[lib] = res
                if res.get("success"):
                    print(f"  Build: {res['build_time_ms']:.1f} ms")
                    print(f"  Avg query: {res['avg_time_ms']:.2f} ms "
                          f"(p95={res['p95_time_ms']:.2f} ms, {res['qps']:.0f} QPS)")
                    if lib == "nseekfs":
                        print(f"  └─ internal engine avg={res['internal_avg_ms']:.2f} ms "
                              f"(p95={res['internal_p95_ms']:.2f} ms)")
                else:
                    print(f"  FAILED: {res.get('error')}")
            except Exception as e:
                results[lib] = {'success': False, 'error': str(e)}
                print(f"  ERROR: {e}")

        # ranking por avg_time_ms (apenas libs com sucesso)
        ok = {k: v for k, v in results.items() if v.get("success")}
        ranking = sorted(ok.items(), key=lambda x: x[1]["avg_time_ms"])
        print("\nRanking by avg query time:")
        for i, (lib, data) in enumerate(ranking, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"  {medal} {lib.upper()}: {data['avg_time_ms']:.2f} ms")

        return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", type=str, default="small,medium,large")
    parser.add_argument("--include-ann", action="store_true", help="incluir Annoy (ANN) na comparação")
    args = parser.parse_args()

    dataset_configs = {
        "small":  (5_000, 256, 20),
        "medium": (25_000, 384, 10),
        "large":  (100_000, 512, 5),
    }

    bench = FairBenchmark()
    for ds in args.datasets.split(","):
        ds = ds.strip()
        if ds not in dataset_configs:
            print(f"Unknown dataset: {ds}")
            continue
        n_vectors, dims, n_queries = dataset_configs[ds]
        bench.run_dataset(ds, n_vectors, dims, n_queries, top_k=10, include_ann=args.include_ann)


if __name__ == "__main__":
    sys.exit(main())
