import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress

def truncated_power_law(x, a, b, c):
    """
    
    Truncated power-law function.

    Parameters
    ----------
    x : array-like
        Degree values.
    a : float
        Scaling factor.
    b : float
        Power-law exponent.
    c : float
        Cutoff parameter.

    Returns
    -------
    array-like
        Values computed from the truncated power-law formula: a * x^(-b) * exp(-x/c).
    """
    return a * np.power(x, -b) * np.exp(-x / c)

def r_squared(y_true, y_pred):
    """
    Compute the coefficient of determination (R²) between observed and predicted values.

    Parameters
    ----------
    y_true : array-like
        Observed data values.
    y_pred : array-like
        Fitted or predicted data values.

    Returns
    -------
    float
        R² value indicating the goodness of fit.
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)

def fit_truncated_power_law(degrees,
                             title="Truncated Power-Law Fit",
                             xlabel="Degree",
                             ylabel="Frequency",
                             show_plot=True,
                             figsize=(8, 6),
                             color_data="black",
                             color_fit="darkred"):
    """
    Fit a truncated power-law to a degree distribution and optionally plot the result.

    Parameters
    ----------
        degrees (array-like): Degree values (not yet counted).
        title (str): Title of the plot.
        xlabel (str): Label for x-axis.
        ylabel (str): Label for y-axis.
        show_plot (bool): Whether to display the plot.
        figsize (tuple): Size of the figure.
        color_data (str): Color for scatter data.
        color_fit (str): Color for the fitted curve.

    Returns:
        dict: Dictionary with fit parameters and R².
    """
    degrees = np.asarray(degrees)
    values, counts = np.unique(degrees, return_counts=True)

    # Fit
    popt, _ = curve_fit(truncated_power_law, values, counts, maxfev=10000)
    fit_values = truncated_power_law(values, *popt)
    r2 = r_squared(counts, fit_values)

    if show_plot:
        plt.figure(figsize=figsize)
        plt.scatter(values, counts, label="Data", color=color_data)
        plt.plot(values, fit_values, label=f"Fit (R² = {r2:.2f})", color=color_fit)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return {
        "parameters": {"a": popt[0], "b": popt[1], "c": popt[2]},
        "r_squared": r2,
        "x": values,
        "y": counts,
        "fit": fit_values
    }


def fit_strength_vs_degree(df_exporters, df_importers,
                           degree_col="Degree", strength_col="Strength",
                           figsize=(8, 5), show_plot=True):
    """
    Fit and plot strength vs. degree in log-log scale for exporters and importers.

    Parameters
    ----------
        df_exporters (pd.DataFrame): Exporters' degree and strength.
        df_importers (pd.DataFrame): Importers' degree and strength.
        degree_col (str): Column name for degree values.
        strength_col (str): Column name for strength values.
        figsize (tuple): Size of the plot.
        show_plot (bool): Whether to display the plot.

    Returns:
        dict: Dictionary containing slopes, intercepts, R² values, and fitted data.
    """
    def power_law_fit(degree_vals, strength_vals):
        mask = (degree_vals > 0) & (strength_vals > 0)
        degree_vals = degree_vals[mask]
        strength_vals = strength_vals[mask]

        log_degree = np.log10(degree_vals)
        log_strength = np.log10(strength_vals)

        slope, intercept, r_value, _, _ = linregress(log_degree, log_strength)

        sorted_indices = np.argsort(degree_vals)
        degree_sorted = degree_vals[sorted_indices]
        fit_strength = 10 ** intercept * degree_sorted ** slope

        return slope, intercept, r_value**2, degree_sorted, fit_strength

    # Ajustes
    slope_exp, intercept_exp, r2_exp, deg_exp, fit_exp = power_law_fit(
        df_exporters[degree_col].values,
        df_exporters[strength_col].values)

    slope_imp, intercept_imp, r2_imp, deg_imp, fit_imp = power_law_fit(
        df_importers[degree_col].values,
        df_importers[strength_col].values)

    if show_plot:
        plt.figure(figsize=figsize)
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Degree (Number of Connections)')
        plt.ylabel('Strength (Sum of Weights)')
        plt.title('Power-law Fit: Strength vs Degree')
        plt.grid(True)

        # Puntos
        plt.scatter(df_exporters[degree_col], df_exporters[strength_col], 
                    alpha=0.7, color='blue', label=f'Exporters (α={slope_exp:.2f})')
        plt.scatter(df_importers[degree_col], df_importers[strength_col],
                    alpha=0.7, color='orange', label=f'Importers (α={slope_imp:.2f})')

        # Líneas de ajuste
        plt.plot(deg_exp, fit_exp, color='blue', linestyle='dashed')
        plt.plot(deg_imp, fit_imp, color='orange', linestyle='dashed')
        
        plt.legend()
        plt.tight_layout()
        plt.show()

    return {
        "exporters": {
            "slope": slope_exp,
            "intercept": intercept_exp,
            "r_squared": r2_exp,
            "x": deg_exp,
            "fit": fit_exp
        },
        "importers": {
            "slope": slope_imp,
            "intercept": intercept_imp,
            "r_squared": r2_imp,
            "x": deg_imp,
            "fit": fit_imp
        }
    }