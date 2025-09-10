from __future__ import annotations
import polars as pl
from great_tables import GT
from typing import Union
import numpy as np
import time

# Optional scipy imports - lazy loaded to avoid import warnings
SCIPY_AVAILABLE = None  # Will be checked when needed
stats = None


def _check_scipy_availability():
    """Check if SciPy is available and import it if needed."""
    global SCIPY_AVAILABLE, stats
    
    if SCIPY_AVAILABLE is None:
        try:
            from scipy import stats as scipy_stats
            stats = scipy_stats
            SCIPY_AVAILABLE = True
        except (ImportError, ValueError):
            # Handle both import errors and binary incompatibility
            SCIPY_AVAILABLE = False
            stats = None
    
    return SCIPY_AVAILABLE


def _format_memory_usage(df: pl.DataFrame) -> str:
    """Format memory usage with appropriate units using Polars unit parameter."""
    try:
        if df.estimated_size(unit='mb') >= 1000:  # >= 1 GB
            return f"{df.estimated_size(unit='gb'):.1f} GB"
        elif df.estimated_size(unit='mb') >= 1.0:  # >= 1 MB
            return f"{df.estimated_size(unit='mb'):.1f} MB"
        else:  # < 1 MB, use KB
            return f"{df.estimated_size(unit='kb'):.1f} KB"
    except Exception:
        # Fallback for older Polars versions
        try:
            memory_bytes = df.estimated_size()
            memory_mb = memory_bytes / 1024 / 1024
            if memory_mb < 1.0:
                memory_kb = memory_mb * 1024
                return f"{memory_kb:.1f} KB"
            else:
                return f"{memory_mb:.1f} MB"
        except Exception:
            return "Unknown"


def _get_columns_to_analyze(df: pl.DataFrame, include: str | list[str] | None) -> list[str]:
    """
    Filter columns based on include parameter.
    
    Parameters
    ----------
    df : pl.DataFrame
        The DataFrame to analyze
    include : str, list[str], or None
        Which data types to include
        
    Returns
    -------
    list[str]
        List of column names to analyze
    """
    if include is None or include == 'numeric':
        # Default behavior: only numeric columns)
        return [c for c, dt in zip(df.columns, df.dtypes) if dt.is_numeric()]
    
    elif include == 'all':
        # Include all columns
        return df.columns
    
    elif include == 'string':
        # Only string/text columns
        return [c for c, dt in zip(df.columns, df.dtypes) if dt in (pl.String, pl.Utf8)]
    
    elif include == 'temporal':
        # Only date/datetime columns
        return [c for c, dt in zip(df.columns, df.dtypes) if dt.is_temporal()]
    
    elif isinstance(include, list):
        # Specific data type names
        include_types = set(include)
        return [c for c, dt in zip(df.columns, df.dtypes) if str(dt) in include_types]
    
    else:
        raise ValueError(f"Invalid include parameter: {include}. "
                        f"Must be None, 'all', 'numeric', 'string', 'temporal', or list of dtype names.")


