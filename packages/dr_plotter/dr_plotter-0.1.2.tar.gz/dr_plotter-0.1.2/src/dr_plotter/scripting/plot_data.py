from __future__ import annotations


import numpy as np
import pandas as pd


def experimental_data(
    n_samples: int = 120,
    time_points: int = 20,
    categories: list[str] | None = None,
    groups: list[str] | None = None,
    experiments: list[str] | None = None,
    conditions: list[str] | None = None,
    metrics: list[str] | None = None,
    pattern_type: str = "time_series",
    noise_level: float = 0.05,
    trend_strength: float = 0.1,
    seed: int = 42,
) -> pd.DataFrame:
    np.random.seed(seed)

    if categories is None:
        categories = [f"Cat_{chr(65 + i)}" for i in range(4)]
    if groups is None:
        groups = [f"Group_{chr(65 + i)}" for i in range(3)]
    if experiments is None:
        experiments = ["Exp_A", "Exp_B"]
    if conditions is None:
        conditions = ["Control", "Treatment"]
    if metrics is None:
        metrics = ["performance", "accuracy"]

    if pattern_type == "time_series":
        return _generate_time_series_pattern(
            time_points, groups, noise_level, trend_strength, n_samples
        )
    elif pattern_type == "categorical":
        return _generate_categorical_pattern(categories, groups, n_samples, noise_level)
    elif pattern_type == "ml_training":
        return _generate_ml_training_pattern(
            time_points, metrics, experiments, noise_level
        )
    elif pattern_type == "ab_test":
        return _generate_ab_test_pattern(
            time_points, experiments, conditions, noise_level
        )
    elif pattern_type == "distribution":
        return _generate_distribution_pattern(n_samples, groups)
    elif pattern_type == "multi_dimensional":
        return _generate_multi_dimensional_pattern(
            experiments, conditions, categories, n_samples, noise_level
        )
    else:
        raise ValueError(f"Unknown pattern_type: {pattern_type}")


def matrix_data(
    rows: int = 8,
    cols: int = 6,
    row_names: list[str] | None = None,
    col_names: list[str] | None = None,
    pattern_type: str = "heatmap",
    correlation_strength: float = 0.3,
    seed: int = 42,
) -> pd.DataFrame:
    np.random.seed(seed)

    if row_names is None:
        row_names = [f"Row_{i + 1}" for i in range(rows)]
    if col_names is None:
        col_names = [f"Col_{chr(65 + i)}" for i in range(cols)]

    if pattern_type == "heatmap":
        return _generate_heatmap_pattern(row_names, col_names, correlation_strength)
    elif pattern_type == "contour":
        return _generate_contour_pattern(rows, cols)
    elif pattern_type == "correlation":
        return _generate_correlation_pattern(row_names, col_names, correlation_strength)
    else:
        raise ValueError(f"Unknown pattern_type: {pattern_type}")


def _generate_time_series_pattern(
    time_points: int,
    groups: list[str],
    noise_level: float,
    trend_strength: float,
    n_samples: int,
) -> pd.DataFrame:
    records = []

    for group in groups:
        base_trend = np.random.randn() * trend_strength
        values = np.random.randn(time_points).cumsum() + base_trend * np.arange(
            time_points
        )

        for t, v in enumerate(values):
            records.append(
                {
                    "time_point": t,
                    "value": v + np.random.randn() * noise_level,
                    "group": group,
                    "x_continuous": np.random.randn(),
                    "y_continuous": v + np.random.randn() * noise_level,
                    "category": np.random.choice(
                        [f"Cat_{chr(65 + i)}" for i in range(4)]
                    ),
                }
            )

    return pd.DataFrame(records)


