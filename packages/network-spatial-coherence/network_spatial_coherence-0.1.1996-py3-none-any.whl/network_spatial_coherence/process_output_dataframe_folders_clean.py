import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
from structure_and_args import GraphArgs
from sklearn.linear_model import LinearRegression
import scienceplots

# Constants
C_BAR_LIMITS = {
    "network_dim": (0.5, 3.5),
    "gram_total_contribution": (0.3, 1),
    "gram_spectral_gap": (0, 1),
    "gram_last_spectral_gap": (0, 1),
    "largeworldness": (0, 1),
}

LABEL_MAPPINGS = {
    "network_dim": "Network Dimension",
    "gram_total_contribution": "Variance Contribution",
    "gram_spectral_gap": "Spectral Gap (mean)",
    "gram_last_spectral_gap": "Spectral Gap",
    "largeworldness": "Large Worldness",
    "false_edges_ratio": "False Edges Ratio",
    "false_edges_count": "Number of False Edges",
    "Quantile": "Filtering Power",
    "False Edge Ratio": "False Edges Ratio",
    "true_edges_deletion_ratio": "Missing Edges Ratio",
    "intended_av_degree": r"$\langle k \rangle$",

    "epsilon-ball": r"$\epsilon$-ball",
    "epsilon_bipartite": r"$\epsilon$-ball Bipartite",
    "knn": r"KNN",
    "knn_bipartite": r"KNN Bipartite",
    "delaunay_corrected": "Delaunay",

    "num_points": "N",
    "average_false_edge_length": "Average False Edge Length",

    "elapsed_time": "Time (s)",

}

COLORMAP_STYLES = {
    "network_dim": "Spectral_r",
    "gram_total_contribution": "magma",
    "gram_spectral_gap": "magma",
    "gram_last_spectral_gap": "magma",
}

BINNING_MAP = {
    'average_false_edge_length': 3,  # Bin 'parameter_x' into quartiles
}

def setup_plot_style():
    plt.style.use(['science', 'no-latex', 'nature'])
    base_figsize = (6, 4.5)
    base_fontsize = 18
    plt.rcParams.update({
        'figure.figsize': base_figsize,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'font.size': base_fontsize,
        'axes.labelsize': base_fontsize,
        'axes.titlesize': base_fontsize + 2,
        'xtick.labelsize': base_fontsize,
        'ytick.labelsize': base_fontsize,
        'legend.fontsize': base_fontsize - 6,
        'lines.linewidth': 2,
        'lines.markersize': 6,
        'figure.autolayout': True,
        'text.usetex': False,
    })


def add_dimension_to_data(df):
    # Extract dimensions
    dimension_series = df[df['Property'] == 'dim']['Value'].reset_index(drop=True)
    # Assuming the same dimension applies to all entries in a single DataFrame (common in batch processed files)
    if not dimension_series.empty:
        df['dimension'] = dimension_series.iloc[0]
    else:
        df['dimension'] = 'Unknown'  # Handling cases where no dimension data is present
    return df
def load_and_process_data(folder_path: str, parameter_x: str, parameter_y: str, quantity_to_evaluate: str,
                          omit_df_with_parameters, split_by_dim=False):
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    data_dict = {}

    for file in all_files:
        df = pd.read_csv(file)
        if should_omit_file(df, omit_df_with_parameters):
            continue

        if parameter_x == "Total_Mode":
            df = append_total_mode(df)

        filtered_df = filter_data(df, parameter_x, parameter_y, quantity_to_evaluate)
        pivoted = pivot_data(filtered_df)

        if split_by_dim:
            # Assuming 'dim' is now properly retained in filtered_df
            for dim in pivoted['dimension'].unique():
                if dim not in data_dict:
                    data_dict[dim] = pd.DataFrame()
                dim_data = pivoted[pivoted['dimension'] == dim]
                data_dict[dim] = pd.concat([data_dict[dim], dim_data], ignore_index=True)
        else:
            combined_key = 'combined'
            if combined_key not in data_dict:
                data_dict[combined_key] = pd.DataFrame()
            data_dict[combined_key] = pd.concat([data_dict[combined_key], pivoted], ignore_index=True)

    return data_dict


