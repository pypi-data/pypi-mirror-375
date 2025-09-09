from __future__ import annotations

import numpy as np
import pandas as pd


class ExampleData:
    @staticmethod
    def simple_scatter(n: int = 100, seed: int = 42) -> pd.DataFrame:
        np.random.seed(seed)
        x = np.random.randn(n)
        y = x * 0.5 + np.random.randn(n) * 0.5
        return pd.DataFrame({"x": x, "y": y})

    @staticmethod
    def time_series(
        periods: int = 100, series: int = 1, seed: int = 42
    ) -> pd.DataFrame:
        """Time series data with optional multiple series."""
        np.random.seed(seed)
        data = {"time": np.arange(periods)}

        if series == 1:
            data["value"] = np.random.randn(periods).cumsum()
        else:
            for i in range(series):
                data[f"series_{i + 1}"] = np.random.randn(periods).cumsum()

        return pd.DataFrame(data)

    @staticmethod
    def time_series_grouped(
        periods: int = 50, groups: int = 3, seed: int = 42
    ) -> pd.DataFrame:
        """Time series with categorical groups (for hue encoding)."""
        np.random.seed(seed)
        group_names = [f"Group_{chr(65 + i)}" for i in range(groups)]

        records = []
        for group in group_names:
            base_trend = np.random.randn() * 0.5  # Different trend per group
            values = np.random.randn(periods).cumsum() + base_trend * np.arange(periods)
            for t, v in enumerate(values):
                records.append({"time": t, "value": v, "group": group})

        return pd.DataFrame(records)

    @staticmethod
    def categorical_data(
        n_categories: int = 5, n_per_category: int = 20, seed: int = 42
    ) -> pd.DataFrame:
        """Data with categorical x-axis for bar/violin plots."""
        np.random.seed(seed)
        categories = [f"Cat_{chr(65 + i)}" for i in range(n_categories)]

        records = []
        for cat in categories:
            # Different mean and variance per category
            mean = np.random.randn() * 2
            std = 0.5 + np.random.rand() * 1.5
            values = np.random.normal(mean, std, n_per_category)
            records.extend([{"category": cat, "value": val} for val in values])

        return pd.DataFrame(records)

    @staticmethod
    def grouped_categories(
        n_categories: int = 4, n_groups: int = 3, n_per_combo: int = 10, seed: int = 42
    ) -> pd.DataFrame:
        """Categorical data with additional grouping variable."""
        np.random.seed(seed)
        categories = [f"Cat_{chr(65 + i)}" for i in range(n_categories)]
        groups = [f"Group_{i + 1}" for i in range(n_groups)]

        records = []
        for cat in categories:
            for group in groups:
                # Different effects per combination
                base = np.random.randn() * 2
                group_effect = np.random.randn()
                values = np.random.normal(base + group_effect, 0.8, n_per_combo)
                records.extend(
                    [{"category": cat, "group": group, "value": val} for val in values]
                )

        return pd.DataFrame(records)

    @staticmethod
    def distribution_data(
        n_samples: int = 1000, distributions: int = 1, seed: int = 42
    ) -> pd.DataFrame:
        """Data for histograms with optional multiple distributions."""
        np.random.seed(seed)

        if distributions == 1:
            return pd.DataFrame({"values": np.random.randn(n_samples)})
        else:
            records = []
            dist_names = ["Normal", "Skewed", "Bimodal"][:distributions]

            for dist in dist_names:
                if dist == "Normal":
                    values = np.random.randn(n_samples)
                elif dist == "Skewed":
                    values = np.random.gamma(2, 2, n_samples)
                elif dist == "Bimodal":
                    values = np.concatenate(
                        [
                            np.random.normal(-2, 0.5, n_samples // 2),
                            np.random.normal(2, 0.5, n_samples // 2),
                        ]
                    )
                records.extend([{"value": val, "distribution": dist} for val in values])
            return pd.DataFrame(records)

    @staticmethod
    def heatmap_data(rows: int = 10, cols: int = 8, seed: int = 42) -> pd.DataFrame:
        """Data for heatmap in tidy/long format."""
        np.random.seed(seed)

        records = []
        row_names = [f"Row_{i + 1}" for i in range(rows)]
        col_names = [f"Col_{chr(65 + i)}" for i in range(cols)]

        # Generate correlated patterns
        base_pattern = np.random.randn(rows, cols)
        base_pattern = np.cumsum(base_pattern, axis=0) * 0.3
        base_pattern = np.cumsum(base_pattern, axis=1) * 0.3

        for i, row in enumerate(row_names):
            for j, col in enumerate(col_names):
                records.append(
                    {
                        "row": row,
                        "column": col,
                        "value": base_pattern[i, j] + np.random.randn() * 0.5,
                    }
                )

        return pd.DataFrame(records)

    @staticmethod
    def ranking_data(
        time_points: int = 20, categories: int = 6, seed: int = 42
    ) -> pd.DataFrame:
        """Data for bump plots showing rankings over time."""
        np.random.seed(seed)

        records = []
        category_names = [f"Team_{chr(65 + i)}" for i in range(categories)]

        # Initialize with random starting positions
        positions = {cat: np.random.rand() * 100 for cat in category_names}

        for t in range(time_points):
            # Random walk for each category
            for cat in category_names:
                positions[cat] += np.random.randn() * 5
                positions[cat] = max(0, positions[cat])  # Keep positive

                records.append({"time": t, "category": cat, "score": positions[cat]})

        return pd.DataFrame(records)

    @staticmethod
    def gaussian_mixture(
        n_components: int = 3, n_samples: int = 500, seed: int = 42
    ) -> pd.DataFrame:
        """2D data from gaussian mixture for contour plots."""
        np.random.seed(seed)

        samples_per_component = n_samples // n_components
        data = []

        # Generate components with different means and covariances
        means = [(0, 0), (3, 3), (-2, 2)][:n_components]
        covs = [[[1, 0.5], [0.5, 1]], [[2, -0.8], [-0.8, 1]], [[0.8, 0.3], [0.3, 1.5]]][
            :n_components
        ]

        for mean, cov in zip(means, covs):
            samples = np.random.multivariate_normal(mean, cov, samples_per_component)
            data.append(samples)

        all_samples = np.vstack(data)
        return pd.DataFrame(all_samples, columns=["x", "y"])

    @staticmethod
    def ml_training_curves(
        epochs: int = 50,
        learning_rates: list[float] | None = None,
        metrics: list[str] | None = None,
        seed: int = 42,
    ) -> pd.DataFrame:
        """ML experiment data with train/val metrics."""
        np.random.seed(seed)

        if learning_rates is None:
            learning_rates = [0.001, 0.01, 0.1]
        if metrics is None:
            metrics = ["loss", "accuracy"]

        records = []

        for lr in learning_rates:
            # Simulate training dynamics based on learning rate
            convergence_speed = lr * 10

            for epoch in range(epochs):
                # Loss decreases over time
                train_loss = np.exp(-epoch * convergence_speed / epochs) * (
                    1 + np.random.randn() * 0.1
                )
                val_loss = train_loss * (1.1 + np.random.randn() * 0.05)

                # Accuracy increases over time
                train_acc = 1 - train_loss * 0.9
                val_acc = 1 - val_loss * 0.9

                if "loss" in metrics:
                    records.append(
                        {
                            "epoch": epoch,
                            "learning_rate": lr,
                            "train_loss": train_loss,
                            "val_loss": val_loss,
                        }
                    )

                if "accuracy" in metrics:
                    # If we want both metrics, update the last record
                    if "loss" in metrics:
                        records[-1].update(
                            {"train_accuracy": train_acc, "val_accuracy": val_acc}
                        )
                    else:
                        records.append(
                            {
                                "epoch": epoch,
                                "learning_rate": lr,
                                "train_accuracy": train_acc,
                                "val_accuracy": val_acc,
                            }
                        )

        return pd.DataFrame(records)

    @staticmethod
    def experiment_time_series(time_points: int = 20, seed: int = 401) -> pd.DataFrame:
        np.random.seed(seed)

        experiments = ["Exp_A", "Exp_B"]
        conditions = ["Control", "Treatment"]

        records = []
        for exp in experiments:
            for cond in conditions:
                base_performance = 0.6 if exp == "Exp_A" else 0.7
                treatment_boost = 0.1 if cond == "Treatment" else 0.0

                performance_trend = np.random.randn() * 0.02
                noise_level = 0.03

                for t in range(time_points):
                    trend_component = performance_trend * t
                    seasonal_component = 0.05 * np.sin(2 * np.pi * t / 10)
                    noise_component = np.random.randn() * noise_level

                    performance = (
                        base_performance
                        + treatment_boost
                        + trend_component
                        + seasonal_component
                        + noise_component
                    )
                    performance = np.clip(performance, 0.3, 1.0)

                    records.append(
                        {
                            "experiment": exp,
                            "condition": cond,
                            "time_point": t,
                            "performance": performance,
                        }
                    )

        return pd.DataFrame(records)

    @staticmethod
    def multi_metric_data(n_samples: int = 100, seed: int = 42) -> pd.DataFrame:
        """Data with multiple y-columns for multi-metric plotting."""
        np.random.seed(seed)

        x = np.linspace(0, 10, n_samples)

        return pd.DataFrame(
            {
                "x": x,
                "metric_a": np.sin(x) + np.random.randn(n_samples) * 0.1,
                "metric_b": np.cos(x) + np.random.randn(n_samples) * 0.1,
                "metric_c": np.sin(x * 0.5) * 2 + np.random.randn(n_samples) * 0.1,
                "category": np.repeat(["Type_1", "Type_2"], n_samples // 2)[:n_samples],
            }
        )

    @staticmethod
    def complex_encoding_data(n_samples: int = 120, seed: int = 42) -> pd.DataFrame:
        """Data with multiple grouping variables for complex visual encoding."""
        np.random.seed(seed)

        experiments = ["Exp_A", "Exp_B", "Exp_C"]
        conditions = ["Control", "Treatment"]
        algorithms = ["Algo_1", "Algo_2"]

        records = []
        for exp in experiments:
            for cond in conditions:
                for algo in algorithms:
                    n = n_samples // (
                        len(experiments) * len(conditions) * len(algorithms)
                    )

                    # Different distributions per combination
                    if cond == "Control":
                        x_offset, y_offset = 0, 0
                    else:
                        x_offset, y_offset = 2, 1

                    spread = 1 if algo == "Algo_1" else 1.5

                    x = np.random.randn(n) * spread + x_offset
                    y = np.random.randn(n) * spread + y_offset

                    for xi, yi in zip(x, y):
                        records.append(
                            {
                                "x": xi,
                                "y": yi,
                                "experiment": exp,
                                "condition": cond,
                                "algorithm": algo,
                                "performance": xi * yi + np.random.randn() * 0.5,
                            }
                        )

        return pd.DataFrame(records)

    @staticmethod
    def get_individual_vs_grouped_data() -> pd.DataFrame:
        np.random.seed(600)
        n_samples = 120

        x_continuous = np.random.randn(n_samples)
        y_continuous = x_continuous * 0.7 + np.random.randn(n_samples) * 0.6

        categories = ["Category_A", "Category_B", "Category_C", "Category_D"]
        x_categorical = np.random.choice(categories, n_samples)

        groups = ["Group_1", "Group_2", "Group_3"]
        category_group = np.random.choice(groups, n_samples)

        time_series = np.tile(np.arange(n_samples // 3), 3)

        return pd.DataFrame(
            {
                "x_continuous": x_continuous,
                "y_continuous": y_continuous,
                "x_categorical": x_categorical,
                "category_group": category_group,
                "time_series": time_series,
            }
        )

    @staticmethod
    def get_all_plot_types_data() -> dict[str, pd.DataFrame]:
        np.random.seed(100)

        scatter_data = ExampleData.simple_scatter(n=80, seed=100)
        scatter_data["size_metric"] = np.random.uniform(20, 100, len(scatter_data))
        scatter_data["category"] = np.repeat(["A", "B"], len(scatter_data) // 2)

        line_data = ExampleData.time_series_grouped(periods=30, groups=2, seed=101)

        bar_data = ExampleData.categorical_data(
            n_categories=5, n_per_category=1, seed=102
        )
        bar_data["category_group"] = [
            "Group_1",
            "Group_2",
            "Group_1",
            "Group_2",
            "Group_1",
        ]

        histogram_data = ExampleData.distribution_data(
            n_samples=400, distributions=2, seed=103
        )

        violin_data = ExampleData.grouped_categories(
            n_categories=3, n_groups=2, n_per_combo=25, seed=104
        )

        heatmap_data = ExampleData.heatmap_data(rows=6, cols=5, seed=105)

        contour_data = ExampleData.gaussian_mixture(
            n_components=2, n_samples=300, seed=106
        )

        bump_data = ExampleData.ranking_data(time_points=15, categories=4, seed=107)

        return {
            "scatter_data": scatter_data,
            "line_data": line_data,
            "bar_data": bar_data,
            "histogram_data": histogram_data,
            "violin_data": violin_data,
            "heatmap_data": heatmap_data,
            "contour_data": contour_data,
            "bump_data": bump_data,
        }

    @staticmethod
    def get_color_coordination_data() -> dict[str, pd.DataFrame]:
        np.random.seed(200)
        shared_categories = ["Alpha", "Beta", "Gamma", "Delta"]

        scatter_data = ExampleData.simple_scatter(n=60, seed=200)
        scatter_data["category"] = np.tile(shared_categories, len(scatter_data) // 4)[
            : len(scatter_data)
        ]

        line_data = ExampleData.time_series_grouped(periods=25, groups=4, seed=201)
        line_data["series"] = (
            line_data["group"]
            .map({"Group_A": "Alpha", "Group_B": "Beta", "Group_C": "Gamma"})
            .fillna("Delta")
        )

        violin_data = ExampleData.grouped_categories(
            n_categories=3, n_groups=4, n_per_combo=15, seed=202
        )
        violin_data["group"] = (
            violin_data["group"]
            .map(
                {
                    "Group_1": "Alpha",
                    "Group_2": "Beta",
                    "Group_3": "Gamma",
                    "Group_4": "Delta",
                }
            )
            .fillna("Alpha")
        )

        bar_data = ExampleData.categorical_data(
            n_categories=4, n_per_category=1, seed=203
        )
        bar_data["category"] = shared_categories

        histogram_data = ExampleData.distribution_data(
            n_samples=300, distributions=4, seed=204
        )
        dist_map = {"Normal": "Alpha", "Skewed": "Beta", "Bimodal": "Gamma"}
        histogram_data["distribution"] = (
            histogram_data["distribution"].map(dist_map).fillna("Delta")
        )

        heatmap_data = ExampleData.heatmap_data(rows=4, cols=4, seed=205)

        return {
            "scatter_data": scatter_data,
            "line_data": line_data,
            "violin_data": violin_data,
            "bar_data": bar_data,
            "histogram_data": histogram_data,
            "heatmap_data": heatmap_data,
        }

    @staticmethod
    def get_cross_groupby_legends_data() -> pd.DataFrame:
        np.random.seed(400)

        experiments = ["Exp_A", "Exp_B", "Exp_C"]
        conditions = ["Control", "Treatment"]
        algorithms = ["Method_1", "Method_2", "Method_3"]

        records = []
        for exp in experiments:
            for cond in conditions:
                for algo in algorithms:
                    base_performance = np.random.uniform(0.5, 0.9)
                    base_accuracy = np.random.uniform(0.6, 0.95)

                    n_samples = 15
                    records.extend(
                        [
                            {
                                "experiment": exp,
                                "condition": cond,
                                "algorithm": algo,
                                "performance": base_performance
                                + np.random.normal(0, 0.05),
                                "accuracy": base_accuracy + np.random.normal(0, 0.03),
                                "runtime": np.random.uniform(10, 200),
                                "time_point": np.random.randint(0, 20),
                            }
                            for _ in range(n_samples)
                        ]
                    )
        return pd.DataFrame(records)

    @staticmethod
    def get_individual_styling_data() -> dict[str, pd.DataFrame]:
        np.random.seed(300)

        scatter_data = ExampleData.simple_scatter(n=80, seed=300)
        scatter_data["category"] = np.random.choice(
            ["Type_A", "Type_B", "Type_C"], len(scatter_data)
        )

        line_data = ExampleData.time_series_grouped(periods=40, groups=4, seed=301)

        violin_data = ExampleData.grouped_categories(
            n_categories=3, n_groups=3, n_per_combo=20, seed=302
        )

        bar_data = ExampleData.categorical_data(
            n_categories=5, n_per_category=1, seed=303
        )
        bar_data["category"] = ["A", "B", "C", "D", "E"]

        histogram_data = ExampleData.distribution_data(
            n_samples=400, distributions=1, seed=304
        )

        heatmap_data = ExampleData.heatmap_data(rows=6, cols=6, seed=305)

        return {
            "scatter_data": scatter_data,
            "line_data": line_data,
            "violin_data": violin_data,
            "bar_data": bar_data,
            "histogram_data": histogram_data,
            "heatmap_data": heatmap_data,
        }

    @staticmethod
    def get_legend_positioning_data() -> pd.DataFrame:
        np.random.seed(500)

        categories = ["Alpha", "Beta", "Gamma", "Delta"]
        n_samples_per_category = 25

        records = []
        for category in categories:
            center_x = np.random.uniform(-2, 2)
            center_y = np.random.uniform(-2, 2)

            records.extend(
                [
                    {
                        "category_group": category,
                        "performance": center_x + np.random.normal(0, 0.8),
                        "accuracy": center_y + np.random.normal(0, 0.8),
                        "runtime": np.random.uniform(10, 100),
                        "memory": np.random.uniform(50, 500),
                    }
                    for _ in range(n_samples_per_category)
                ]
            )

        return pd.DataFrame(records)

    @staticmethod
    def get_category_time_series(
        time_points: int = 15, seed: int = 502
    ) -> pd.DataFrame:
        np.random.seed(seed)

        categories = ["Alpha", "Beta", "Gamma", "Delta"]

        records = []
        for category in categories:
            base_performance = np.random.uniform(0.4, 0.8)
            performance_trend = np.random.randn() * 0.03
            noise_level = 0.04

            for t in range(time_points):
                trend_component = performance_trend * t
                seasonal_component = 0.06 * np.sin(2 * np.pi * t / 8)
                noise_component = np.random.randn() * noise_level

                performance = (
                    base_performance
                    + trend_component
                    + seasonal_component
                    + noise_component
                )
                performance = np.clip(performance, 0.2, 1.0)

                records.append(
                    {
                        "category_group": category,
                        "time_point": t,
                        "performance": performance,
                    }
                )

        return pd.DataFrame(records)
