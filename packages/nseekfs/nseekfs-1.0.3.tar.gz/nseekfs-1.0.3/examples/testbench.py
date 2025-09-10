#!/usr/bin/env python3
"""
NSeekFS Performance Benchmark
====================================================

Comprehensive benchmark comparing NSeekFS against popular vector search libraries
for exact cosine similarity search.

Libraries tested:
- NSeekFS (Rust-based)
- FAISS (Facebook AI Similarity Search)
- scikit-learn (brute force)
- NumPy (baseline implementation)

Test scenarios:
- Dataset sizes: 25K to 500K vectors
- Dimensions: 384 (common for embeddings)
- Top-K values: 5, 10, 50
- Single query and batch query performance
"""

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import psutil
import os
import sys

# Import libraries with error handling
try:
    import nseekfs
    HAS_NSEEKFS = True
except ImportError:
    HAS_NSEEKFS = False
    print("Warning: NSeekFS not available")

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    print("Warning: FAISS not available")

try:
    from sklearn.neighbors import NearestNeighbors
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Warning: scikit-learn not available")

plt.style.use('default')
if 'seaborn' in plt.style.available:
    plt.style.use('seaborn-v0_8')

def get_memory_usage_mb():
    """Return current memory usage in MB"""
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

def robust_timer(func, *args, repeat=5, warmup=1, **kwargs):
    """Timer with warmup and outlier removal"""
    # Warmup runs
    for _ in range(warmup):
        try:
            func(*args, **kwargs)
        except:
            pass
    
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            times.append(elapsed)
        except Exception as e:
            return None, str(e)
    
    # Remove outliers if we have enough measurements
    if len(times) >= 3:
        mean = np.mean(times)
        std = np.std(times)
        times = [t for t in times if abs(t - mean) <= 2 * std]
    
    return np.mean(times) if times else None, None

def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    """Normalize vectors for cosine similarity"""
    if vectors.ndim == 1:
        norm = np.linalg.norm(vectors)
        return vectors / norm if norm > 0 else vectors
    else:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return vectors / norms