def should_omit_file(df: pd.DataFrame, omit_df_with_parameters) -> bool:
    for key, value in omit_df_with_parameters.items():
        if key in df['Property'].values and df.loc[df['Property'] == key, 'Value'].iloc[0] == value:
            return True
    return False


def append_total_mode(df: pd.DataFrame) -> pd.DataFrame:
    modes = df[df['Property'].isin(['dim', 'proximity_mode', 'bipartiteness'])]
    modes = modes.set_index('Property')['Value'].to_dict()
    total_mode = f"{modes.get('proximity_mode', '')}_{modes.get('dim', '')}_{modes.get('bipartiteness', '')}"
    total_mode_row = pd.DataFrame({'Property': ['Total_Mode'], 'Value': [total_mode], 'Category': ['Parameter']})
    return pd.concat([df, total_mode_row], ignore_index=True)


def filter_data(df: pd.DataFrame, parameter_x: str, parameter_y: str, quantity_to_evaluate: str) -> pd.DataFrame:
    properties = [parameter_y, quantity_to_evaluate, parameter_x, 'dimension']
    filtered_df = df[df['Property'].isin(properties)]
    if 'Category' in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=['Category'])
    filtered_df = filtered_df.drop_duplicates()

    return filtered_df


def pivot_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.set_index('Property').T

def reformat_total_mode(total_mode):
    parts = total_mode.split('_')
    proximity_mode = parts[0]
    dimension = parts[1]
    bipartitedness = "bipartite" if parts[2] == "True" else "unipartite"

    # Special handling for modes where bipartiteness is implied in the name
    if "bipartite" in proximity_mode:
        return f"{proximity_mode} {dimension}"
    else:
        return f"{proximity_mode} {dimension} {bipartitedness}"


def bin_for_continuous_quantities(data, parameter):
    if parameter in BINNING_MAP and BINNING_MAP[parameter] > 0:
        # Create quantile bins and retrieve bin edges
        data[f'{parameter}_binned'], bins = pd.qcut(data[parameter], q=BINNING_MAP[parameter], duplicates='drop', retbins=True)

        # Generate human-readable labels for the bins
        labels = [f"{np.round(bins[i], 2)} - {np.round(bins[i+1], 2)}" for i in range(len(bins)-1)]

        # Update categories in the existing Categorical object
        data[f'{parameter}_binned'] = data[f'{parameter}_binned'].cat.rename_categories(labels)

        print(data[f'{parameter}_binned'])

        return f'{parameter}_binned'
    return parameter

def format_label(label):
    try:
        # Attempt to convert label to a float and then conditionally to an integer if applicable
        num = float(label)
        if num.is_integer():
            return str(int(num))  # Convert to integer and then to string if no decimal part
        else:
            return str(round(num, 2))  # Keep as float but round to 2 decimal places
    except ValueError:
        # If conversion to float fails, return the label as is
        return label

def set_formatted_ticklabels(ax, labels, axis='x'):
    # Format labels with conditional integer formatting
    formatted_labels = [format_label(label) for label in labels]

    # Apply formatted labels to the appropriate axis
    if axis == 'x':
        ax.set_xticklabels(formatted_labels)
    elif axis == 'y':
        ax.set_yticklabels(formatted_labels)

def update_heatmap_labels(ax):
    # Retrieve current tick labels from both axes
    x_labels = [item.get_text() for item in ax.get_xticklabels()]
    y_labels = [item.get_text() for item in ax.get_yticklabels()]

    # Format and set x-axis labels
    set_formatted_ticklabels(ax, x_labels, 'x')
    # Format and set y-axis labels
    set_formatted_ticklabels(ax, y_labels, 'y')