def _generate_categorical_pattern(
    categories: list[str], groups: list[str], n_samples: int, noise_level: float
) -> pd.DataFrame:
    records = []
    samples_per_combo = max(1, n_samples // (len(categories) * len(groups)))

    for category in categories:
        for group in groups:
            base_value = np.random.randn() * 2
            group_effect = np.random.randn() * 0.5

            for _ in range(samples_per_combo):
                x_cont = np.random.randn()
                y_cont = base_value + group_effect + np.random.randn() * noise_level

                records.append(
                    {
                        "category": category,
                        "group": group,
                        "value": y_cont,
                        "x_continuous": x_cont,
                        "y_continuous": y_cont,
                        "time_point": np.random.randint(0, 20),
                    }
                )

    return pd.DataFrame(records)


def _generate_ml_training_pattern(
    time_points: int, metrics: list[str], experiments: list[str], noise_level: float
) -> pd.DataFrame:
    records = []
    learning_rates = [0.001, 0.01, 0.1]

    for lr in learning_rates:
        convergence_speed = lr * 10

        for epoch in range(time_points):
            train_loss = np.exp(-epoch * convergence_speed / time_points) * (
                1 + np.random.randn() * noise_level
            )
            val_loss = train_loss * (1.1 + np.random.randn() * noise_level * 0.5)
            train_acc = 1 - train_loss * 0.9
            val_acc = 1 - val_loss * 0.9

            records.extend(
                [
                    {
                        "time_point": epoch,
                        "learning_rate": lr,
                        "train_loss": train_loss,
                        "val_loss": val_loss,
                        "train_accuracy": train_acc,
                        "val_accuracy": val_acc,
                        "value": train_loss,
                        "metric_name": "loss",
                        "group": f"lr_{lr}",
                        "experiment": experiments[0] if experiments else "default",
                    },
                    {
                        "time_point": epoch,
                        "learning_rate": lr,
                        "train_loss": train_loss,
                        "val_loss": val_loss,
                        "train_accuracy": train_acc,
                        "val_accuracy": val_acc,
                        "value": train_acc,
                        "metric_name": "accuracy",
                        "group": f"lr_{lr}",
                        "experiment": experiments[0] if experiments else "default",
                    },
                ]
            )

    return pd.DataFrame(records)


def _generate_ab_test_pattern(
    time_points: int, experiments: list[str], conditions: list[str], noise_level: float
) -> pd.DataFrame:
    records = []

    for experiment in experiments:
        for condition in conditions:
            base_performance = 0.6 if experiment == "Exp_A" else 0.7
            treatment_boost = 0.1 if condition == "Treatment" else 0.0
            performance_trend = np.random.randn() * 0.02

            for t in range(time_points):
                trend_component = performance_trend * t
                seasonal_component = 0.05 * np.sin(2 * np.pi * t / 10)
                noise_component = np.random.randn() * noise_level

                performance = np.clip(
                    base_performance
                    + treatment_boost
                    + trend_component
                    + seasonal_component
                    + noise_component,
                    0.3,
                    1.0,
                )

                records.append(
                    {
                        "experiment": experiment,
                        "condition": condition,
                        "time_point": t,
                        "value": performance,
                        "group": condition,
                        "category": experiment,
                        "x_continuous": t,
                        "y_continuous": performance,
                    }
                )

    return pd.DataFrame(records)


def _generate_distribution_pattern(n_samples: int, groups: list[str]) -> pd.DataFrame:
    records = []
    samples_per_group = n_samples // len(groups)

    for i, group in enumerate(groups):
        if i == 0:
            values = np.random.randn(samples_per_group)
        elif i == 1:
            values = np.random.gamma(2, 2, samples_per_group)
        else:
            values = np.concatenate(
                [
                    np.random.normal(-2, 0.5, samples_per_group // 2),
                    np.random.normal(2, 0.5, samples_per_group // 2),
                ]
            )

        records.extend(
            [
                {
                    "value": val,
                    "group": group,
                    "distribution": group,
                    "x_continuous": val,
                    "y_continuous": np.random.randn(),
                    "category": group,
                }
                for val in values
            ]
        )

    return pd.DataFrame(records)


def _generate_multi_dimensional_pattern(
    experiments: list[str],
    conditions: list[str],
    categories: list[str],
    n_samples: int,
    noise_level: float,
) -> pd.DataFrame:
    records = []
    algorithms = ["Algo_1", "Algo_2"]
    samples_per_combo = max(
        1, n_samples // (len(experiments) * len(conditions) * len(algorithms))
    )

    for experiment in experiments:
        for condition in conditions:
            for algorithm in algorithms:
                x_offset = 2 if condition == "Treatment" else 0
                y_offset = 1 if condition == "Treatment" else 0
                spread = 1 if algorithm == "Algo_1" else 1.5

                for _ in range(samples_per_combo):
                    x = np.random.randn() * spread + x_offset
                    y = np.random.randn() * spread + y_offset

                    records.append(
                        {
                            "x_continuous": x,
                            "y_continuous": y,
                            "experiment": experiment,
                            "condition": condition,
                            "algorithm": algorithm,
                            "value": x * y + np.random.randn() * noise_level,
                            "group": condition,
                            "category": experiment,
                            "time_point": np.random.randint(0, 20),
                        }
                    )

    return pd.DataFrame(records)


def _generate_heatmap_pattern(
    row_names: list[str], col_names: list[str], correlation_strength: float
) -> pd.DataFrame:
    records = []
    rows, cols = len(row_names), len(col_names)

    base_pattern = np.random.randn(rows, cols)
    base_pattern = np.cumsum(base_pattern, axis=0) * correlation_strength
    base_pattern = np.cumsum(base_pattern, axis=1) * correlation_strength

    for i, row_name in enumerate(row_names):
        for j, col_name in enumerate(col_names):
            records.append(
                {
                    "row": row_name,
                    "column": col_name,
                    "value": base_pattern[i, j] + np.random.randn() * 0.5,
                }
            )

    return pd.DataFrame(records)


def _generate_contour_pattern(n_samples: int, n_components: int = 3) -> pd.DataFrame:
    samples_per_component = n_samples // n_components
    data = []

    means = [(0, 0), (3, 3), (-2, 2)][:n_components]
    covs = [[[1, 0.5], [0.5, 1]], [[2, -0.8], [-0.8, 1]], [[0.8, 0.3], [0.3, 1.5]]][
        :n_components
    ]

    for mean, cov in zip(means, covs):
        samples = np.random.multivariate_normal(mean, cov, samples_per_component)
        data.append(samples)

    all_samples = np.vstack(data)
    return pd.DataFrame(all_samples, columns=["x", "y"])


def _generate_correlation_pattern(
    row_names: list[str], col_names: list[str], correlation_strength: float
) -> pd.DataFrame:
    rows, cols = len(row_names), len(col_names)
    correlation_matrix = np.random.randn(rows, cols)

    for i in range(rows):
        for j in range(cols):
            if i == j and i < min(rows, cols):
                correlation_matrix[i, j] = 1.0
            else:
                correlation_matrix[i, j] = correlation_strength * np.random.randn()

    records = []
    for i, row_name in enumerate(row_names):
        for j, col_name in enumerate(col_names):
            records.append(
                {"row": row_name, "column": col_name, "value": correlation_matrix[i, j]}
            )

    return pd.DataFrame(records)
