import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


def setup_classification_plot(
    x,
    y,
    cmap: ListedColormap,
    title,
    x_label,
    y_label,
    meshgrid=None,
    feature_scale=None,
    predict=None,
):
    """
    Sets up a classification plot with decision boundaries and classified regions.

    This function creates a visualization of a classification model's decision boundaries
    and the resulting classified regions. It plots the training data points colored by their
    class and overlays the decision boundaries of the classifier.

    Args:
        x: Feature data, typically a 2D array where each row is a sample and each column is a feature.
        y: Target data, typically a 1D array of class labels.
        cmap (ListedColormap): Colormap for visualizing different classes.
        title (str): Title for the plot.
        x_label (str): Label for the x-axis.
        y_label (str): Label for the y-axis.
        meshgrid (dict[int, dict[str, float]]): Controls the np.meshgrid arange parameters for each axis.
            Provide a dict with two entries indexed by 0 and 1 (x-axis and y-axis respectively),
            where each entry is a dict with keys:
            - "min": float padding to subtract from the min value for the start of the range
            - "max": float padding to add to the max value for the end of the range
            - "step": float step size between values in the range
            Example: {0: {"min": 10, "max": 10, "step": 0.25}, 1: {"min": 1000, "max": 1000, "step": 0.25}}
        feature_scale (callable): Function to transform the feature data for visualization.
            Should take x and y as input and return the transformed x and y.
            If None, no transformation is applied.
        predict (callable): Function to predict class labels for the mesh grid points.
            Should take x1 and x2 (mesh grid coordinates) as input and return predicted classes.

    Returns:
        bool: True if the plot was successfully created.

    Example:
        >>> setup_classification_plot(
        ...     x=x_train,
        ...     y=y_train,
        ...     cmap=ListedColormap(("salmon", "dodgerblue")),
        ...     title="Logistic Regression",
        ...     x_label="Feature 1",
        ...     y_label="Feature 2",
        ...     meshgrid={0: {"min": 10, "max": 10, "step": 0.25}, 1: {"min": 1000, "max": 1000, "step": 0.25}},
        ...     feature_scale=lambda x_set, y_set: (x_set, y_set),
        ...     predict=lambda x1, x2: classifier.predict(np.array([x1.ravel(), x2.ravel()]).T).reshape(x1.shape)
        ... )
    """
    if meshgrid is None:
        meshgrid = {
            0: {"min": 10, "max": 10, "step": 0.25},
            1: {"min": 1000, "max": 1000, "step": 0.25},
        }
    if feature_scale is not None:
        x_set, y_set = feature_scale(x, y)
    else:
        x_set, y_set = x, y
    x1, x2 = np.meshgrid(
        np.arange(
            start=x_set[:, 0].min() - meshgrid[0]["min"],
            stop=x_set[:, 0].max() + meshgrid[0]["max"],
            step=meshgrid[0]["step"],
        ),
        np.arange(
            start=x_set[:, 1].min() - meshgrid[1]["min"],
            stop=x_set[:, 1].max() + meshgrid[1]["max"],
            step=meshgrid[1]["step"],
        ),
    )
    y_pred = predict(x1, x2)
    plt.contourf(x1, x2, y_pred, alpha=0.75, cmap=cmap)
    plt.contour(x1, x2, y_pred, colors="black", alpha=0.5, linewidths=0.5)
    plt.xlim(x1.min(), x1.max())
    plt.ylim(x2.min(), x2.max())
    for i, j in enumerate(np.unique(y_set)):
        plt.scatter(
            x_set[y_set == j, 0], x_set[y_set == j, 1], c=cmap.colors[i], label=j
        )
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    return True