class VectorSearchBenchmark:
    """Benchmark engine for vector search libraries"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.results = []
        
    def log(self, message):
        if self.verbose:
            print(f"[BENCH] {message}")
    
    def benchmark_nseekfs(self, vectors: np.ndarray, queries: np.ndarray, top_k: int) -> Dict:
        """Benchmark NSeekFS performance"""
        if not HAS_NSEEKFS:
            return {'success': False, 'error': 'NSeekFS not available'}
        
        try:
            self.log("Testing NSeekFS...")
            
            # Measure index build time
            build_start = time.perf_counter()
            index = nseekfs.from_embeddings(vectors, normalized=True, verbose=False)
            build_time = (time.perf_counter() - build_start) * 1000
            
            # Single query performance
            single_query = queries[0]
            single_time, error = robust_timer(lambda: index.query(single_query, top_k=top_k))
            if error:
                return {'success': False, 'error': f"Single query failed: {error}"}
            
            # Get detailed info about the query method
            detailed_result = index.query_detailed(single_query, top_k=top_k)
            
            # Batch query performance
            batch_time, error = robust_timer(lambda: index.query_batch(queries, top_k=top_k))
            if error:
                return {'success': False, 'error': f"Batch query failed: {error}"}
            
            return {
                'success': True,
                'library': 'NSeekFS',
                'build_time_ms': build_time,
                'single_query_ms': single_time,
                'batch_total_ms': batch_time,
                'batch_per_query_ms': batch_time / len(queries),
                'method_used': detailed_result.method_used,
                'simd_used': detailed_result.simd_used,
                'memory_mb': get_memory_usage_mb()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def benchmark_faiss(self, vectors: np.ndarray, queries: np.ndarray, top_k: int) -> Dict:
        """Benchmark FAISS performance"""
        if not HAS_FAISS:
            return {'success': False, 'error': 'FAISS not available'}
        
        try:
            self.log("Testing FAISS...")
            
            # Build index
            build_start = time.perf_counter()
            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors.astype(np.float32))
            build_time = (time.perf_counter() - build_start) * 1000
            
            # Single query (FAISS expects 2D arrays)
            single_query = queries[0:1]
            single_time, error = robust_timer(lambda: index.search(single_query, top_k))
            if error:
                return {'success': False, 'error': f"Single query failed: {error}"}
            
            # Batch query
            batch_time, error = robust_timer(lambda: index.search(queries, top_k))
            if error:
                return {'success': False, 'error': f"Batch query failed: {error}"}
            
            return {
                'success': True,
                'library': 'FAISS',
                'build_time_ms': build_time,
                'single_query_ms': single_time,
                'batch_total_ms': batch_time,
                'batch_per_query_ms': batch_time / len(queries),
                'memory_mb': get_memory_usage_mb()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def benchmark_sklearn(self, vectors: np.ndarray, queries: np.ndarray, top_k: int) -> Dict:
        """Benchmark scikit-learn performance"""
        if not HAS_SKLEARN:
            return {'success': False, 'error': 'scikit-learn not available'}
        
        try:
            self.log("Testing scikit-learn...")
            
            # Build index
            build_start = time.perf_counter()
            nn = NearestNeighbors(n_neighbors=top_k, algorithm="brute", metric="cosine")
            nn.fit(vectors)
            build_time = (time.perf_counter() - build_start) * 1000
            
            # Single query (sklearn expects 2D arrays)
            single_query = queries[0:1]
            single_time, error = robust_timer(lambda: nn.kneighbors(single_query))
            if error:
                return {'success': False, 'error': f"Single query failed: {error}"}
            
            # Batch query
            batch_time, error = robust_timer(lambda: nn.kneighbors(queries))
            if error:
                return {'success': False, 'error': f"Batch query failed: {error}"}
            
            return {
                'success': True,
                'library': 'scikit-learn',
                'build_time_ms': build_time,
                'single_query_ms': single_time,
                'batch_total_ms': batch_time,
                'batch_per_query_ms': batch_time / len(queries),
                'memory_mb': get_memory_usage_mb()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def benchmark_numpy(self, vectors: np.ndarray, queries: np.ndarray, top_k: int) -> Dict:
        """Benchmark NumPy baseline implementation"""
        try:
            self.log("Testing NumPy baseline...")
            
            # No build time for NumPy (just stores the vectors)
            build_time = 0
            
            def numpy_single_search(query):
                similarities = vectors @ query
                if top_k >= len(similarities):
                    top_indices = np.argsort(-similarities)
                else:
                    top_indices = np.argpartition(-similarities, top_k)[:top_k]
                    top_indices = top_indices[np.argsort(-similarities[top_indices])]
                return top_indices
            
            def numpy_batch_search(queries):
                results = []
                for query in queries:
                    similarities = vectors @ query
                    if top_k >= len(similarities):
                        top_indices = np.argsort(-similarities)
                    else:
                        top_indices = np.argpartition(-similarities, top_k)[:top_k]
                        top_indices = top_indices[np.argsort(-similarities[top_indices])]
                    results.append(top_indices)
                return results
            
            # Single query performance
            single_time, error = robust_timer(lambda: numpy_single_search(queries[0]))
            if error:
                return {'success': False, 'error': f"Single query failed: {error}"}
            
            # Batch query performance
            batch_time, error = robust_timer(lambda: numpy_batch_search(queries))
            if error:
                return {'success': False, 'error': f"Batch query failed: {error}"}
            
            return {
                'success': True,
                'library': 'NumPy',
                'build_time_ms': build_time,
                'single_query_ms': single_time,
                'batch_total_ms': batch_time,
                'batch_per_query_ms': batch_time / len(queries),
                'memory_mb': get_memory_usage_mb()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_benchmark_scenario(self, n_vectors: int, dimensions: int, n_queries: int, top_k: int) -> Dict:
        """Execute a complete benchmark scenario"""
        
        print(f"\nBenchmark: {n_vectors:,} vectors x {dimensions}D, {n_queries} queries, top_k={top_k}")
        print("-" * 80)
        
        self.log("Generating test data...")
        np.random.seed(42)  # For reproducible results
        vectors = normalize_vectors(np.random.randn(n_vectors, dimensions).astype(np.float32))
        queries = normalize_vectors(np.random.randn(n_queries, dimensions).astype(np.float32))
        
        # List of available benchmarks
        benchmarks = []
        if HAS_NSEEKFS:
            benchmarks.append(('NSeekFS', self.benchmark_nseekfs))
        if HAS_FAISS:
            benchmarks.append(('FAISS', self.benchmark_faiss))
        if HAS_SKLEARN:
            benchmarks.append(('scikit-learn', self.benchmark_sklearn))
        benchmarks.append(('NumPy', self.benchmark_numpy))
        
        scenario_results = {
            'n_vectors': n_vectors,
            'dimensions': dimensions,
            'n_queries': n_queries,
            'top_k': top_k,
            'libraries': {}
        }
        
        # Run benchmarks
        for lib_name, benchmark_func in benchmarks:
            result = benchmark_func(vectors, queries, top_k)
            scenario_results['libraries'][lib_name] = result
            
            if result['success']:
                single_ms = result['single_query_ms']
                batch_ms = result['batch_per_query_ms']
                build_ms = result['build_time_ms']
                memory_mb = result['memory_mb']
                
                print(f"  {lib_name:12s}: Single={single_ms:6.2f}ms | "
                      f"Batch={batch_ms:6.2f}ms/q | "
                      f"Build={build_ms:6.0f}ms | "
                      f"Memory={memory_mb:5.0f}MB")
                
                # Show additional NSeekFS details
                if lib_name == 'NSeekFS' and 'method_used' in result:
                    method = result['method_used']
                    simd = result['simd_used']
                    print(f"    Algorithm: {method}, SIMD: {simd}")
            else:
                print(f"  {lib_name:12s}: FAILED - {result['error']}")
        
        self.results.append(scenario_results)
        return scenario_results
    
    def generate_results_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame"""
        data = []
        
        for scenario in self.results:
            for lib_name, result in scenario['libraries'].items():
                if result['success']:
                    row = {
                        'Dataset': f"{scenario['n_vectors']/1000:.0f}K x {scenario['dimensions']}D",
                        'Library': lib_name,
                        'Top_K': scenario['top_k'],
                        'Single_Query_ms': result['single_query_ms'],
                        'Batch_Per_Query_ms': result['batch_per_query_ms'],
                        'Build_Time_ms': result['build_time_ms'],
                        'Memory_MB': result['memory_mb'],
                        'N_Vectors': scenario['n_vectors'],
                        'Dimensions': scenario['dimensions']
                    }
                    
                    # Add NSeekFS-specific columns
                    if lib_name == 'NSeekFS':
                        row['Algorithm'] = result.get('method_used', 'N/A')
                        row['SIMD'] = result.get('simd_used', False)
                    else:
                        row['Algorithm'] = 'N/A'
                        row['SIMD'] = False
                    
                    data.append(row)
        
        return pd.DataFrame(data)
    
    def create_performance_chart(self, save_path: str = "nseekfs_benchmark_chart.png"):
        """Generate performance comparison charts"""
        
        df = self.generate_results_dataframe()
        if df.empty:
            print("No results available for charting")
            return None
        
        # Filter for specific top_k values for cleaner visualization
        chart_df = df[df['Top_K'].isin([10])].copy()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Vector Search Library Performance Comparison\n(Exact Cosine Similarity)', 
                     fontsize=14, fontweight='bold')
        
        # Single query performance
        sns.barplot(data=chart_df, x='Dataset', y='Single_Query_ms', 
                   hue='Library', ax=ax1)
        ax1.set_title('Single Query Latency (Top-K=10)')
        ax1.set_ylabel('Time (ms)')
        ax1.set_yscale('log')
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Batch query performance
        sns.barplot(data=chart_df, x='Dataset', y='Batch_Per_Query_ms', 
                   hue='Library', ax=ax2)
        ax2.set_title('Batch Query Performance (Top-K=10)')
        ax2.set_ylabel('Time per Query (ms)')
        ax2.set_yscale('log')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Speedup vs NumPy
        speedup_data = []
        for dataset in chart_df['Dataset'].unique():
            dataset_data = chart_df[chart_df['Dataset'] == dataset]
            numpy_time = dataset_data[dataset_data['Library'] == 'NumPy']['Single_Query_ms']
            
            if not numpy_time.empty:
                numpy_baseline = numpy_time.iloc[0]
                
                for lib in dataset_data['Library'].unique():
                    if lib != 'NumPy':
                        lib_data = dataset_data[dataset_data['Library'] == lib]
                        if not lib_data.empty:
                            lib_time = lib_data['Single_Query_ms'].iloc[0]
                            speedup = numpy_baseline / lib_time
                            speedup_data.append({
                                'Dataset': dataset,
                                'Library': lib,
                                'Speedup': speedup
                            })
        
        if speedup_data:
            speedup_df = pd.DataFrame(speedup_data)
            sns.barplot(data=speedup_df, x='Dataset', y='Speedup', hue='Library', ax=ax3)
            ax3.set_title('Speedup vs NumPy Baseline')
            ax3.set_ylabel('Speedup Factor')
            ax3.tick_params(axis='x', rotation=45)
            ax3.axhline(y=1, color='red', linestyle='--', alpha=0.7)
            ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Memory usage
        memory_df = chart_df.groupby(['Dataset', 'Library'])['Memory_MB'].mean().reset_index()
        sns.barplot(data=memory_df, x='Dataset', y='Memory_MB', hue='Library', ax=ax4)
        ax4.set_title('Memory Usage')
        ax4.set_ylabel('Memory (MB)')
        ax4.tick_params(axis='x', rotation=45)
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved as: {save_path}")
        
        return fig
    
    def print_summary_report(self):
        """Print comprehensive benchmark summary"""
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY REPORT")
        print("="*80)
        
        df = self.generate_results_dataframe()
        if df.empty:
            print("No successful benchmark results to summarize")
            return
        
        # Performance champions by category
        categories = [
            ('Single_Query_ms', 'Single Query Performance'),
            ('Batch_Per_Query_ms', 'Batch Query Performance'),
            ('Build_Time_ms', 'Index Build Speed')
        ]
        
        for metric, title in categories:
            print(f"\n{title} Leaders:")
            for dataset in sorted(df['Dataset'].unique()):
                dataset_df = df[(df['Dataset'] == dataset) & (df['Top_K'] == 10)]
                if not dataset_df.empty:
                    best = dataset_df.loc[dataset_df[metric].idxmin()]
                    print(f"  {dataset}: {best['Library']} ({best[metric]:.2f}ms)")
        
        # NSeekFS specific analysis
        nseekfs_df = df[df['Library'] == 'NSeekFS']
        if not nseekfs_df.empty:
            print(f"\nNSeekFS Analysis:")
            print(f"  Algorithm diversity: {nseekfs_df['Algorithm'].nunique()} different optimization methods")
            print(f"  SIMD utilization: {nseekfs_df['SIMD'].sum()}/{len(nseekfs_df)} test cases")
            print(f"  Average single query: {nseekfs_df['Single_Query_ms'].mean():.2f}ms")
            print(f"  Average batch per query: {nseekfs_df['Batch_Per_Query_ms'].mean():.2f}ms")
            
            # Calculate average speedup vs NumPy
            numpy_df = df[df['Library'] == 'NumPy']
            speedups = []
            for _, nseek_row in nseekfs_df.iterrows():
                numpy_match = numpy_df[
                    (numpy_df['Dataset'] == nseek_row['Dataset']) & 
                    (numpy_df['Top_K'] == nseek_row['Top_K'])
                ]
                if not numpy_match.empty:
                    speedup = numpy_match['Single_Query_ms'].iloc[0] / nseek_row['Single_Query_ms']
                    speedups.append(speedup)
            
            if speedups:
                print(f"  Average speedup vs NumPy: {np.mean(speedups):.1f}x")