def xray(
    df: pl.DataFrame,
    *,
    include: str | list[str] | None = None,
    great_tables: bool = True,
    basic_statistics: bool = True,
    counts_ratios: bool = True,
    distribution: bool = True,
    statistical_tests: bool = False,
    quality_assessment: bool = False,
    samples: bool | int = False,
    correlation: bool = False,
    title: str | None = None,
    percentiles: list[float] | None = None,
    outlier_method: str = "iqr",
    outlier_bounds: list[float] | None = None,
    corr_target: str | None = None,
    normality_test: str = "shapiro",
    uniformity_test: str = "ks",
    missing_threshold: float = 0.3,
    constant_threshold: float = 0.99,
    skew_threshold: float = 2.0,
    kurtosis_threshold: float = 7.0,
    outlier_threshold: float = 0.05,
    quality_test: bool = False,
    decimals: int = 2,
    sep_mark: str = ",",
    dec_mark: str = ".",
    compact: bool = False
) -> Union[GT, pl.DataFrame]:
    """
    X-ray your data: comprehensive statistical analysis with quality assessment.
    
    This function provides deep insight into DataFrame structure and quality,
    revealing hidden issues, statistical properties, and data health indicators.
    Perfect for exploratory data analysis and data quality assessment.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame to summarize.
    include : str, list[str], or None, default None
        Which data types to include in the analysis.
        - None (default): Only numeric columns (Int8, Int16, Int32, Int64, Float32, Float64)
        - 'all': All columns regardless of data type
        - 'numeric': Only numeric columns (same as None)
        - 'string': Only string/text columns
        - 'temporal': Only date/datetime columns
        - list of strings: Specific data type names (e.g., ['Float64', 'String'])
    great_tables : bool, default True
        Whether to return a formatted Great Tables object (True) or standard
        Polars DataFrame output (False). Histograms are included by default for Great Tables.
    basic_statistics : bool, default True
        Include basic statistical metrics (DEFAULT section): dtype, dtype_optimal, count, mean, std, 
        min, percentiles, max, iqr. Set to False to exclude.
    counts_ratios : bool, default True
        Include count and ratio metrics (DEFAULT section): null_count, null_pct, zero_count, zero_pct,
        unique_count, unique_pct, outlier_count, outlier_pct, duplicates_count,
        duplicates_pct, positive_pct, negative_pct. Set to False to exclude.
    distribution : bool, default True
        Include distribution metrics (DEFAULT section): histogram (Great Tables only), variance, skew, kurtosis, mad. Set to False to exclude.
    statistical_tests : bool, default False
        Include statistical test results (OPT-IN section): normality_test, uniformity_test.
    quality_assessment : bool, default False
        Include quality assessment metrics (OPT-IN section): usability_flags, usability_score,
        recommendation, quality_score, quality_assessment.
    samples : bool | int, default False
        Include sample metrics (OPT-IN section): samples.
        - False: No samples column
        - True: Show 3 sample values per column
        - int: Show specified number of sample values per column (max 10, e.g., samples=5)
    correlation : bool, default False
        Include correlation analysis with target column (OPT-IN section).
    title : str | None, optional
        Custom title for the Great Tables output. If None, uses default titles.
        Only applies when great_tables=True.
    percentiles : list[float] | None, optional
        Custom percentiles to calculate. Default: [0.25, 0.5, 0.75].
        Percentiles are automatically sorted in ascending order.
    outlier_method : str, default "iqr"
        Method for outlier detection:
        - "iqr": Interquartile range method (Q1 - 1.5*IQR, Q3 + 1.5*IQR)
        - "percentile": Use custom percentile bounds from outlier_bounds
        - "zscore": Z-score method (mean ± 3*std)
    outlier_bounds : list[float] | None, optional
        Custom percentile bounds for outlier detection when method="percentile".
        Example: [0.05, 0.95] for 5th and 95th percentiles.
        Only used when outlier_method="percentile".
    corr_target : str | None, optional
        Target column for correlation analysis. Must be a numeric column.
        Shows correlation between each numeric column and the target.
        Only used when correlation=True.
    normality_test : str, default "shapiro"
        Statistical test for normality (requires scipy):
        - "shapiro": Shapiro-Wilk test (good for small/medium samples)
        - "anderson": Anderson-Darling test (sensitive to tail behavior)
        - "ks": Kolmogorov-Smirnov test vs normal distribution
        Only used when statistical_tests=True.
    uniformity_test : str, default "ks"
        Statistical test for uniformity (requires scipy):
        - "ks": Kolmogorov-Smirnov test vs uniform distribution
        - "chi2": Chi-square goodness of fit test
        Only used when statistical_tests=True.
    missing_threshold : float, default 0.3
        Threshold for flagging high missingness (0.3 = 30%).
        Used in quality assessment calculations.
    constant_threshold : float, default 0.99
        Threshold for flagging quasi-constant columns (0.99 = 99% same value).
        Used in quality assessment calculations.
    skew_threshold : float, default 2.0
        Threshold for flagging extreme skewness (|skew| > threshold).
        Used in quality assessment calculations.
    kurtosis_threshold : float, default 7.0
        Threshold for flagging high kurtosis (fat tails).
        Used in quality assessment calculations.
    outlier_threshold : float, default 0.05
        Threshold for flagging outlier-heavy columns (0.05 = 5%).
        Used in quality assessment calculations.
    quality_test : bool, default False
        Include sophisticated quality assessment with weighted flags and recommendations.
        Adds columns: usability_flags, usability_score, recommendation.
    decimals : int, default 2
        Number of decimal places for numeric formatting in Great Tables output.
        Only applies when great_tables=True.
    sep_mark : str, default ","
        Thousands separator mark for numeric formatting (e.g., "1,000").
        Only applies when great_tables=True.
    dec_mark : str, default "."
        Decimal mark for numeric formatting (e.g., "1.23").
        Only applies when great_tables=True.
    compact : bool, default False
        If True, large numbers are auto-scaled with suffixes (e.g., "10K", "1.5M").
        Only applies when great_tables=True.

    Returns
    -------
    Union[GT, pl.DataFrame]
        Either a Great Tables object (if great_tables=True) or a Polars DataFrame
        (if great_tables=False) containing the comprehensive summary statistics.

    Examples
    --------
    Basic data X-ray (numeric columns only):
    
    >>> import polars as pl
    >>> import polarscope as ps
    >>> df = pl.DataFrame({
    ...     'price': [100, 200, 150, 300, 250],
    ...     'volume': [1000, 1500, 1200, 2000, 1800],
    ...     'category': ['A', 'B', 'A', 'C', 'B'],
    ...     'rating': [4.5, 3.8, 4.2, 4.9, 4.1]
    ... })
    >>> table = ps.xray(df)  # Only shows price, volume, rating (numeric columns)
    >>> table.show()
    
    Include all columns with specific sections:
    
    >>> full_xray = ps.xray(
    ...     df, 
    ...     include='all',
    ...     statistical_tests=True,
    ...     quality_assessment=True
    ... )
    
    Custom quality thresholds:
    
    >>> quality_xray = ps.xray(
    ...     df,
    ...     include='all',
    ...     missing_threshold=0.2,  # Flag >20% missing
    ...     skew_threshold=1.5,     # Flag |skew| > 1.5
    ...     quality_test=True       # Include quality assessment
    ... )
    
    Disable default sections:
    
    >>> minimal_xray = ps.xray(
    ...     df,
    ...     basic_statistics=False,  # Exclude basic stats
    ...     counts_ratios=False,     # Exclude counts & ratios
    ...     distribution=False       # Exclude distribution metrics
    ... )

    Notes
    -----
    When quality_test=True, sophisticated quality assessment is performed:
    - Weighted flag system (HM, MM, ID, BN, CV, EO, ES, EK, NN, ZH, UC)
    - 0-100 usability score with actionable recommendations
    - Based on polarsight's proven model usability framework
    
    Statistical tests require scipy. If not available, tests are skipped
    with informative messages.
    """
    # Start timing for performance measurement
    start_time = time.perf_counter()
    
    # Memory usage will be calculated in _format_memory_usage() using unit parameter
    
    # Set default percentiles and ensure they are sorted in ascending order
    if percentiles is None:
        percentiles = [0.25, 0.5, 0.75]
    else:
        percentiles = sorted(percentiles)  # Ensure ascending order
    
    # Validate parameters
    if outlier_method not in ["iqr", "percentile", "zscore"]:
        raise ValueError("outlier_method must be 'iqr', 'percentile', or 'zscore'")
    
    if outlier_method == "percentile" and not outlier_bounds:
        raise ValueError("outlier_bounds must be provided when outlier_method='percentile'")
    
    if outlier_bounds and len(outlier_bounds) != 2:
        raise ValueError("outlier_bounds must be a list of exactly 2 values")
    
    if normality_test not in ["shapiro", "anderson", "ks"]:
        raise ValueError("normality_test must be 'shapiro', 'anderson', or 'ks'")
    
    if uniformity_test not in ["ks", "chi2"]:
        raise ValueError("uniformity_test must be 'ks' or 'chi2'")
    
    # Validate correlation target
    if corr_target:
        if corr_target not in df.columns:
            raise ValueError(f"Target column '{corr_target}' not found in DataFrame")
        target_dtype = df.select(pl.col(corr_target)).dtypes[0]
        if not target_dtype.is_numeric():
            raise ValueError(f"Target column '{corr_target}' must be numeric, got {target_dtype}")
    
    # Filter columns based on include parameter)
    all_cols = _get_columns_to_analyze(df, include)
    
    # Calculate comprehensive statistics for all columns
    stats_data = []
    
    for col in all_cols:
        dtype = df.select(pl.col(col)).dtypes[0]
        is_numeric = dtype.is_numeric()
        series = df[col]
        series_clean = series.drop_nulls()
        n_total = len(series)
        n_valid = len(series_clean)
        n_missing = series.null_count()
        pct_missing = (n_missing / n_total * 100) if n_total > 0 else 0
        
        # Initialize column stats
        col_stats = {
            'Column': col,
            'dtype': str(dtype),
            'count': n_valid,
            'null_count': n_missing,
            'null_pct': round(pct_missing, 2)
        }
        
        # Basic counts and ratios - use approx for large datasets
        is_large_dataset = n_total > 300000
        try:
            # Use approximate count for large datasets (>300k rows) for better performance
            if is_large_dataset:
                n_unique = df.select(pl.col(col).approx_n_unique()).item()
            else:
                n_unique = df.select(pl.col(col).n_unique()).item()
        except Exception:
            # Fallback - count via groupby (more reliable for problematic dtypes)
            n_unique = df.select(pl.col(col).drop_nulls().value_counts().height).item()
        
        # Use appropriate column name based on dataset size
        n_unique_col = 'unique_count(approx)' if is_large_dataset else 'unique_count'
        col_stats[n_unique_col] = n_unique
        col_stats['unique_pct'] = round(n_unique / n_total, 4) if n_total > 0 else 0
        
        # Duplicate analysis for historized datasets
        n_duplicates = n_total - n_unique
        pct_duplicates = round((n_duplicates / n_total * 100), 2) if n_total > 0 else 0
        col_stats['duplicates_count'] = n_duplicates
        col_stats['duplicates_pct'] = pct_duplicates
        
        if is_numeric and n_valid > 0:
            # Numeric-specific statistics - use vectorized operations
            series_clean = df.select(pl.col(col).drop_nulls()).to_series()
            
            # Basic descriptive stats
            quantile_stats = _calculate_quantiles(series_clean, percentiles)
            col_stats.update(quantile_stats)
            
            mean_val = float(series_clean.mean())
            std_val = float(series_clean.std()) if n_valid > 1 else None
            try:
                min_val = float(series_clean.min())
                max_val = float(series_clean.max())
            except (ValueError, TypeError):
                # Handle cases where min/max operations fail with mixed types
                min_val = max_val = 0.0
            
            col_stats['mean'] = round(mean_val, 3)
            col_stats['std'] = round(std_val, 3) if std_val is not None else None
            col_stats['min'] = round(min_val, 3)
            col_stats['max'] = round(max_val, 3)
            
            # IQR
            if 0.25 in percentiles and 0.75 in percentiles:
                q25 = quantile_stats.get('25%')
                q75 = quantile_stats.get('75%') 
                if q25 is not None and q75 is not None:
                    col_stats['iqr'] = round(q75 - q25, 3)
            
            # Zero/positive/negative counts
            n_zero = int((series_clean == 0).sum())
            n_pos = int((series_clean > 0).sum())
            n_neg = int((series_clean < 0).sum())
            
            col_stats['zero_count'] = n_zero
            col_stats['zero_pct'] = round(n_zero / n_valid * 100, 2) if n_valid > 0 else 0
            col_stats['positive_pct'] = round(n_pos / n_valid * 100, 2) if n_valid > 0 else 0
            col_stats['negative_pct'] = round(n_neg / n_valid * 100, 2) if n_valid > 0 else 0
            
            # Skewness (always calculated for default view)
            if n_valid > 2:
                skew_val = float(series_clean.skew())
                col_stats['skew'] = round(skew_val, 3)
            else:
                col_stats['skew'] = None
            
            # Distribution plot data for nanoplots
            if n_valid > 0:
                try:
                    # Always use histogram for distribution plots
                    # Calculate optimal number of bins (max 12 for nanoplots)
                    n_bins = min(12, max(5, int(np.sqrt(n_valid))))
                    
                    # Get data range
                    min_val = float(series_clean.min())
                    max_val = float(series_clean.max())
                    
                    # Create bin edges
                    if min_val == max_val:
                        # All values are the same
                        distribution_data = [n_valid]
                    else:
                        bin_edges = np.linspace(min_val, max_val, n_bins + 1)
                        # Calculate histogram using numpy
                        counts, _ = np.histogram(series_clean.to_numpy(), bins=bin_edges)
                        distribution_data = counts.tolist()
                    
                    
                    col_stats['histogram'] = distribution_data
                except Exception:
                    # Fallback if distribution calculation fails
                    col_stats['histogram'] = []
            else:
                col_stats['histogram'] = []
            
            # Advanced statistics (based on section arguments)
            if distribution:
                # Variance
                if n_valid > 1:
                    var_val = float(series_clean.var())
                    # Use scientific notation for very large variance values
                    if abs(var_val) >= 1e6:
                        col_stats['variance'] = f"{var_val:.3e}"
                    else:
                        col_stats['variance'] = round(var_val, 3)
                
                # MAD (Median Absolute Deviation)
                if n_valid > 0:
                    median_val = float(series_clean.median())
                    mad = (series_clean - median_val).abs().median()
                    col_stats['mad'] = round(float(mad), 3)
                
                # Kurtosis (expanded mode only)
                if n_valid > 2:
                    # Calculate kurtosis (excess kurtosis)
                    kurt_val = _calculate_kurtosis(series_clean.to_numpy())
                    col_stats['kurtosis'] = round(kurt_val, 3)
                
            
            # Optimal dtype suggestion (always calculate)
            col_stats['dtype_optimal'] = _suggest_optimal_dtype(series_clean, dtype)
            
            # Statistical tests (if scipy available and requested)
            if statistical_tests and _check_scipy_availability() and n_valid > 3:
                normality_result = _test_normality(series_clean.to_numpy(), normality_test)
                col_stats['normality_test'] = normality_result
                
                uniformity_result = _test_uniformity(series_clean.to_numpy(), uniformity_test)
                col_stats['uniformity_test'] = uniformity_result
            
            # Outlier detection
            n_outliers = _count_outliers(series_clean, outlier_method, outlier_bounds)
            pct_outliers = (n_outliers / n_valid * 100) if n_valid > 0 else 0
            col_stats['outlier_count'] = n_outliers
            col_stats['outlier_pct'] = round(pct_outliers, 2)
            
            # Correlation with target - optimized
            if corr_target:
                if col == corr_target:
                    col_stats['correlation'] = '-'  # Target column shows '-' instead of None
                    col_stats['correlation_plot'] = None  # No plot for target column
                else:
                    try:
                        corr_val = df.select(pl.corr(corr_target, col)).item()
                        col_stats['correlation'] = round(corr_val, 3) if corr_val is not None else None
                        # Create single value for horizontal bar nanoplot (fixed -1 to 1 scale)
                        # Round to 3 decimal places for better performance and readability
                        col_stats['correlation_plot'] = round(corr_val, 3) if corr_val is not None else 0.0
                    except Exception:
                        col_stats['correlation'] = None
                        col_stats['correlation_plot'] = None
        
        else:
            # Non-numeric columns - set numeric stats to None/0
            for stat in ['mean', 'std', 'min', 'max', 'iqr', 'zero_count', 'zero_pct', 
                        'positive_pct', 'negative_pct', 'outlier_count', 'outlier_pct']:
                col_stats[stat] = None if stat in ['mean', 'std', 'iqr'] else 0
            
            # Non-numeric columns don't have distribution plots
            col_stats['histogram'] = []
            
            # For quantiles, set based on percentiles
            for p in percentiles:
                label = _percentile_to_label(p)
                col_stats[label] = None
            
            # Set distribution stats to None for non-numeric columns
            col_stats['variance'] = None
            col_stats['mad'] = None
            col_stats['skew'] = None
            col_stats['kurtosis'] = None
            col_stats['dtype_optimal'] = _suggest_optimal_dtype(series_clean, dtype)
            col_stats['normality_test'] = "N/A (non-numeric)"
            col_stats['uniformity_test'] = "N/A (non-numeric)"
            
            # Correlation with target for non-numeric columns
            if corr_target:
                if col == corr_target:
                    col_stats['correlation'] = '-'  # Target column shows '-' instead of None
                    col_stats['correlation_plot'] = None  # No plot for target column
                else:
                    col_stats['correlation'] = None  # Non-numeric columns can't correlate
                    col_stats['correlation_plot'] = None  # No plot for non-numeric columns
        
        # Samples section - get random sample values
        if samples:
            try:
                # Determine number of samples to show (max 10 to prevent table layout issues)
                n_samples = 3 if samples is True else min(int(samples), 10)
                # Get random sample values from the column
                sample_values = df.select(pl.col(col).drop_nulls().sample(n_samples, seed=42)).to_series().to_list()
                # Format as string with comma separation, limit to reasonable length
                if sample_values:
                    formatted_samples = []
                    for val in sample_values:
                        if isinstance(val, str) and len(val) > 20:
                            formatted_samples.append(f"{val[:17]}...")
                        else:
                            formatted_samples.append(str(val))
                    col_stats['samples'] = ", ".join(formatted_samples)
                else:
                    col_stats['samples'] = "No valid data"
            except Exception:
                col_stats['samples'] = "Error sampling"
        
        # Quality assessment (merged shakiness and model usability)
        if quality_test or quality_assessment:
            # Calculate quality score using the more sophisticated model usability approach
            usability_result = _evaluate_column_usability(
                col_stats,
                has_correlation=bool(corr_target)
            )
            col_stats['usability_flags'] = usability_result['flag_string']
            col_stats['usability_score'] = usability_result['score']
            col_stats['recommendation'] = usability_result['recommendation']
            
            # Also include the simpler quality score for backward compatibility
            shakiness_score = _calculate_shakiness_score(
                col_stats, missing_threshold, constant_threshold, 
                skew_threshold, kurtosis_threshold, outlier_threshold
            )
            col_stats['quality_score'] = shakiness_score
            col_stats['quality_assessment'] = "⚠ SHAKY" if shakiness_score >= 2 else "✓ OK"
        
        stats_data.append(col_stats)
    
    # Create DataFrame
    summary_df = pl.DataFrame(stats_data)
    
    # Apply column filtering based on section arguments
    selected_cols = ['Column']  # Always include column name
    
    # Always include dtype_optimal as the second column
    if 'dtype_optimal' in summary_df.columns:
        selected_cols.append('dtype_optimal')
    
    # Basic Statistics section (DEFAULT - always included unless explicitly disabled)
    if basic_statistics:
        basic_cols = ['dtype', 'count', 'mean', 'std', 'min']
        # Add percentiles in order
        for p in percentiles:
            label = _percentile_to_label(p)
            if label in summary_df.columns:
                basic_cols.append(label)
        # Add max and iqr
        basic_cols.extend(['max', 'iqr'])
        selected_cols.extend([c for c in basic_cols if c in summary_df.columns])
    
    # Counts & Ratios section (DEFAULT - always included unless explicitly disabled)
    if counts_ratios:
        count_cols = ['null_count', 'null_pct', 'zero_count', 'zero_pct', 'unique_count', 'unique_count(approx)', 'unique_pct', 
                     'outlier_count', 'outlier_pct', 'duplicates_count', 'duplicates_pct', 'positive_pct', 'negative_pct']
        selected_cols.extend([c for c in count_cols if c in summary_df.columns])
    
    # Distribution section (DEFAULT - always included unless explicitly disabled)
    if distribution:
        dist_cols = ['variance', 'skew', 'kurtosis', 'mad']
        # Add histogram for Great Tables (first column in Distribution section)
        if great_tables and 'histogram' in summary_df.columns:
            dist_cols.insert(0, 'histogram')
        selected_cols.extend([c for c in dist_cols if c in summary_df.columns])
    
    # Statistical Tests section (OPT-IN - only included when explicitly requested)
    if statistical_tests:
        test_cols = ['normality_test', 'uniformity_test']
        selected_cols.extend([c for c in test_cols if c in summary_df.columns])
    
    # Quality Assessment section (OPT-IN - only included when explicitly requested)
    if quality_assessment or quality_test:
        quality_cols = ['usability_flags', 'usability_score', 'recommendation', 'quality_score', 'quality_assessment']
        selected_cols.extend([c for c in quality_cols if c in summary_df.columns])
    
    # Samples section (OPT-IN - only included when explicitly requested)
    if samples:
        sample_cols = ['samples']
        selected_cols.extend([c for c in sample_cols if c in summary_df.columns])
    
    # Correlation section (OPT-IN - only included when explicitly requested)
    if correlation and corr_target:
        corr_cols = ['correlation', 'correlation_plot']
        selected_cols.extend([c for c in corr_cols if c in summary_df.columns])
    
    # Select only the columns that exist in the dataframe
    available_cols = [c for c in selected_cols if c in summary_df.columns]
    final_df = summary_df.select(available_cols)

    # Return standard DataFrame if great_tables=False
    if not great_tables:
        return final_df

    # Build Great Tables object
    # Calculate timing
    end_time = time.perf_counter()
    execution_time_ms = (end_time - start_time) * 1000
    
    # Determine if this is expanded mode (any opt-in sections enabled)
    is_expanded = any([statistical_tests, quality_assessment, quality_test, samples, correlation])
    
    if is_expanded:
        return _build_expanded_gt_table(final_df, df.height, df.width, df, execution_time_ms, corr_target, percentiles, decimals, sep_mark, dec_mark, compact, title, quality_test, basic_statistics, counts_ratios, distribution, statistical_tests, quality_assessment, samples, correlation)
    else:
        return _build_minimal_gt_table(final_df, df.height, df.width, df, execution_time_ms, corr_target, percentiles, decimals, sep_mark, dec_mark, compact, title, quality_test, basic_statistics, counts_ratios, distribution)


