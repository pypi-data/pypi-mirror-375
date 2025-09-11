"""
Utilities for anomaly detection benchmarking on battery cell data.

This module provides the :class:`ModelRunner` class to orchestrate data
preparation, prediction, evaluation, and visualization for a single cell.
It supports several PyOD models via the :data:`PyODModelType` type alias
and produces publication-ready figures saved per cell in an artifacts
directory.

Key features:
    - ``create_model_x_input``: Extracts selected feature columns from the
      input DataFrame and stores them as ``self.Xdata``.
    - ``pred_outlier_indices_from_proba``: Identifies indices of predicted
      outliers based on probability outputs and a decision threshold.
    - ``evaluate_indices``: Compares predicted outliers against benchmark
      labels and computes recall and precision scores.
    - ``create_2d_mesh_grid``: Builds a 2D mesh grid from the first two
      features of ``self.Xdata`` for plotting decision surfaces.
    - ``predict_anomaly_score_map``: Fits a PyOD model, visualizes anomaly
      probabilities with a decision boundary, highlights predicted outliers,
      and saves the resulting figure to the cell’s artifact directory.

.. code-block::

    from osbad.model import ModelRunner
"""
# Standard library
import logging
import os
import pathlib
import sys
from typing import Any, Callable, Dict, List, Literal, Tuple, Union

# Third-party libraries
import fireducks.pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib import rcParams
import pyod
from pyod.models.auto_encoder import AutoEncoder
from pyod.models.gmm import GMM
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from pyod.models.pca import PCA
from sklearn.metrics import precision_score, recall_score

rcParams["text.usetex"] = True

# Custom osbad library for anomaly detection
import osbad.config as bconf
import osbad.modval as modval
from osbad.config import CustomFormatter


SELECTED_FEATURE_COLS = ("log_max_diff_dQ", "log_max_diff_dV")

# Type alias for supported anomaly detection models ---------------------
PyODModelType = Union[
    pyod.models.iforest.IForest,
    pyod.models.knn.KNN,
    pyod.models.gmm.GMM,
    pyod.models.lof.LOF,
    pyod.models.pca.PCA,
    pyod.models.auto_encoder.AutoEncoder]
