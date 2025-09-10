#!/usr/bin/env python3
# try_nseekfs_ai.py
#
# Primeiro contacto com o NSeekFS, como num pipeline de IA:
# - constrói um índice a partir de embeddings
# - normaliza para cosseno
# - mede latências single e batch
# - valida resultados vs NumPy (baseline exato)
# - opção: demonstração simples RAG com sentence-transformers se disponível

import time
from pathlib import Path
import numpy as np
import nseekfs

RNG_SEED = 42
N = 20_000           # número de vetores (ajuste consoante a sua máquina)
D = 384              # dimensão típica de muitos modelos de embeddings
Q = 32               # número de queries para batch
TOP_K = 10

def normalize_rows(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return (x / n).astype(np.float32, copy=False)

def numpy_topk_cosine(vectors_norm: np.ndarray, q_norm: np.ndarray, k: int):
    sims = vectors_norm @ q_norm
    if k >= sims.size:
        order = np.argsort(-sims, kind="stable")
        return order, sims[order]
    idx = np.argpartition(-sims, k-1)[:k]
    part = sims[idx]
    order_local = np.argsort(-part, kind="stable")
    top_idx = idx[order_local]
    top_scores = part[order_local]
    return top_idx, top_scores

def section(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def main():
    rng = np.random.default_rng(RNG_SEED)

    section("1) Preparação de dados (simulados) e normalização para cosseno")
    embeddings = rng.standard_normal((N, D), dtype=np.float32)
    queries = rng.standard_normal((Q, D), dtype=np.float32)

    embeddings = normalize_rows(embeddings)
    queries = normalize_rows(queries)
    print(f"Embeddings: {embeddings.shape} float32 normalizados")
    print(f"Queries   : {queries.shape} float32 normalizados")

    section("2) Construção do índice NSeekFS")
    t0 = time.perf_counter()
    index = nseekfs.from_embeddings(
        embeddings,
        normalized=True,   # já normalizámos; evitar normalização redundante no core
        verbose=False
    )
    build_ms = (time.perf_counter() - t0) * 1000.0
    print(f"Index: {index.rows} vetores × {index.dims} dims")
    print(f"Tempo de build: {build_ms:.2f} ms")

    section("3) Query simples (latência single-query)")
    # aquecimento
    _ = index.query(queries[0], top_k=TOP_K)
    # medições
    single_times = []
    for q in queries:
        t0 = time.perf_counter()
        res = index.query(q, top_k=TOP_K)
        single_times.append((time.perf_counter() - t0) * 1000.0)
    single_ms = np.mean(single_times)
    p95_ms = np.percentile(single_times, 95)
    print(f"Média: {single_ms:.3f} ms/query | p95: {p95_ms:.3f} ms | QPS ~ {1000.0/single_ms:.0f}")

    section("4) Query em batch (throughput)")
    t0 = time.perf_counter()
    batch_res = index.query_batch(queries, top_k=TOP_K, format="simple")
    batch_avg_ms = ((time.perf_counter() - t0) * 1000.0) / len(queries)
    print(f"Média: {batch_avg_ms:.3f} ms/query em batch ({len(batch_res)} queries)")

    section("5) Validação de correção vs NumPy (ground-truth exato)")
    # comparamos top-1 e recall@k em algumas queries
    n_check = min(10, Q)
    top1_ok = 0
    recall_sum = 0.0
    for i in range(n_check):
        q = queries[i]
        gt_idx, gt_sc = numpy_topk_cosine(embeddings, q, TOP_K)
        nseek = index.query(q, top_k=TOP_K)
        ns_idx = np.array([r["idx"] for r in nseek], dtype=np.int64)

        if ns_idx[0] == gt_idx[0]:
            top1_ok += 1
        recall_sum += len(set(ns_idx.tolist()) & set(gt_idx.tolist())) / TOP_K

    print(f"Top-1 match: {top1_ok}/{n_check}  |  Recall@{TOP_K}: {recall_sum/n_check:.3f}")
    assert top1_ok == n_check, "Top-1 não corresponde ao ground-truth em todas as amostras"
    print("Correção validada nas amostras testadas.")

    section("6) Query detalhada com métricas internas")
    detailed = index.query_detailed(queries[0], top_k=TOP_K)
    print(f"Tempo reportado pelo engine: {detailed.query_time_ms:.3f} ms "
          f"(simd={detailed.simd_used}, método={detailed.method_used})")

    section("7) Persistência e reload do índice")
    path = Path(index.index_path)
    print(f"Caminho do índice: {path}")
    reloaded = nseekfs.from_bin(str(path))
    sanity = reloaded.query_simple(queries[0], top_k=1)[0]["idx"]
    print(f"Reload OK. Sanity top-1 idx: {sanity}")

    section("8) Métricas agregadas do motor")
    metrics = index.get_performance_metrics()
    print(f"Métricas: {metrics}")

    section("9) Mini-benchmark embutido (quick sanity)")
    nseekfs.benchmark(vectors=2_000, dims=D, queries=50, verbose=True)

    section("10) Extra (opcional): mini-RAG com sentence-transformers")
    # demonstração simples: se sentence-transformers estiver disponível, indexa textos e faz uma query semântica
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        corpus = [
            "How to fine-tune a transformer for intent classification",
            "Best practices for vector search in production",
            "Setting up retrieval-augmented generation with LangChain",
            "Optimizing cosine similarity with SIMD instructions",
            "Deploying Rust-based services behind a Python API",
            "Batching queries to maximize throughput in inference",
            "Compressing embeddings with quantization techniques",
            "Implementing HNSW for approximate nearest neighbors",
            "Building a recommendation system with implicit feedback",
            "Indexing large document sets for semantic search"
        ]
        corpus_emb = model.encode(corpus, normalize_embeddings=True).astype(np.float32)
        rag_index = nseekfs.from_embeddings(corpus_emb, normalized=True)
        user_query = "how to build a fast semantic search for RAG"
        q_emb = model.encode([user_query], normalize_embeddings=True).astype(np.float32)[0]

        hits = rag_index.query(q_emb, top_k=5)
        print("Consulta:", user_query)
        for rank, hit in enumerate(hits, 1):
            print(f"{rank:2d}. score={hit['score']:.3f}  text={corpus[hit['idx']]}")
    except Exception as e:
        print("sentence-transformers não disponível. Para ver o exemplo RAG, instale:")
        print("  pip install sentence-transformers")

if __name__ == "__main__":
    main()