# Helper Functions

def _percentile_to_label(p: float) -> str:
    """Convert percentile float to column label in percent format."""
    if p == 0.5:
        return "50%"  # Keep 50% instead of "Median" for consistency
    else:
        return f"{int(p*100)}%"


def _calculate_quantiles(series: pl.Series, percentiles: list[float]) -> dict:
    """Calculate quantiles for a series."""
    quantile_stats = {}
    for p in percentiles:
        label = _percentile_to_label(p)
        if len(series) > 0:
            val = float(series.quantile(p))
            quantile_stats[label] = round(val, 3)
        else:
            quantile_stats[label] = None
    return quantile_stats


def _calculate_kurtosis(data: np.ndarray) -> float:
    """Calculate excess kurtosis (kurtosis - 3)."""
    if len(data) < 4:
        return np.nan
    
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    
    if std == 0:
        return np.nan
    
    # Calculate fourth moment
    fourth_moment = np.mean((data - mean) ** 4)
    kurtosis = fourth_moment / (std ** 4)
    
    # Return excess kurtosis (subtract 3 for normal distribution)
    return kurtosis - 3


def _suggest_optimal_dtype(series: pl.Series, current_dtype) -> str:
    """Suggest optimal data type for a series."""
    if len(series) == 0:
        return str(current_dtype)
    
    # Check if boolean
    unique_vals = set(series.unique().to_list())
    if unique_vals.issubset({0, 1}) or unique_vals.issubset({True, False}):
        return "Bool"
    
    if current_dtype.is_integer():
        try:
            min_val = int(series.min())
            max_val = int(series.max())
        except (ValueError, TypeError):
            # Handle cases where min/max return non-integer types
            return str(current_dtype)
        
        # Check if fits in smaller integer types
        if -128 <= min_val <= 127 and -128 <= max_val <= 127:
            return "Int8"
        elif -32768 <= min_val <= 32767 and -32768 <= max_val <= 32767:
            return "Int16"
        elif -2147483648 <= min_val <= 2147483647:
            return "Int32"
        else:
            return "Int64"
    
    elif current_dtype.is_float():
        # For floats, check if values could be represented as integers
        if all(x.is_integer() for x in series.to_list() if not np.isnan(x)):
            # Could be integer, suggest Int64
            return "Int64"
        else:
            # Check precision requirements
            return "Float32"  # Usually sufficient for most data
    
    elif current_dtype == pl.String:
        # Check if categorical would be better
        try:
            # Use approximate count for large datasets (>300k rows)
            if len(series) > 300000:
                n_unique = series.approx_n_unique()
            else:
                n_unique = series.n_unique()
        except Exception:
            # Fallback for problematic dtypes
            n_unique = series.drop_nulls().value_counts().height
        
        n_total = len(series)
        if n_unique / n_total < 0.5:  # Less than 50% unique
            return "Categorical"
        return "String"
    
    return str(current_dtype)