"""
Type alias for supported PyOD anomaly detection models.

This alias groups together the most commonly used PyOD estimators for
outlier detection. It allows functions and methods to accept any of
these model types without explicitly listing each one in the type
annotations.

Models included:
    - IForest (Isolation Forest)
    - KNN (k-Nearest Neighbors)
    - GMM (Gaussian Mixture Model)
    - LOF (Local Outlier Factor)
    - PCA (Principal Component Analysis for outliers)
    - AutoEncoder (Neural-network-based autoencoder for anomalies)

"""
class ModelRunner:
    def __init__(
        self,
        cell_label: str,
        df_input_features: pd.DataFrame,
        selected_feature_cols: Union[Tuple, List]):
        """
        Run anomaly-detection workflows for a single battery cell.

        This class organizes data preparation, model execution, evaluation,
        and figure export for a selected cell. It manages an artifacts
        directory per cell where generated plots are saved.

        Args:
            cell_label (str): Label identifying the evaluated cell.
            df_input_features (pd.DataFrame): Input feature dataset containing
                per-cycle metrics for the cell. Must include the columns
                required by ``SELECTED_FEATURE_COLS``.
            selected_feature_cols (Union[Tuple, List]): Names of columns used
                as model inputs.

        .. note::

            The input dataset is expected to contain the following feature
            columns:
                - max_diff_dQ
                - log_max_diff_dQ
                - cycle_index
                - max_diff_dV
                - log_max_diff_dV
                - cell_index

        """
        self._selected_cell_label = cell_label
        self.df_input_features = df_input_features
        self.selected_features = selected_feature_cols
        self._show_fig_status = bconf.SHOW_FIG_STATUS

        # create a new folder for each evaluated cell
        # store all figures output for each evaluated
        # cell into its corresponding folder
        self._selected_cell_artifacts = bconf.PIPELINE_OUTPUT_DIR.joinpath(
            self._selected_cell_label)
        if not os.path.exists(self._selected_cell_artifacts):
            os.mkdir(self._selected_cell_artifacts)

    def create_model_x_input(
        self):
        """
        Extract selected feature columns as a NumPy array.

        This method selects the feature columns specified in
        ``self.selected_features`` from the input DataFrame
        ``self.df_input_features``. The values are converted into a NumPy
        array and stored in ``self.Xdata`` for downstream model training and
        visualization.

        Args:
            None

        Returns:
            np.ndarray: Array of shape (n_samples, n_features) containing the
            selected feature values.

        .. code-block::

            selected_feature_cols = (
                "log_max_diff_dQ",
                "log_max_diff_dV")

            runner = ModelRunner(
                cell_label=selected_cell_label,
                df_input_features=df_features_per_cell,
                selected_feature_cols=selected_feature_cols
            )

            Xdata = runner.create_model_x_input()
        """

        self.Xdata = (
            self.df_input_features.loc[:, self.selected_features].values)

        return self.Xdata

    def pred_outlier_indices_from_proba(
        self,
        proba: np.ndarray,
        threshold: float,
        outlier_col: int = 1) -> np.ndarray:
        """
        Identify outlier sample indices from probability predictions.

        In PyOD, probability output has shape (n_samples, 2), where:

        - column 0 = inlier probability
        - column 1 = outlier probability

        This function selects all indices where the outlier probability is
        greater than or equal to the given threshold.

        Args:
            proba (np.ndarray):
                Array of shape (n_samples, 2) with predicted probabilities.
            threshold (float):
                Probability threshold above which a sample is flagged
                as outlier.
            outlier_col (int, optional):
                Column index for outlier probability. Defaults to 1.

        Returns:
            np.ndarray:
                Array of indices for samples classified as outliers.
        """
        outlier_prob = proba[:, outlier_col]

        # outliers indices that are non-zero in the flattened version
        # example output anomalous cycle = array([  0,  40, 147, 148])
        pred_outlier_indices = np.flatnonzero(outlier_prob >= threshold)

        # probability outlier score
        # example output score = array(
        #   [0.9366292 , 0.97598594, 0.99033612, 1.  ])
        pred_outlier_score = outlier_prob[pred_outlier_indices]

        return (pred_outlier_indices, pred_outlier_score)

    def evaluate_indices(
        self,
        df_benchmark_dataset: pd.DataFrame,
        pred_indices: np.ndarray) -> Tuple[float, float]:
        """
        Evaluate predicted outlier indices against benchmark labels.

        Uses ``modval.evaluate_pred_outliers`` to align predicted outlier
        indices with the benchmark dataset. The resulting DataFrame is
        expected to contain the columns ``true_outlier`` and
        ``pred_outlier``. Recall and precision are then computed from
        these columns.

        Args:
            df_benchmark_dataset (pd.DataFrame):
                Benchmark dataset containing ground-truth outlier labels.
            pred_indices (np.ndarray):
                Indices of predicted outliers from the model.

        Returns:
            Tuple[float, float]:
                - recall: Fraction of true outliers correctly identified.
                - precision: Fraction of predicted outliers that are true.

        .. note::

            Both recall and precision use ``zero_division=0``. This means
            that if there is a zero division, for example when the denominator
            is zero (TP + FP = 0 for precision) or (TP + FN = 0 for recall),
            the calculated ``recall_score`` or ``precision_score``
            will be zero.
        """
        # Expect modval.evaluate_pred_outliers to return columns
        # 'true_outlier', 'pred_outlier'
        df_eval = modval.evaluate_pred_outliers(
            df_benchmark=df_benchmark_dataset,
            outlier_cycle_index=pred_indices
        )
        y_true = df_eval["true_outlier"].to_numpy()
        y_pred = df_eval["pred_outlier"].to_numpy()

        recall = recall_score(y_true, y_pred, zero_division=0)
        precision = precision_score(y_true, y_pred, zero_division=0)
        return recall, precision


    def create_2d_mesh_grid(
        self):
        """
        Create a 2D mesh grid for visualization of anomaly scores.

        This function generates a square mesh grid covering the range of the
        first two features in ``self.Xdata``. The grid is expanded by ±1 unit
        beyond the min and max values to ensure full coverage. The resulting
        grid can be used for plotting decision boundaries and anomaly score
        heatmaps.

        Args:
            None

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]:
                - xx (np.ndarray): 2D array of x-coordinates.
                - yy (np.ndarray): 2D array of y-coordinates.
                - meshgrid (np.ndarray): Flattened 2D grid of shape
                  (n_points, 2) where each row is a (x, y) coordinate pair.

        """

        # Define the boundaries of the grid
        # Extend the grid boundaries by -1 and +1 to
        # ensure full coverage
        min_xrange = np.min(self.Xdata[:,0]) - 1
        max_xrange = np.max(self.Xdata[:,0]) + 1
        min_yrange = np.min(self.Xdata[:,1]) - 1
        max_yrange = np.max(self.Xdata[:,1]) + 1

        min_ax = np.min([min_xrange, min_yrange])
        max_ax = np.max([max_xrange, max_yrange])

        # Create a linearly spaced square xgrid and ygrid
        # using the min and max values from xdata and ydata
        xgrid = np.linspace(min_ax, max_ax, 100)
        ygrid = np.linspace(min_ax, max_ax, 100)


        # Create 2D meshgrid
        xx, yy = np.meshgrid(
            xgrid,
            ygrid)
        # print(f"xx shape: {xx.shape}")
        # print(f"yy shape: {yy.shape}")
        # print("*"*100)

        # flatten each grid to a vector
        r1, r2 = xx.flatten(), yy.flatten()

        # reshape the vector
        r1, r2 = (
            r1.reshape(len(r1),1),
            r2.reshape(len(r2),1))

        # stack each vector into a grid
        # the first column corresponds to x-axis
        # the second column corresponds to y-axis
        meshgrid = np.hstack((r1, r2))

        return (xx, yy, meshgrid)

    def predict_anomaly_score_map(
        self,
        selected_model: PyODModelType,
        model_name: str,
        xoutliers: pd.Series,
        youtliers: pd.Series,
        pred_outliers_index: np.ndarray,
        threshold: float= 0.7):
        """
        Plot a 2D anomaly score map with decision boundaries.

        This function fits the selected PyOD model to the dataset and
        visualizes the predicted anomaly scores across a 2D mesh grid.
        It creates a contour plot showing anomaly probabilities, a dashed
        decision boundary at the specified threshold, and highlights the
        predicted anomalous cycles. Annotations and a legend are added to
        label outliers, and the figure is saved in the artifacts directory.

        Args:
            selected_model (PyODModelType):
                Trained PyOD model used to predict anomaly scores.
            model_name (str): Name of the model, used as the plot title and
                in the output filename.
            xoutliers (pd.Series): x-coordinates of predicted anomalous
                samples.
            youtliers (pd.Series): y-coordinates of predicted anomalous
                samples.
            pred_outliers_index (np.ndarray): Indices of the predicted
                anomalous samples.
            threshold (np.float64, optional): Probability threshold for the
                anomaly decision boundary. Defaults to 0.7.

        Returns:
            matplotlib.axes.Axes: Axes object containing the anomaly score
            contour plot.

        .. code-block::

            axplot = runner.predict_anomaly_score_map(
                selected_model=model,
                model_name="Isolation Forest",
                xoutliers=df_outliers_pred["log_max_diff_dQ"],
                youtliers=df_outliers_pred["log_max_diff_dV"],
                pred_outliers_index=pred_outlier_indices,
                threshold=param_dict["threshold"]
            )

        .. note::

            Currently supported PyOD models in this benchmarking study are:
                * ``pyod.models.iforest.IForest``
                * ``pyod.models.knn.KNN``
                * ``pyod.models.gmm.GMM``
                * ``pyod.models.lof.LOF``
                * ``pyod.models.pca.PCA``
                * ``pyod.models.auto_encoder.Autoencoder``
        """
        xx, yy, meshgrid = self.create_2d_mesh_grid()

        selected_colormap = cm.RdBu_r

        selected_model.fit(self.Xdata)

        # Predict the probability of the data point
        # on the grid being an outlier
        yhat_grid_score = selected_model.predict_proba(meshgrid)

        # We only want to plot the outlier probability
        yhat_grid_outlier = yhat_grid_score[:, 1]

        # Reshape yhat_grid_outlier into the
        # size of the grid
        zz_grid_outlier_score = yhat_grid_outlier.reshape(xx.shape)

        fig, ax = plt.subplots(figsize=(8,5))

        # Reset the sns settings
        mpl.rcParams.update(mpl.rcParamsDefault)
        rcParams["text.usetex"] = True

        # The contour plot using the model on the grid
        ax_contourplot = ax.contourf(
            xx,
            yy,
            zz_grid_outlier_score,
            cmap=selected_colormap,
            vmin=0,
            vmax=1)

        # Define the threshold for anomalies
        # Threshold: 70% of anomaly probabilities
        decision_boundary = ax.contour(
            xx,
            yy,
            zz_grid_outlier_score,
            levels=[threshold],
            linewidths=2,
            linestyles="dashed",
            colors='black')

        # Set the limits for the colorbar
        cbar_limit = plt.cm.ScalarMappable(cmap=selected_colormap)
        cbar_limit.set_array(zz_grid_outlier_score)
        cbar_limit.set_clim(0., 1.)

        cbar = fig.colorbar(cbar_limit, ax=ax, shrink=0.9)
        cbar.ax.set_ylabel(
            'Outliers probability',
            fontsize=14)

        # Scatterplot of all cycles
        ax.scatter(
            self.Xdata[:, 0],
            self.Xdata[:, 1],
            s=10,
            alpha=1,
            marker="o",
            c="black")

        # Scatterplot for predicted anomalies
        ax.scatter(
            xoutliers,
            youtliers,
            s=150,
            alpha=1,
            zorder=2,
            marker="*",
            c="gold")

        # -------------------------------------------------------------------
        # Text beside each flagged cycle to label the
        # anomalous cycle
        if len(pred_outliers_index) != 0:
            for cycle in pred_outliers_index:
                dQ_text_position = xoutliers.loc[cycle]
                dV_text_position = youtliers.loc[cycle]

                # print(f"Anomalous cycle: {cycle}")
                # print(f"dQ text position: {dQ_text_position}")
                # print(f"dV text position: {dV_text_position}")

                ax.text(
                    # x-position of the text
                    # Add an offset of 0.1 so that the text
                    # does not overlap with the outlier symbol
                    x = dQ_text_position + 0.1,
                    # y-position of the text
                    y = dV_text_position,
                    # text-string is the cycle number
                    s = cycle,
                    horizontalalignment='left',
                    size='medium',
                    color='white',
                    weight='bold')
                # print("*"*70)

            # Textbox for the legend to label anomalous cycles ---------------
            # properties for bbox
            props = dict(
                boxstyle='round',
                facecolor='white',
                alpha=0.8)

            # Create textbox to annotate anomalous cycle
            textstr = '\n'.join((
                r"\textbf{Predicted anomalous cycles:}",
                f"{str(pred_outliers_index)}"))

            # first text value corresponds to the left right
            # alignment starting from left
            # second second value corresponds to up down
            # alignment starting from bottom
            ax.text(
                0.75, 0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=12,
                # ha means right alignment of the text
                ha="center", va='top',
                bbox=props)

            # ----------------------------------------------------------------

            ax.set_xlabel(
                r"$\log(\Delta Q_\textrm{scaled,max,cyc)}\;\textrm{[Ah]}$",
                fontsize=12)
            ax.set_ylabel(
                r"$\log(\Delta V_\textrm{scaled,max,cyc})\;\textrm{[V]}$",
                fontsize=12)

            ax.set_title(model_name, fontsize=16)

            # convert model name to snake case
            # standardize all filename of the exported figures
            filename = model_name.replace(" ", "_").lower()

            output_fig_filename = (
                filename + "_"
                + self._selected_cell_label
                + ".png")

            fig_output_path = (
                self._selected_cell_artifacts.joinpath(output_fig_filename))

            plt.savefig(
                fig_output_path,
                dpi=200,
                bbox_inches="tight")

            if self._show_fig_status:
                plt.show()

        return ax