def create_heatmap(data: pd.DataFrame, parameter_x: str, parameter_y: str, quantity_to_evaluate: str,
                   output_folder: str, suffix=''):
    # Helper function to check if the input is a DataFrame and convert to Series if needed
    def ensure_series(data, column_name):
        if isinstance(data[column_name], pd.DataFrame):
            print(f"Warning: '{column_name}' is a DataFrame, not a Series. Using the first column.")
            return data[column_name].iloc[:, 0]
        return data[column_name]

    # Helper function to handle non-numeric series and convert to categorical if not numeric
    def ensure_numeric_or_categorical(series):
        print(f"Data type of '{series.name}': {series.dtype}")  # Check the data type
        if not pd.api.types.is_numeric_dtype(series):
            try:
                series = pd.to_numeric(series)  # Try converting to numeric
                print(f"Converted '{series.name}' to numeric.")
            except ValueError:
                print(f"Info: '{series.name}' is non-numeric. Converting to categorical codes for heatmap.")
                # return series.astype('category').cat.codes
        return series

    # Ensure the parameters are handled as Series
    data[parameter_x] = ensure_series(data, parameter_x)
    data[parameter_y] = ensure_series(data, parameter_y)

    # Convert parameters to numeric if necessary
    data[parameter_x] = ensure_numeric_or_categorical(data[parameter_x])
    data[parameter_y] = ensure_numeric_or_categorical(data[parameter_y])
    data[quantity_to_evaluate] = ensure_numeric_or_categorical(data[quantity_to_evaluate])

    # Bin quantities that are not discrete
    param_x = bin_for_continuous_quantities(data, parameter_x)
    param_y = bin_for_continuous_quantities(data, parameter_y)


    print(data[parameter_x])

    # Pivot the data for the heatmap
    heatmap_data = data.pivot_table(index=param_y, columns=param_x, values=quantity_to_evaluate, aggfunc='mean')
    heatmap_data = heatmap_data.sort_index(ascending=False)

    # Set up the heatmap plot
    plt.figure(figsize=(10, 8))
    colorbar_min, colorbar_max = C_BAR_LIMITS.get(quantity_to_evaluate,
                                                  (heatmap_data.min().min(), heatmap_data.max().max()))


    ax = sns.heatmap(heatmap_data, annot=True, cmap=COLORMAP_STYLES.get(quantity_to_evaluate, 'viridis'), fmt=".2f",
                cbar_kws={'label': LABEL_MAPPINGS.get(quantity_to_evaluate)},
                vmin=colorbar_min, vmax=colorbar_max, linewidths=2, linecolor='white')



    plt.xlabel(LABEL_MAPPINGS.get(parameter_x))
    plt.ylabel(LABEL_MAPPINGS.get(parameter_y))

    update_heatmap_labels(ax)

    if suffix != '':
        if suffix == "_dimension_2":
            suffix = "2D"
        elif suffix == "_dimension_3":
            suffix = "3D"
        plt.title(f"{suffix}")
    # plt.title(f"Heatmap of {quantity_to_evaluate} by {parameter_x} and {parameter_y}")

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Save the plot
    plt_path = f"{output_folder}/heatmap_{quantity_to_evaluate}_by_{parameter_x}_and_{parameter_y}{suffix}_{current_time}.pdf"
    plt.savefig(plt_path)
    plt.close()
    print(f"Heatmap saved to {plt_path}")

    # Save the heatmap data to a CSV
    filename = f"{plot_folder}/heatmap_data_{quantity_to_evaluate}_by_{parameter_x}_and_{parameter_y}{suffix}_{current_time}.csv"
    heatmap_data.to_csv(filename)