def _test_normality(data: np.ndarray, test_type: str) -> str:
    """Perform normality test and return formatted result."""
    if not _check_scipy_availability():
        return "N/A (scipy not available)"
    
    if len(data) < 3:
        return "N/A (insufficient data)"
    
    try:
        if test_type == "shapiro":
            if len(data) > 5000:
                # Shapiro-Wilk test not reliable for large samples
                return "N/A (sample too large)"
            stat, p_value = stats.shapiro(data)
            test_name = "Shapiro-Wilk"
            
        elif test_type == "anderson":
            result = stats.anderson(data, dist='norm')
            # Anderson-Darling uses critical values, not p-values
            # Use 5% significance level (index 2 in critical_values)
            is_normal = result.statistic < result.critical_values[2]
            p_value = None  # A-D doesn't give exact p-value
            test_name = "Anderson-Darling"
            
        elif test_type == "ks":
            # Lilliefors test (KS test with estimated parameters)
            stat, p_value = stats.kstest(data, 'norm', args=(np.mean(data), np.std(data)))
            test_name = "Kolmogorov-Smirnov"
        
        # Format result
        if test_type == "anderson":
            result_str = "NORMAL" if is_normal else "NON-NORMAL"
            return f"{result_str} ({test_name})"
        else:
            alpha = 0.05
            is_normal = p_value > alpha
            result_str = "NORMAL" if is_normal else "NON-NORMAL"
            return f"{result_str} ({test_name}, p={p_value:.3f})"
            
    except Exception as e:
        return f"Error ({test_type}): {str(e)[:20]}"