def main():
    """Execute the complete benchmark suite"""
    
    print("NSeekFS Vector Search Performance Benchmark")
    print("=" * 50)
    print("Comparing exact cosine similarity search performance")
    print("Libraries: NSeekFS, FAISS, scikit-learn, NumPy")
    print()
    
    # Test configuration
    vector_sizes = [25_000, 50_000, 100_000, 200_000, 500_000]
    dimensions = 384  # Common embedding dimension (e.g., sentence-transformers)
    n_queries = 50    # Sufficient for stable timing measurements
    top_k_values = [5, 10, 50]  # Common top-k values in practice
    
    benchmark = VectorSearchBenchmark(verbose=True)
    
    # Run all benchmark scenarios
    for n_vectors in vector_sizes:
        for top_k in top_k_values:
            try:
                benchmark.run_benchmark_scenario(n_vectors, dimensions, n_queries, top_k)
            except KeyboardInterrupt:
                print("\nBenchmark interrupted by user")
                break
            except Exception as e:
                print(f"Error in scenario {n_vectors}K vectors, top_k={top_k}: {e}")
                continue
    
    print("\n" + "="*80)
    print("GENERATING OUTPUTS")
    print("="*80)
    
    # Save detailed results
    df = benchmark.generate_results_dataframe()
    if not df.empty:
        csv_path = "nseekfs_benchmark_results.csv"
        df.to_csv(csv_path, index=False)
        print(f"Detailed results saved to: {csv_path}")
    
    # Generate visualization
    try:
        benchmark.create_performance_chart("nseekfs_performance_comparison.png")
    except Exception as e:
        print(f"Chart generation failed: {e}")
    
    # Print summary
    benchmark.print_summary_report()
    
    print(f"\nBenchmark complete. Check generated files for detailed analysis.")

if __name__ == "__main__":
    main()