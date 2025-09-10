import base64
import io

import matplotlib.pyplot as plt
import numpy as np
from celery import Task, shared_task
from celery.exceptions import SoftTimeLimitExceeded

from aidrin.file_handling.file_parser import read_file


@shared_task(bind=True, ignore_result=False)
def calculate_outliers(
    self: Task,
    file_info: dict,
    generate_vis: bool = True,
):
    """
    Detects outliers in numerical columns using the IQR method and optionally
    returns a matplotlib figure showing outlier proportions.

    Args:
        self (Task): Celery task instance (bound method).
        file_info (dict): Information to read the dataset.
        generate_vis (bool): If True, generate a matplotlib visualization.

    Returns:
        dict: {
            'Outlier scores': dict,
            'Outliers Visualization': matplotlib.figure.Figure (if generate_vis=True),
        }
    """
    try:
        df = read_file(file_info)

        numerical_columns = df.select_dtypes(include=[np.number])
        if numerical_columns.empty:
            return {"Error": "No numerical columns found in the dataset."}

        numerical_columns_dropna = numerical_columns.dropna()

        q1 = numerical_columns_dropna.quantile(0.25)
        q3 = numerical_columns_dropna.quantile(0.75)
        iqr = q3 - q1

        outliers = numerical_columns_dropna[
            (numerical_columns_dropna < (q1 - 1.5 * iqr))
            | (numerical_columns_dropna > (q3 + 1.5 * iqr))
        ]

        proportions = outliers.notna().mean()
        proportions_dict = proportions.to_dict()

        average_value = (
            sum(proportions_dict.values()) / len(proportions_dict)
            if proportions_dict
            else 0
        )
        proportions_dict["Overall outlier score"] = average_value

        result = {"Outlier scores": proportions_dict}

        if generate_vis:
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.bar(proportions_dict.keys(), proportions_dict.values(), color="red")
            ax.set_title("Proportion of Outliers for Numerical Columns", fontsize=14)
            ax.set_xlabel("Columns", fontsize=14)
            ax.set_ylabel("Proportion of Outliers", fontsize=14)
            plt.xticks(rotation=45, ha="right", fontsize=12)
            plt.subplots_adjust(bottom=0.5)
            plt.tight_layout()
            plt.show()

            result["Outliers Visualization"] = fig
            plt.close(fig)

        return result

    except SoftTimeLimitExceeded:
        raise Exception("Outliers task timed out.")
    except Exception as e:
        return {"Error": f"Error detecting outliers: {str(e)}"}