def _test_uniformity(data: np.ndarray, test_type: str) -> str:
    """Perform uniformity test and return formatted result."""
    if not _check_scipy_availability():
        return "N/A (scipy not available)"
    
    if len(data) < 5:
        return "N/A (insufficient data)"
    
    try:
        if test_type == "ks":
            # KS test against uniform distribution
            min_val, max_val = np.min(data), np.max(data)
            if min_val == max_val:
                return "N/A (constant data)"
            
            # Normalize to [0,1] for uniform test
            normalized = (data - min_val) / (max_val - min_val)
            stat, p_value = stats.kstest(normalized, 'uniform')
            test_name = "KS"
            
        elif test_type == "chi2":
            # Chi-square goodness of fit test
            # Create bins and expected frequencies
            n_bins = min(10, int(np.sqrt(len(data))))
            observed, bin_edges = np.histogram(data, bins=n_bins)
            expected = np.full(n_bins, len(data) / n_bins)
            
            # Remove bins with very low expected frequency
            mask = expected >= 5
            if np.sum(mask) < 2:
                return "N/A (insufficient bins)"
            
            stat, p_value = stats.chisquare(observed[mask], expected[mask])
            test_name = "Chi-square"
        
        # Format result
        alpha = 0.05
        is_uniform = p_value > alpha
        result_str = "UNIFORM" if is_uniform else "NON-UNIFORM"
        return f"{result_str} ({test_name}, p={p_value:.3f})"
        
    except Exception as e:
        return f"Error ({test_type}): {str(e)[:20]}"




def _calculate_histogram_bins(series: pl.Series, n_bins: int | None = None) -> list[int]:
    """Calculate histogram bin counts for a numeric series."""
    try:
        # Remove nulls for histogram calculation
        clean_series = series.drop_nulls()
        
        if clean_series.len() == 0:
            return []
        
        # Calculate optimal number of bins if not provided
        if n_bins is None:
            n = clean_series.len()
            if n < 10:
                n_bins = 5
            elif n < 50:
                n_bins = int(np.ceil(np.log2(n) + 1))  # Sturges' rule
            else:
                # Freedman-Diaconis rule
                q75 = clean_series.quantile(0.75)
                q25 = clean_series.quantile(0.25)
                iqr = q75 - q25
                if iqr > 0:
                    bin_width = 2 * iqr / (n ** (1/3))
                    data_range = clean_series.max() - clean_series.min()
                    n_bins = max(5, min(20, int(np.ceil(data_range / bin_width))))
                else:
                    n_bins = 10
        
        # Ensure reasonable bounds for nanoplots (compact histograms)
        n_bins = max(5, min(12, n_bins))
        
        # Calculate histogram using numpy
        values = clean_series.to_numpy()
        counts, _ = np.histogram(values, bins=n_bins)
        
        return counts.tolist()
        
    except Exception:
        # Return empty list if histogram calculation fails
        return []


def _calculate_shakiness_score(
    col_stats: dict, 
    missing_threshold: float,
    constant_threshold: float,
    skew_threshold: float,
    kurtosis_threshold: float,
    outlier_threshold: float
) -> int:
    """Calculate shakiness score based on data quality indicators."""
    score = 0
    
    # High missingness
    if col_stats.get('Pct_Missing', 0) > missing_threshold * 100:
        score += 1
    
    # Constant/quasi-constant
    uniqueness_ratio = col_stats.get('Uniqueness_Ratio', 1)
    # Handle both exact and approximate N_Unique column names
    n_unique_val = col_stats.get('N_Unique', col_stats.get('N_Unique(approx)', 0))
    if uniqueness_ratio == 0 or n_unique_val == 1:
        score += 1
    elif uniqueness_ratio < (1 - constant_threshold):  # Mode percentage > threshold
        score += 1
    
    # ID-like (too many unique values)
    if uniqueness_ratio > 0.95:  # More than 95% unique
        score += 1
    
    # Extreme skewness
    skewness = col_stats.get('Skewness')
    if skewness is not None and abs(skewness) > skew_threshold:
        score += 1
    
    # High kurtosis
    kurtosis = col_stats.get('Kurtosis')
    if kurtosis is not None and abs(kurtosis) > kurtosis_threshold:
        score += 1
    
    # Outlier-heavy
    pct_outliers = col_stats.get('Pct_Outliers', 0)
    if pct_outliers > outlier_threshold * 100:
        score += 1
    
    # Failed normality test
    normality_test = col_stats.get('Normality_Test', '')
    if 'NON-NORMAL' in normality_test:
        score += 1
    
    return score


# Model Usability Functions (inspired by polarsight)

def _check_missing_values_usability(stats: dict) -> set[str]:
    """Check for missing value flags using polarsight thresholds."""
    flags = set()
    null_pct = stats.get('Pct_Missing', 0)
    
    if null_pct > 90.0:  # High missing (>90%)
        flags.add("HM")
    elif null_pct > 50.0:  # Moderate missing (>50%)
        flags.add("MM")
    
    return flags


