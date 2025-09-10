#!/usr/bin/env python3
"""
NSeekFS v1.0 - Stress Test Script
=================================

Runs simple stress tests on NSeekFS:
- Index creation timing
- Query latency (single & batch)
- Concurrent load with threads
- Basic memory and CPU monitoring

Usage:
    python stress_test.py --vectors 100000 --dims 384 --queries 1000 --threads 4
"""

import argparse
import time
import psutil
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_args():
    parser = argparse.ArgumentParser(description="NSeekFS stress test")
    parser.add_argument("--vectors", type=int, default=50000, help="Number of vectors")
    parser.add_argument("--dims", type=int, default=384, help="Vector dimensions")
    parser.add_argument("--queries", type=int, default=1000, help="Number of queries")
    parser.add_argument("--threads", type=int, default=4, help="Concurrent threads")
    parser.add_argument("--topk", type=int, default=10, help="Top-K")
    return parser.parse_args()

def main():
    args = parse_args()

    try:
        import nseekfs
    except ImportError:
        print("❌ NSeekFS not installed. Run: pip install nseekfs")
        return

    print(f"--- NSeekFS Stress Test ---")
    print(f"Vectors: {args.vectors} × {args.dims}, Queries: {args.queries}, Threads: {args.threads}, TopK={args.topk}")
    print()

    # Generate dataset
    vectors = np.random.randn(args.vectors, args.dims).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)

    # Index creation
    mem_before = psutil.Process().memory_info().rss / (1024 * 1024)
    start = time.perf_counter()
    index = nseekfs.from_embeddings(vectors, normalized=True, verbose=False)
    build_time = time.perf_counter() - start
    mem_after = psutil.Process().memory_info().rss / (1024 * 1024)
    print(f"Index created in {build_time:.2f}s, memory +{mem_after - mem_before:.1f} MB")

    # Single query test
    query = np.random.randn(args.dims).astype(np.float32)
    query /= np.linalg.norm(query)

    # External timing (Python)
    start = time.perf_counter()
    _ = index.query(query, top_k=args.topk)
    elapsed_py = (time.perf_counter() - start) * 1000

    # Internal timing (Rust)
    detailed = index.query_detailed(query, top_k=args.topk)
    elapsed_rs = detailed.query_time_ms

    print(f"Single query (Python wall-time): {elapsed_py:.2f} ms")
    print(f"Single query (NSeekFS internal): {elapsed_rs:.2f} ms, top1 idx={detailed.results[0]['idx']}")

    # Batch queries
    queries = np.random.randn(args.queries, args.dims).astype(np.float32)
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)
    start = time.perf_counter()
    index.query_batch(queries, top_k=args.topk)
    elapsed = (time.perf_counter() - start) * 1000 / args.queries
    print(f"Batch queries: {elapsed:.2f} ms/query")

    # Concurrent load
    def worker(nq):
        local_times = []
        for _ in range(nq):
            q = np.random.randn(args.dims).astype(np.float32)
            q /= np.linalg.norm(q)
            s = time.perf_counter()
            index.query(q, top_k=args.topk)
            local_times.append((time.perf_counter() - s) * 1000)
        return local_times

    q_per_thread = args.queries // args.threads
    futures = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for _ in range(args.threads):
            futures.append(executor.submit(worker, q_per_thread))

    all_times = []
    for f in as_completed(futures):
        all_times.extend(f.result())

    avg = np.mean(all_times)
    p95 = np.percentile(all_times, 95)
    print(f"Concurrent load: {len(all_times)} queries, avg={avg:.2f} ms, p95={p95:.2f} ms")

    # CPU & memory usage
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    print(f"System usage after test: CPU={cpu:.1f}%, MEM={mem:.1f}%")

if __name__ == "__main__":
    main()