def create_2d_plot(data: pd.DataFrame, parameter_x: str, quantity_to_evaluate: str, output_folder: str, linear_fit: bool = False, log_scale: bool = False):
    if pd.api.types.is_categorical_dtype(data[parameter_x]) or data[parameter_x].dtype == 'object':
        # Use barplot if parameter_x is categorical
        create_2d_barplot(data, parameter_x, quantity_to_evaluate, output_folder)
    else:

        if parameter_x == 'Total_Mode':
            data[parameter_x] = data[parameter_x].apply(reformat_total_mode)

        data = data.astype({parameter_x: 'float', quantity_to_evaluate: 'float'})

        plt.figure(figsize=(10, 6))

        if log_scale:
            plt.xscale('log')
            plt.yscale('log')

        sns.scatterplot(data=data, x=parameter_x, y=quantity_to_evaluate, s=100, color='blue', edgecolor='w', alpha=0.6)

        if linear_fit:
            if log_scale:
                # Perform linear fit on log-transformed data
                log_x = np.log10(data[parameter_x].values.reshape(-1, 1))
                log_y = np.log10(data[quantity_to_evaluate].values.reshape(-1, 1))
                model = LinearRegression().fit(log_x, log_y)
                pred_y = model.predict(log_x)
                plt.plot(data[parameter_x], 10**pred_y, color='red', linestyle='--', linewidth=2, label='Linear Fit')

                # Calculate slope and intercept for the equation
                slope = model.coef_[0][0]
                intercept = model.intercept_[0]

                if intercept < 0:
                    equation_text = f"y = {slope:.2f}x {intercept:.2f}"
                else:
                    equation_text = f"y = {slope:.2f}x + {intercept:.2f}"
            else:
                # Perform linear fit on original data
                x = data[parameter_x].values.reshape(-1, 1)
                y = data[quantity_to_evaluate].values.reshape(-1, 1)
                model = LinearRegression().fit(x, y)
                pred_y = model.predict(x)
                plt.plot(data[parameter_x], pred_y, color='red', linestyle='--', linewidth=2, label='Linear Fit')

                # Calculate slope and intercept for the equation
                slope = model.coef_[0][0]
                intercept = model.intercept_[0]
                if slope < 0:
                    equation_text = f"y = {intercept:.2f} {slope:.2f} * x"
                else:
                    equation_text = f"y = {intercept:.2f} + {slope:.2f} * x"

            # Annotate the equation on the plot
            plt.annotate(equation_text, xy=(0.95, 0.95), xycoords='axes fraction', fontsize=12,
                         horizontalalignment='left', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.6))

            plt.legend()

        plt.title(f'Scatter Plot of {quantity_to_evaluate} by {parameter_x}')
        plt.xlabel(LABEL_MAPPINGS.get(parameter_x))
        plt.ylabel(LABEL_MAPPINGS.get(quantity_to_evaluate))
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)

        save_plot(output_folder, f"scatter_{quantity_to_evaluate}_by_{parameter_x}")


def create_2d_barplot(data: pd.DataFrame, parameter_x: str, quantity_to_evaluate: str, output_folder: str, aggfunc: str = 'mean'):
    plt.figure(figsize=(10, 6))

    # Aggregate the data based on the specified aggregation function
    aggregated_data = data.groupby(parameter_x)[quantity_to_evaluate].agg(aggfunc).reset_index()

    # Create the bar plot
    sns.barplot(data=aggregated_data, x=parameter_x, y=quantity_to_evaluate, color='#009ADE')


    plt.xlabel(LABEL_MAPPINGS.get(parameter_x))
    plt.ylabel(LABEL_MAPPINGS.get(quantity_to_evaluate))

    # Check if rotation is necessary for x-axis labels
    plt.xticks(rotation=0)
    plt.draw()  # Draw the plot to get the dimensions of the x-axis labels
    # Check if the labels are too wide to fit without overlap
    labels = plt.gca().get_xticklabels()
    if any(label.get_window_extent().width > plt.gca().get_xbound()[1] / len(labels) for label in labels):
        plt.xticks(rotation=45, ha='right')  # Rotate the labels if they overlap

    # Save the plot
    save_plot(output_folder, f"barplot_{quantity_to_evaluate}_by_{parameter_x}_{aggfunc}")


def create_violin_plot(data: pd.DataFrame, quantity_to_evaluate: str, output_folder: str):
    data[quantity_to_evaluate] = pd.to_numeric(data[quantity_to_evaluate], errors='coerce')

    sns.violinplot(data=data, y=quantity_to_evaluate)
    plt.ylabel(LABEL_MAPPINGS[quantity_to_evaluate])

    save_plot(output_folder, f"violin_plot_{quantity_to_evaluate}")