def _is_likely_id_column(col_name: str, stats: dict) -> bool:
    """
    Advanced ID column detection that considers multiple factors:
    1. Column name patterns (ID, _id, etc.)
    2. High cardinality even with duplicates (historized data)
    3. Sequential patterns in numeric IDs
    4. Format patterns in string IDs
    """
    col_name_lower = col_name.lower()
    
    # Check for ID-like column names using regex pattern (similar to cs.matches)
    import re
    id_pattern = r'(?i)id|key|code|num|no'
    has_id_name = bool(re.search(id_pattern, col_name))
    
    # Get statistics
    n_unique = stats.get('unique_count', stats.get('unique_count(approx)', 0))
    n_total = stats.get('count', 0) + stats.get('null_count', 0)  # Total including nulls
    uniqueness_ratio = stats.get('unique_pct', 0)  # unique_pct is already a decimal (1.0 = 100%)
    
    
    if n_total == 0:
        return False
    
    # High cardinality check (even with duplicates, many unique values suggests ID)
    high_cardinality = n_unique > 1000  # More than 1000 unique values
    
    # Traditional high uniqueness ratio (for non-ID named columns, be strict)
    # But exclude obvious numeric columns that happen to be unique
    if not has_id_name and uniqueness_ratio > 0.95:
        # Check if this looks like a numeric column that's just unique by chance
        # (e.g., revenue, price, etc. that happen to have no duplicates)
        if col_name_lower in ['revenue', 'price', 'amount', 'value', 'cost', 'sales', 'profit', 'income']:
            return False
        return True
    
    # For columns with ID-like names, be more lenient with uniqueness
    # This handles historized datasets where IDs are repeated across time periods
    if has_id_name:
        # If it has an ID-like name and high cardinality, it's likely an ID
        if high_cardinality:
            return True
        # Even with lower cardinality, if uniqueness is reasonable, flag it
        if uniqueness_ratio > 0.1 and n_unique > 100:
            return True
        # If it has an ID-like name and very high uniqueness (>95%), it's likely an ID
        if uniqueness_ratio > 0.95:
            return True
    
    return False


def _check_unique_values_usability(stats: dict) -> set[str]:
    """Check for unique value related flags using enhanced ID detection."""
    flags = set()
    n_unique_val = stats.get('unique_count', stats.get('unique_count(approx)', 0))
    count = stats.get('count', 1)
    col_name = stats.get('Column', '')
    
    if count > 0:
        # Use the uniqueness ratio from stats if available, otherwise calculate it
        # uniqueness_ratio = stats.get('Uniqueness_Ratio', 0) * 100  # Not used in this function
        
        if n_unique_val == 1:  # Constant value
            flags.add("CV")
        elif n_unique_val == 2:  # Binary column
            flags.add("BN")
        elif _is_likely_id_column(col_name, stats):  # Enhanced ID detection
            flags.add("ID")
    
    return flags


def _check_distribution_usability(stats: dict) -> set[str]:
    """Check for distribution-related flags using polarsight thresholds."""
    flags = set()
    
    # Check outliers
    outlier_pct = stats.get('Pct_Outliers', 0)
    if outlier_pct > 10.0:  # Extreme outliers (>10%)
        flags.add("EO")
    
    # Check skew
    skew = stats.get('skew')
    if skew is not None and abs(skew) > 3.0:  # Extreme skew (|skew| > 3)
        flags.add("ES")
    
    # Check kurtosis
    kurtosis = stats.get('Kurtosis')
    if kurtosis is not None and abs(kurtosis) > 7.0:  # Extreme kurtosis (|kurtosis| > 7)
        flags.add("EK")
    
    # Check normality
    normality_test = stats.get('Normality_Test', '')
    if 'NON-NORMAL' in normality_test:  # Non-normal distribution
        flags.add("NN")
    
    # Check zero values
    zero_pct = stats.get('Pct_Zero', 0)
    if zero_pct > 80.0:  # High zero values (>80%)
        flags.add("ZH")
    
    return flags


def _check_correlation_reliability_usability(stats: dict, has_correlation: bool) -> set[str]:
    """Check if correlation values are reliable using polarsight logic."""
    flags = set()
    
    # If column is non-normal and we're showing correlations, flag it
    if has_correlation and 'NON-NORMAL' in stats.get('Normality_Test', ''):
        flags.add("UC")
    
    return flags


def _calculate_usability_score(flags: set[str]) -> tuple[float, str]:
    """
    Calculate model usability score based on flags using polarsight weights.
    Returns score (0-100, higher is better) and recommendation.
    """
    # Define flag weights (from polarsight)
    flag_weights = {
        "HM": 5.0,  # High missing values (>90%)
        "MM": 3.0,  # Moderate missing values (>50%)
        "ID": 4.0,  # ID-like column (>95% unique values)
        "BN": 1.0,  # Binary column (exactly 2 unique values)
        "CV": 5.0,  # Constant value (only 1 unique value)
        "EO": 2.5,  # Extreme outliers (>10% outliers)
        "ES": 2.0,  # Extreme skew (|skew| > 3)
        "EK": 2.0,  # Extreme kurtosis (|kurtosis| > 7)
        "NN": 1.5,  # Non-normal distribution (p-value < 0.01)
        "ZH": 2.5,  # High zero values (>80%)
        "UC": 1.0,  # Unreliable correlation (non-normal with correlation)
    }
    
    if not flags:
        return 100.0, "Good for modelling"
    
    # Calculate weighted penalty
    total_weight = sum(flag_weights.get(flag, 0) for flag in flags)
    
    # Maximum possible weight (if all flags were present)
    max_weight = sum(flag_weights.values())
    
    # Score from 0-100 (higher is better)
    score = max(0, 100 - (total_weight / max_weight * 100))
    
    # Generate recommendation based on flags
    if "CV" in flags:
        recommendation = "Drop - constant value"
    elif "HM" in flags:
        recommendation = "Drop - too many missing values"
    elif "ID" in flags:
        recommendation = "Drop - likely an ID column"
    elif score < 30:
        recommendation = "Use with extreme caution"
    elif score < 50:
        recommendation = "Use with caution"
    elif score < 70:
        recommendation = "Review before using"
    elif score < 90:
        recommendation = "Minor issues - review"
    else:
        recommendation = "Good for modelling"
    
    return score, recommendation


def _evaluate_column_usability(
    stats: dict,
    has_correlation: bool = False
) -> dict[str, any]:
    """
    Evaluate column usability for modelling using polarsight approach.
    
    Returns dictionary with:
    - flags: Set of flag codes
    - flag_string: Comma-separated flag codes
    - score: Usability score (0-100)
    - recommendation: Text recommendation
    """
    flags = set()
    
    # Check all flag categories
    flags.update(_check_missing_values_usability(stats))
    flags.update(_check_unique_values_usability(stats))
    flags.update(_check_distribution_usability(stats))
    flags.update(_check_correlation_reliability_usability(stats, has_correlation))
    
    # Calculate score and recommendation
    score, recommendation = _calculate_usability_score(flags)
    
    return {
        "flags": flags,
        "flag_string": ",".join(sorted(flags)) if flags else "-",
        "score": score,
        "recommendation": recommendation,
    }


def _count_outliers(series: pl.Series, method: str, bounds: list[float] | None) -> int:
    """Count outliers in a series using specified method."""
    if len(series) == 0:
        return 0
    
    if method == "iqr":
        q25 = series.quantile(0.25)
        q75 = series.quantile(0.75)
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        
    elif method == "percentile":
        lower_bound = series.quantile(bounds[0])
        upper_bound = series.quantile(bounds[1])
        
    elif method == "zscore":
        mean_val = series.mean()
        std_val = series.std()
        if std_val == 0:
            return 0
        lower_bound = mean_val - 3 * std_val
        upper_bound = mean_val + 3 * std_val
    
    # Count values outside bounds using boolean indexing
    mask = (series < lower_bound) | (series > upper_bound)
    return int(mask.sum())


def _build_minimal_gt_table(
    summary_df: pl.DataFrame,
    n_rows: int,
    n_cols: int,
    df: pl.DataFrame,
    execution_ms: float,
    corr_target: str | None,
    percentiles: list[float],
    decimals: int,
    sep_mark: str,
    dec_mark: str,
    compact: bool,
    title: str | None,
    quality_test: bool = False,
    basic_statistics: bool = True,
    counts_ratios: bool = True,
    distribution: bool = True
) -> GT:
    """Build minimal Great Tables object."""
    # Determine column organization based on section arguments
    basic_cols = []
    essential_cols = []
    quality_cols = []
    
    # Always include dtype_optimal as the second column
    basic_cols = ["dtype_optimal"] if "dtype_optimal" in summary_df.columns else []
    
    # Basic Statistics section
    if basic_statistics:
        basic_cols.extend(["dtype", "count", "mean", "std", "min", "max", "iqr"])
    
    # Quantiles section
    quantile_cols = []
    if basic_statistics:
        quantile_cols = [str(_percentile_to_label(p)) for p in percentiles if _percentile_to_label(p) in summary_df.columns]
    
    # Counts & Ratios section
    if counts_ratios:
        n_unique_cols = [c for c in ["unique_count", "unique_count(approx)"] if c in summary_df.columns]
        essential_cols = ["null_count", "null_pct", "zero_count", "zero_pct"] + n_unique_cols + ["unique_pct", "outlier_count", "outlier_pct", "duplicates_count", "duplicates_pct", "positive_pct", "negative_pct"]
    
    # Distribution section
    distribution_cols = []
    if distribution:
        distribution_cols = ["variance", "skew", "kurtosis", "mad"]
        # Add histogram for Great Tables (first column in Distribution section)
        if "histogram" in summary_df.columns:
            distribution_cols.insert(0, "histogram")
    
    # Filter to existing columns and ensure all are strings
    basic_cols = [str(c) for c in basic_cols if c in summary_df.columns]
    quantile_cols = [str(c) for c in quantile_cols if c in summary_df.columns]
    essential_cols = [str(c) for c in essential_cols if c in summary_df.columns] 
    distribution_cols = [str(c) for c in distribution_cols if c in summary_df.columns]
    quality_cols = [str(c) for c in quality_cols if c in summary_df.columns]
    
    try:
        # Use custom title or default
        table_title = title if title is not None else "🔬 DataFrame X-ray"
        
        gt_table = (
            GT(summary_df)
            .tab_header(
                title=table_title,
                subtitle=f"Dataset: {n_rows:,} rows × {n_cols} columns ({_format_memory_usage(df)} in memory) - X-rayed in {execution_ms:.0f} ms"
            )
        )
    except Exception as e:
        # If GT creation fails, return a basic table without advanced formatting
        raise ValueError(f"Great Tables formatting failed. Try using great_tables=False. Error: {e}")
    
    # Add spanners only for non-empty column groups
    if basic_cols:
        gt_table = gt_table.tab_spanner(label="Basic Statistics", columns=basic_cols)
    if quantile_cols:
        gt_table = gt_table.tab_spanner(label="Quantiles", columns=quantile_cols)
    if essential_cols:
        gt_table = gt_table.tab_spanner(label="Counts & Ratios", columns=essential_cols)
    if distribution_cols:
        gt_table = gt_table.tab_spanner(label="Distribution", columns=distribution_cols)
    if quality_cols:
        gt_table = gt_table.tab_spanner(label="Quality", columns=quality_cols)
    
    gt_table = (
        gt_table
        .fmt_integer(columns=[c for c in ["count", "null_count", "outlier_count"] if c in summary_df.columns], sep_mark=sep_mark)
        .fmt_number(
            columns=[c for c in ["mean", "std", "min", "0.25", "0.5", "0.75", "max", "iqr", "skew"] if c in summary_df.columns], 
            decimals=decimals, 
            sep_mark=sep_mark, 
            dec_mark=dec_mark,
            compact=compact,
        )
        .fmt_number(columns=[c for c in ["null_pct"] if c in summary_df.columns], decimals=1, sep_mark=sep_mark, dec_mark=dec_mark)
        .cols_align(align="center", columns=[str(c) for c in (basic_cols + quantile_cols + essential_cols + distribution_cols + quality_cols)])
        .cols_align(align="left", columns=["Column"])
        .tab_options(
            table_font_size="13px",
            heading_background_color="#f8f9fa",
            column_labels_background_color="#e9ecef"
        )
    )
    
    # Add correlation if specified
    if corr_target and "Correlation" in summary_df.columns:
        gt_table = (
            gt_table
            .tab_spanner(label=f"Correlation with '{corr_target}'", columns=["correlation"])
            # Note: Skip fmt_number for Correlation since it contains both numbers and '-' string
            .cols_align(align="center", columns=["Correlation"])
        )
    
    # Add histogram nanoplots for numeric columns (if Histogram column exists)
    if "histogram" in summary_df.columns:
        try:
            from great_tables import nanoplot_options
            # Always use histogram for distribution plots
            gt_table = gt_table.fmt_nanoplot(
                    columns="histogram",
                    plot_type="bar",
                    options=nanoplot_options(
                        data_bar_stroke_width=0,  # No gaps between bars (like histogram)
                        data_bar_fill_color="#4A90E2",
                        show_data_line=False,
                        show_data_area=False
                    )
                )
        except ImportError:
            # If nanoplot_options not available, use basic nanoplot
            plot_type = "bar"
            gt_table = gt_table.fmt_nanoplot(columns="histogram", plot_type=plot_type)
        except Exception:
            # If nanoplot formatting fails, continue without it
            pass
    
    # Add correlation nanoplots (horizontal bars with fixed -1 to 1 scale)
    if "Correlation_Plot" in summary_df.columns:
        try:
            from great_tables import nanoplot_options
            gt_table = gt_table.fmt_nanoplot(
                columns="Correlation_Plot",
                plot_type="bar",
                expand_x=[-1, 1],  # Fixed scale from -1 to 1
                options=nanoplot_options(
                    data_bar_stroke_width=1,
                    data_bar_fill_color="#4A90E2",
                    data_bar_negative_fill_color="#E24A4A",  # Red for negative correlations
                    show_data_line=False,
                    show_data_area=False
                )
            )
        except ImportError:
            # If nanoplot_options not available, use basic nanoplot
            gt_table = gt_table.fmt_nanoplot(columns="Correlation_Plot", plot_type="bar")
        except Exception:
            # If nanoplot formatting fails, continue without it
            pass
    
    return gt_table