def save_plot(output_folder: str, filename: str):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    full_filename = f"{output_folder}/{filename}_{current_time}"
    plt.savefig(full_filename + '.svg')
    plt.savefig(full_filename + '.pdf')
    plt.close()


def main(folder_path: str, parameter_x: str, parameter_y: str, quantity_to_evaluate: str,
         plot_type: str, output_folder: str, omit_df_with_parameters={}, split_by_dim=False):
    setup_plot_style()

    # Load data and optionally split by 'dim'
    data_dict = load_and_process_data(folder_path, parameter_x, parameter_y, quantity_to_evaluate,
                                      omit_df_with_parameters, split_by_dim)

    if quantity_to_evaluate == "elapsed_time":
        lin_fit = True
        log_scale = True
    else:
        lin_fit = False
        log_scale = False

    if split_by_dim:
        # Process each split data separately
        for dim, data in data_dict.items():
            suffix = f"_dimension_{dim}"
            if plot_type == 'heatmap':
                create_heatmap(data, parameter_x, parameter_y, quantity_to_evaluate, output_folder, suffix=suffix)
            elif plot_type == '2d':
                create_2d_plot(data, parameter_x, quantity_to_evaluate, output_folder, suffix=suffix)
            elif plot_type == 'violin':
                create_violin_plot(data, quantity_to_evaluate, output_folder, suffix=suffix)
            else:
                raise ValueError(f"Unknown plot type: {plot_type}")
    else:
        # Use the 'combined' data for a single, unified plot
        combined_data = data_dict.get('combined', pd.DataFrame())
        if plot_type == 'heatmap':
            create_heatmap(combined_data, parameter_x, parameter_y, quantity_to_evaluate, output_folder)
        elif plot_type == '2d':
            create_2d_plot(combined_data, parameter_x, quantity_to_evaluate, output_folder,
                           linear_fit=lin_fit, log_scale=log_scale)
        elif plot_type == 'violin':
            create_violin_plot(combined_data, quantity_to_evaluate, output_folder)
        else:
            raise ValueError(f"Unknown plot type: {plot_type}")


if __name__ == "__main__":
    # Example usage
    args = GraphArgs()
    dataframe_folder = args.directory_map['output_dataframe']
    plot_folder = args.directory_map['dataframes']



    # # For num node dependence with proximity graph: parameter_x = proximity_mode, parameter_y = num_points
    # folder_path = "/home/david/PycharmProjects/Spatial_Constant_Analysis/results/output_dataframe/20240813_170347_proximity_mode_intended_av_degree_dim_num_points_10000/"

    # For dependence with false edge length: parameter_x = average_false_edge_length, parameter_y = false_edges_count
    folder_path = "/home/david/PycharmProjects/Spatial_Constant_Analysis/results/output_dataframe/20240814_132203_proximity_mode_intended_av_degree_dim_num_points_max_false_edge_length_false_edges_count/"

    # For computational complexity
    folder_path = "/home/david/PycharmProjects/Spatial_Constant_Analysis/results/output_dataframe/20240814_151543_proximity_mode_num_points/"

    # For different point modes (shapes)
    folder_path = "/home/david/PycharmProjects/Spatial_Constant_Analysis/results/output_dataframe/20240814_170454_point_mode/"

    # For density anomalies and point modes
    folder_path = "/home/david/PycharmProjects/Spatial_Constant_Analysis/results/output_dataframe/20240815_112503_point_mode/"

    parameter_x = "point_mode"
    parameter_y = "false_edges_count"
    quantity_to_evaluate = "gram_total_contribution"   #network_dim, gram_total_contribution, elapsed_time, gram_last_spectral_gap
    split_by_dim = False
    plot_type = "2d"  # heatmap, 2d, violin
    output_folder = plot_folder
    omit_df_with_parameters = {'Filtered': False}
    main(folder_path, parameter_x, parameter_y, quantity_to_evaluate, plot_type, output_folder, omit_df_with_parameters,
         split_by_dim=split_by_dim)