def _build_expanded_gt_table(
    summary_df: pl.DataFrame,
    n_rows: int,
    n_cols: int,
    df: pl.DataFrame,
    execution_ms: float,
    corr_target: str | None,
    percentiles: list[float],
    decimals: int,
    sep_mark: str,
    dec_mark: str,
    compact: bool,
    title: str | None,
    quality_test: bool = False,
    basic_statistics: bool = True,
    counts_ratios: bool = True,
    distribution: bool = True,
    statistical_tests: bool = False,
    quality_assessment: bool = False,
    samples: bool | int = False,
    correlation: bool = False
) -> GT:
    """Build expanded Great Tables object with all statistics."""
    # Organize columns by category based on section arguments
    basic_cols = []
    quantile_cols = []
    distribution_cols = []
    count_cols = []
    test_cols = []
    quality_cols = []
    
    # Always include dtype_optimal as the second column
    basic_cols = ["dtype_optimal"] if "dtype_optimal" in summary_df.columns else []
    
    # Basic Statistics section
    if basic_statistics:
        basic_cols.extend(["dtype", "count", "mean", "std", "min"])
        quantile_cols = [str(_percentile_to_label(p)) for p in percentiles if _percentile_to_label(p) in summary_df.columns]
        basic_cols.extend(["max", "iqr"])
    
    # Counts & Ratios section
    if counts_ratios:
        n_unique_cols = [c for c in ["unique_count", "unique_count(approx)"] if c in summary_df.columns]
        count_cols = ["null_count", "null_pct", "zero_count", "zero_pct"] + n_unique_cols + ["unique_pct", "outlier_count", "outlier_pct", "duplicates_count", "duplicates_pct", "positive_pct", "negative_pct"]
    
    # Distribution section
    if distribution:
        distribution_cols = ["variance", "skew", "kurtosis", "mad"]
        # Add histogram for Great Tables (first column in Distribution section)
        if "histogram" in summary_df.columns:
            distribution_cols.insert(0, "histogram")
    
    # Statistical Tests section
    if statistical_tests:
        test_cols = ["normality_test", "uniformity_test"]
    
    # Quality Assessment section
    if quality_assessment or quality_test:
        quality_cols = ["quality_score", "quality_assessment"]
        if quality_test:
            quality_cols.extend(["usability_flags", "usability_score", "recommendation"])
    
    # Samples section
    sample_cols = []
    if samples:
        sample_cols = ["samples"]
    
    # Filter to existing columns and ensure all are strings
    basic_cols = [str(c) for c in basic_cols if c in summary_df.columns]
    distribution_cols = [str(c) for c in distribution_cols if c in summary_df.columns]
    count_cols = [str(c) for c in count_cols if c in summary_df.columns]
    test_cols = [str(c) for c in test_cols if c in summary_df.columns]
    quality_cols = [str(c) for c in quality_cols if c in summary_df.columns]
    sample_cols = [str(c) for c in sample_cols if c in summary_df.columns]
    
    try:
        # Use custom title or default
        table_title = title if title is not None else "🔬 Expanded Statistics"
        
        gt_table = (
            GT(summary_df)
            .tab_header(
                title=table_title,
                subtitle=f"Dataset: {n_rows:,} rows × {n_cols} columns ({_format_memory_usage(df)} in memory) - X-rayed in {execution_ms:.0f} ms"
            )
        )
    except Exception as e:
        # If GT creation fails, return a basic table without advanced formatting
        raise ValueError(f"Great Tables formatting failed. Try using great_tables=False. Error: {e}")
    
    # Add spanners only for non-empty column groups
    if basic_cols:
        gt_table = gt_table.tab_spanner(label="Basic Statistics", columns=basic_cols)
    if quantile_cols:
        gt_table = gt_table.tab_spanner(label="Quantiles", columns=quantile_cols)
    if distribution_cols:
        gt_table = gt_table.tab_spanner(label="Distribution", columns=distribution_cols)
    if count_cols:
        gt_table = gt_table.tab_spanner(label="Counts & Ratios", columns=count_cols)
    if test_cols:
        gt_table = gt_table.tab_spanner(label="Statistical Tests", columns=test_cols)
    if quality_cols:
        gt_table = gt_table.tab_spanner(label="Quality Assessment", columns=quality_cols)
    if sample_cols:
        gt_table = gt_table.tab_spanner(label="Samples", columns=sample_cols)
    
    gt_table = (
        gt_table
        .fmt_integer(columns=[c for c in ["count", "null_count"] + n_unique_cols + ["duplicates_count", "zero_count", "outlier_count", "quality_score"] + (["usability_score"] if quality_test and "usability_score" in summary_df.columns else []) if c in summary_df.columns], sep_mark=sep_mark)
        .fmt_number(
            columns=[c for c in ["mean", "std", "min", "max", "iqr", "mad"] + quantile_cols if c in summary_df.columns], 
            decimals=decimals, 
            sep_mark=sep_mark, 
            dec_mark=dec_mark,
            compact=compact,
        )
        .fmt_number(columns=[c for c in ["skew", "kurtosis"] if c in summary_df.columns], decimals=3, sep_mark=sep_mark, dec_mark=dec_mark)
        .fmt_number(columns=[c for c in ["null_pct", "duplicates_pct", "zero_pct", "positive_pct", "negative_pct", "outlier_pct"] if c in summary_df.columns], decimals=1, sep_mark=sep_mark, dec_mark=dec_mark)
        .fmt_number(columns=[c for c in ["unique_pct"] if c in summary_df.columns], decimals=4, sep_mark=sep_mark, dec_mark=dec_mark)
        .cols_align(align="center", columns=[str(c) for c in (basic_cols + quantile_cols + distribution_cols + count_cols + (["quality_score"] if "quality_score" in summary_df.columns else []) + (["usability_score"] if quality_test and "usability_score" in summary_df.columns else []))])
        .cols_align(align="left", columns=[str(c) for c in (["Column"] + (["dtype_optimal"] if "dtype_optimal" in summary_df.columns else []) + (["quality_assessment"] if "quality_assessment" in summary_df.columns else []) + (["usability_flags", "recommendation"] if quality_test else []) + test_cols + sample_cols)])
        .tab_options(
            table_font_size="12px",
            heading_background_color="#f8f9fa", 
            column_labels_background_color="#e9ecef"
        )
    )
    
    # Add correlation if specified
    if corr_target and "Correlation" in summary_df.columns:
        gt_table = (
            gt_table
            .tab_spanner(label=f"Correlation with '{corr_target}'", columns=["correlation"])
            # Note: Skip fmt_number for Correlation since it contains both numbers and '-' string
            .cols_align(align="center", columns=["Correlation"])
        )
    
    # Add histogram nanoplots for numeric columns (if Histogram column exists)
    if "histogram" in summary_df.columns:
        try:
            from great_tables import nanoplot_options
            # Always use histogram for distribution plots
            gt_table = gt_table.fmt_nanoplot(
                    columns="histogram",
                    plot_type="bar",
                    options=nanoplot_options(
                        data_bar_stroke_width=0,  # No gaps between bars (like histogram)
                        data_bar_fill_color="#4A90E2",
                        show_data_line=False,
                        show_data_area=False
                    )
                )
        except ImportError:
            # If nanoplot_options not available, use basic nanoplot
            plot_type = "bar"
            gt_table = gt_table.fmt_nanoplot(columns="histogram", plot_type=plot_type)
        except Exception:
            # If nanoplot formatting fails, continue without it
            pass
    
    # Add correlation nanoplots (horizontal bars with fixed -1 to 1 scale)
    if "Correlation_Plot" in summary_df.columns:
        try:
            from great_tables import nanoplot_options
            gt_table = gt_table.fmt_nanoplot(
                columns="Correlation_Plot",
                plot_type="bar",
                expand_x=[-1, 1],  # Fixed scale from -1 to 1
                options=nanoplot_options(
                    data_bar_stroke_width=1,
                    data_bar_fill_color="#4A90E2",
                    data_bar_negative_fill_color="#E24A4A",  # Red for negative correlations
                    show_data_line=False,
                    show_data_area=False
                )
            )
        except ImportError:
            # If nanoplot_options not available, use basic nanoplot
            gt_table = gt_table.fmt_nanoplot(columns="Correlation_Plot", plot_type="bar")
        except Exception:
            # If nanoplot formatting fails, continue without it
            pass
    
    return gt_table