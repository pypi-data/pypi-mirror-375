import os.path

import numpy as np
import matplotlib.pyplot as plt
from structure_and_args import GraphArgs
from create_proximity_graph import write_proximity_graph
from utils import load_graph
from data_analysis import run_simulation_subgraph_sampling_by_bfs_depth, run_spatial_constant_continuous
import matplotlib.colors as mcolors
import pandas as pd
from algorithms import compute_shortest_path_matrix_sparse_graph, select_false_edges_csr
from gram_matrix_analysis import plot_gram_matrix_eigenvalues
from utils import add_specific_random_edges_to_csrgraph, write_edge_list_sparse_graph
from plots import save_plotting_data
from check_latex_installation import check_latex_installed
from dimension_prediction import run_dimension_prediction, run_dimension_prediction_continuous
from gram_matrix_analysis import compute_gram_matrix_eigenvalues
import copy
import random
import matplotlib
import matplotlib.patches as mpatches
import warnings
matplotlib.use('Agg')  # Use a non-GUI backend, it was throwing errors otherwise when running the experimental setting

# is_latex_in_os = check_latex_installed()
# if is_latex_in_os:
#     plt.style.use(['nature'])
# else:
#     plt.style.use(['no-latex', 'nature'])
# plt.style.use(['no-latex', 'nature'])
# font_size = 24
# plt.rcParams.update({'font.size': font_size})
# plt.rcParams['axes.labelsize'] = font_size
# plt.rcParams['axes.titlesize'] = font_size + 6
# plt.rcParams['xtick.labelsize'] = font_size
# plt.rcParams['ytick.labelsize'] = font_size
# plt.rcParams['legend.fontsize'] = font_size - 10

is_latex_in_os = check_latex_installed()
if is_latex_in_os:
    plt.style.use(['nature'])
else:
    plt.style.use(['no-latex', 'nature'])
plt.style.use(['no-latex', 'nature'])
# font_size = 24
# plt.rcParams.update({'font.size': font_size})
# plt.rcParams['axes.labelsize'] = font_size
# plt.rcParams['axes.titlesize'] = font_size + 6
# plt.rcParams['xtick.labelsize'] = font_size
# plt.rcParams['ytick.labelsize'] = font_size
# plt.rcParams['legend.fontsize'] = font_size - 10


base_figsize = (6, 4.5)  # Width, Height in inches
base_fontsize = 18
plt.rcParams.update({
    'figure.figsize': base_figsize,  # Set the default figure size
    'figure.dpi': 300,  # Set the figure DPI for high-resolution images
    'savefig.dpi': 300,  # DPI for saved figures
    'font.size': base_fontsize,  # Base font size
    'axes.labelsize': base_fontsize ,  # Font size for axis labels
    'axes.titlesize': base_fontsize + 2,  # Font size for subplot titles
    'xtick.labelsize': base_fontsize - 4,  # Font size for X-axis tick labels
    'ytick.labelsize': base_fontsize,  # Font size for Y-axis tick labels
    'legend.fontsize': base_fontsize - 6,  # Font size for legends
    'lines.linewidth': 2,  # Line width for plot lines
    'lines.markersize': 6,  # Marker size for plot markers
    'figure.autolayout': True,  # Automatically adjust subplot params to fit the figure
    'text.usetex': False,  # Use LaTeX for text rendering (set to True if LaTeX is installed)
})

np.random.seed(42)
random.seed(42)

def generate_several_graphs(from_one_graph=False, proximity_mode="knn", show_plots=False):
    args_list = []
    # false_edge_list = [0, 20, 40, 60, 80, 100]
    # false_edge_list = [0, 2, 5, 10, 20, 1000]
    false_edge_list = [0, 5, 10, 50, 100]




    if not from_one_graph:
        for idx, false_edge_count in enumerate(false_edge_list):
            args = GraphArgs()
            args.verbose = False
            args.proximity_mode = proximity_mode
            args.dim = 2
            args.show_plots = False
            args.intended_av_degree = 10
            args.num_points = 1000
            args.false_edges_count = false_edge_count
            args.network_name = f'FE={args.false_edges_count}'
            edge_list_title = f"edge_list_{args.args_title}_graph_{idx}.csv"  # Assuming 'args.title' exists
            args.edge_list_title = edge_list_title  # update the edge list title
            args.original_edge_list_title = edge_list_title
            write_proximity_graph(args, point_mode="square", order_indices=False)
            # compute_shortest_path_matrix_sparse_graph(graph, args=args)
            args_list.append(args)
    # TODO: just add false edges to one graph, but "create" different ones

    else:
        args = GraphArgs()
        args.verbose = False
        args.proximity_mode = proximity_mode
        args.dim = 2
        args.show_plots = show_plots
        args.intended_av_degree = 10
        args.num_points = 2000
        write_proximity_graph(args, point_mode="square", order_indices=False)
        load_graph(args, load_mode='sparse')
        all_random_false_edges = select_false_edges_csr(args.sparse_graph, max(false_edge_list))

        for idx, num_edges in enumerate(false_edge_list):
            args_i = copy.copy(args)
            modified_graph = add_specific_random_edges_to_csrgraph(args.sparse_graph, all_random_false_edges,
                                                                   num_edges)
            args_i.sparse_graph = modified_graph
            args.shortest_path_matrix = compute_shortest_path_matrix_sparse_graph(args=args_i, sparse_graph=args_i.sparse_graph, force_recompute=True)
            args_i.false_edges_count = num_edges
            edge_list_title = f"edge_list_{args_i.args_title}_graph_{idx}.csv"
            args_i.edge_list_title = edge_list_title  # update the edge list title
            args_i.network_name = f'FE={args_i.false_edges_count}'
            args_i.original_edge_list_title = edge_list_title
            args_i.update_args_title()
            write_edge_list_sparse_graph(args_i, args_i.sparse_graph)
            args_list.append(args_i)

    return args_list

def generate_experimental_graphs(edge_list_titles_dict, add_2d_simulation=True, show_plots=False, force_dim=None):
    """
    Load experimental graphs from comparisons. Just input all the edge_list_titles you want in the
    data/edge_lists folder. If you want different thresholds for the same weighted graph, you can input it as the value
    of the dictionary (second element of the tuple).

    Dictionary:  key --> edge list name, value --> 'weight' tuple (see below)
    Weight[0] --> name of the network
    Weight[1] --> it is none, or contains a list of weight thresholds
    """

    args_list = []
    for item in edge_list_titles_dict.items():
        if len(item) == 2:
            edge_list, weight_list = item
        elif len(item) == 3:
            edge_list, weight_list, color = item

        if weight_list[1] is None:
            args = GraphArgs()
            args.verbose = False
            if len(weight_list) == 3:
                color = weight_list[2]
                args.color = color
            args.dim = 3 if "dim=3" in edge_list else 2
            if force_dim is not None:
                args.dim = force_dim
            args.show_plots = show_plots
            args.edge_list_title = edge_list
            args.proximity_mode = "experimental"
            if args.num_points > 3000:
                warnings.warn("Large graph detected! Subsampling reccommended")
                # args.large_graph_subsampling = True
                # args.max_subgraph_size = 3000
            sparse_graph = load_graph(args, load_mode='sparse')
            args.sparse_graph = sparse_graph
            args.shortest_path_matrix = compute_shortest_path_matrix_sparse_graph(args=args,
                                                                                  sparse_graph=args.sparse_graph)
            args.network_name = weight_list[0]

            args_list.append(args)
        else:
            for weight in weight_list[1]:
                args = GraphArgs()
                args.verbose = False
                args.dim = 3 if "dim=3" in edge_list else 2
                if force_dim is not None:
                    args.dim = force_dim
                if len(weight_list) == 3:
                    color = weight_list[2]
                    args.color = color
                args.show_plots = show_plots
                args.weighted = True
                args.weight_threshold = weight
                args.edge_list_title = edge_list
                args.proximity_mode = "experimental"
                args.weighted = True
                args.weight_to_distance = True
                args.weight_to_distance_fun = "exp"
                if args.num_points > 3000:
                    warnings.warn("Large graph detected! Subsampling reccommended")
                    # args.large_graph_subsampling = True
                    # args.max_subgraph_size = 3000
                sparse_graph = load_graph(args, load_mode='sparse')
                args.sparse_graph = sparse_graph
                args.shortest_path_matrix = compute_shortest_path_matrix_sparse_graph(args=args, sparse_graph=args.sparse_graph)
                args.edge_list_title = f"{os.path.splitext(edge_list)[0]}_weight_threshold_{args.weight_threshold}.csv"
                args.network_name = weight_list[0] + f"{args.weight_threshold}"
                write_edge_list_sparse_graph(args, args.sparse_graph)

                args_list.append(args)



    ## add simulated graph for compariosn

    if args.weighted and args.weight_to_distance:  # if the last case was weighted, the simulation will also be
        a = 2
    elif add_2d_simulation:  # only have simulated comparison for unweighted graph
        args_sim = GraphArgs()
        args_sim.num_points = 1000
        args_sim.proximity_mode = "delaunay_corrected"
        if len(weight_list) == 3:
            color = weight_list[2]
            args.color = color
        args_sim.dim = 2
        args_sim.intended_av_degree = 10
        args_sim.verbose = False
        write_proximity_graph(args_sim, point_mode="circle", order_indices=False)
        args_sim.sparse_graph = load_graph(args_sim, load_mode='sparse')
        args_sim.shortest_path_matrix = compute_shortest_path_matrix_sparse_graph(args=args_sim, sparse_graph=args_sim.sparse_graph)
        args_sim.network_name = "Simulation"
        args_list.append(args_sim)
    return args_list


def get_maximally_separated_colors(num_colors):
    hues = np.linspace(0, 1, num_colors + 1)[:-1]  # Avoid repeating the first color
    colors = [mcolors.hsv_to_rgb([h, 0.7, 0.7]) for h in hues]  # S and L fixed for aesthetic colors
    # Convert to HEX format for broader compatibility
    colors = [mcolors.to_hex(color) for color in colors]
    return colors

def plot_comparative_spatial_constant(results_dfs, args_list, title="", use_depth=False, single_color=None, square_mode=False):
    from matplotlib.ticker import MaxNLocator

    ax = plt.figure(figsize=(9, 4.5)).gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    num_colors = len(args_list)
    if single_color:
        colors = [single_color] * num_colors
    else:
        colors = get_maximally_separated_colors(num_colors)

    if use_depth:
        size_magnitude = 'depth'
        s_constant = 'S_general'
    else:
        size_magnitude = 'intended_size'
        s_constant = 'S_general'

    data_means = []
    data_depths = []
    data_stds = []
    for i, (results_df_net, args) in enumerate(zip(results_dfs, args_list)):
        unique_sizes = results_df_net[size_magnitude].unique()
        means = []
        std_devs = []
        sizes = []

        for size in unique_sizes:
            subset = results_df_net[results_df_net[size_magnitude] == size]
            mean = subset['S_general'].mean()
            std = subset['S_general'].std()
            means.append(mean)
            std_devs.append(std)
            sizes.append(size)

        sizes_net = np.array(sizes)
        means_net = np.array(means)
        std_devs_net = np.array(std_devs)

        data_means.append(means_net)
        data_depths.append(sizes_net)
        data_stds.append(std_devs_net)

        # Use color from the selected palette
        if hasattr(args, "color") and not single_color:
            color = args.color
        else:
            color = colors[i]

        # Scatter plot and ribbon for mean spatial constants
        plt.plot(sizes, means, label=f'{args.network_name}', marker='o', color=color)
        plt.fill_between(sizes_net, means_net - std_devs_net, means_net + std_devs_net, alpha=0.2, color=color)

    if use_depth:
        plt.xlabel('Depth')
    else:
        plt.xlabel('Size')
    plt.ylabel('Mean Spatial Constant')
    plt.legend()

    if square_mode:
        plt.gca().set_box_aspect(1)

    plt.tight_layout()

    # Save the figure
    plot_folder = f"{args_list[0].directory_map['plots_spatial_constant_subgraph_sampling']}"
    plt.savefig(f"{plot_folder}/comparative_spatial_constant_{title}.svg")
    plot_folder2 = f"{args_list[0].directory_map['comparative_plots']}"
    plt.savefig(f"{plot_folder2}/comparative_spatial_constant_{title}.svg")

    column_names_means = [args.network_name + ' mean spatial constant' for args in args_list]
    column_names_sizes = [args.network_name + ' depths' for args in args_list]
    column_names_stds = [args.network_name + ' stds' for args in args_list]
    column_names = column_names_means + column_names_sizes + column_names_stds
    data = data_means + data_depths + data_stds

    save_plotting_data(column_names=column_names, data=data,
                       csv_filename=f"{plot_folder2}/comparative_spatial_constant_{title}.csv")

    if args_list[0].show_plots:
        plt.show()

def make_spatial_constant_comparative_plot(args_list, title="", single_color=None, square_mode=False):
    n_samples = 5
    net_results_df_list = []
    for args in args_list:
        size_interval = int(args.num_points / 10)  # collect 10 data points

        ## Network Spatial Constant
        # igraph_graph = load_graph(args, load_mode='igraph')  #TODO: make sure igraph is what you need
        # igraph_graph = load_graph(args, load_mode='sparse')

        # ### Run with size
        # net_results_df = run_simulation_subgraph_sampling(args, size_interval=size_interval, n_subgraphs=n_samples,
        #                                                   graph=igraph_graph,
        #                                                   add_false_edges=False, add_mst=False, return_simple_output=False)

        ### Run with depth  #TODO: check that this work
        shortest_path_matrix = args.shortest_path_matrix
        print("NETWORK NAME", args.network_name)

        if args.weighted and args.weight_to_distance:
            igraph_graph = load_graph(args, load_mode='sparse')
            net_results_df = run_spatial_constant_continuous(args, shortest_path_matrix=shortest_path_matrix,
                                                          n_subgraphs=10,
                                                          graph=igraph_graph, add_false_edges=False,
                                                          false_edge_list=[], return_simple_output=False)
        else:
            igraph_graph = load_graph(args, load_mode='igraph')  # TODO: make sure igraph is what you need
            net_results_df = run_simulation_subgraph_sampling_by_bfs_depth(args, shortest_path_matrix=shortest_path_matrix,
                                                                        n_subgraphs=n_samples, graph=igraph_graph,
                                                                        add_false_edges=False, return_simple_output=False,
                                                                        all_depths=True)



        net_results_df_list.append(net_results_df)


    plot_comparative_spatial_constant(net_results_df_list, args_list, title=title, use_depth=True, single_color=single_color, square_mode=square_mode)


def make_dimension_prediction_comparative_plot(args_list, title="", single_color=None, square_mode=False):
    results_pred_dimension_list = []
    for args in args_list:
        if args.sparse_graph is None:
            sparse_graph = load_graph(args, load_mode='sparse')
            compute_shortest_path_matrix_sparse_graph(sparse_graph=sparse_graph, args=args)
        elif args.shortest_path_matrix is None:
            compute_shortest_path_matrix_sparse_graph(sparse_graph=args.sparse_graph, args=args)

        if args.weight_to_distance and args.weighted:  # weighted case
            # TODO: include heatmap nodes for weighted
            results_pred_dimension = run_dimension_prediction_continuous(args, distance_matrix=args.shortest_path_matrix,
                                                              )
        else:
            print("2", args.shortest_path_matrix)
            print("1", args.mean_shortest_path)
            results_pred_dimension = run_dimension_prediction(args, distance_matrix=args.shortest_path_matrix,
                                                              dist_threshold=int(args.mean_shortest_path),
                                                              local_dimension=False, plot_heatmap_all_nodes=False)
        results_pred_dimension_list.append(results_pred_dimension)
    plot_comparative_predicted_dimension(args_list=args_list, results_predicted_dimension_list=results_pred_dimension_list,
                                         title=title, single_color=single_color, square_mode=square_mode)


def plot_comparative_predicted_dimension(args_list, results_predicted_dimension_list, title="", single_color=None,
                                         square_mode=False):
    ax_limits = False  # I put this to plot Revision 1 supp plot 3
    if ax_limits:
    # Set the limits for the y-axis
        y_min = 0
        y_max = 3.5
    plt.figure(figsize=(9, 4.5))

    num_colors = len(args_list)
    colors = []
    if single_color:
        colors = [single_color] * num_colors
    else:
        default_colors = get_maximally_separated_colors(num_colors)
        default_index = 0

        for arg in args_list:
            if hasattr(arg, 'color'):
                colors.append(arg.color)
            else:
                colors.append(default_colors[default_index])
                default_index += 1

    # X-axis positions for each violin plot
    x_positions = np.arange(num_colors)

    # Data for plotting, now directly using 'predicted_dimension_list' from each dictionary
    violin_data = [res['predicted_dimension_list'] for res in results_predicted_dimension_list]
    labels = [args.network_name for args in args_list]

    parts = plt.violinplot(violin_data, positions=x_positions, showmeans=False, showmedians=True)
    # Overlay points on the violin plots
    for i, data in enumerate(violin_data):
        # Generating a slight random offset to spread the points horizontally and improve visibility
        x_values = np.random.normal(i, 0.04, size=len(data))
        plt.scatter(x_values, data, alpha=1, color=colors[i],
                    edgecolor='black')  # Adjust alpha as needed for better visibility

    # Coloring each violin plot
    for pc, color in zip(parts['bodies'], colors):
        pc.set_facecolor(color)
        pc.set_edgecolor('black')  # Adding a contrasting edge color for better visibility
        pc.set_alpha(0.7)

    # Aesthetics
    if len(labels) > 5:  # Adjust this threshold as needed
        plt.xticks(x_positions, labels, rotation=45, ha="right")
    else:
        plt.xticks(x_positions, labels, rotation=0, ha="center")
    plt.ylabel('Predicted Dimension')
    # plt.title(title if title else 'Predicted Dimension Distribution for Each Graph')

    if ax_limits:
        plt.ylim(y_min, y_max)

    if square_mode:
        plt.gca().set_box_aspect(1)

    plt.tight_layout()

    plot_folder = f"{args_list[0].directory_map['dimension_prediction_iterations']}"
    plt.savefig(f"{plot_folder}/comparative_dimension_prediction_violin_{title}.svg")
    plot_folder2 = f"{args_list[0].directory_map['comparative_plots']}"
    plt.savefig(f"{plot_folder2}/comparative_dimension_prediction_violin_{title}.svg")

    column_names = [args.network_name for args in args_list]
    data = violin_data
    save_plotting_data(column_names=column_names, data=data,
                       csv_filename=f"{plot_folder2}/comparative_dimension_prediction_violin_{title}.csv")

    if args_list[0].show_plots:
        plt.show()


def make_gram_matrix_analysis_comparative_plot(args_list, title="", single_color=None, square_mode=False):
    eigenvalues_list = []
    for i, args in enumerate(args_list):
        if args.sparse_graph is None:
            sparse_graph = load_graph(args, load_mode='sparse')
            compute_shortest_path_matrix_sparse_graph(sparse_graph=sparse_graph, args=args)
        elif args.shortest_path_matrix is None:
            compute_shortest_path_matrix_sparse_graph(sparse_graph=args.sparse_graph, args=args)

        eigenvalues_sp_matrix = compute_gram_matrix_eigenvalues(distance_matrix=args.shortest_path_matrix)
        eigenvalues_list.append(eigenvalues_sp_matrix)

        first_d_values_contribution,\
        first_d_values_contribution_5_eigen,\
        spectral_gap,\
        last_spectral_gap, \
        first_2_values_contribution_5_eigen \
            = plot_gram_matrix_eigenvalues(args=args, shortest_path_matrix=args.shortest_path_matrix)
    # plot_eigenvalue_contributions_comparative(eigenvalues_list, args_list, title=title, single_color=single_color, square_mode=square_mode)
    plot_eigenvalue_contributions_comparative(eigenvalues_list, args_list, consider_first_eigenvalues_only=True, title=title,single_color=single_color, square_mode=square_mode)
    plot_spectral_gap_comparative(args_list, eigenvalues_list, score_method='f', title=title, single_color=single_color, square_mode=square_mode)
    #plot_pos_neg_eigenvalue_proportions_comparative(args_list, eigenvalues_list)



def plot_eigenvalue_contributions_comparative_v0(eigenvalues_list, args_list, title='', consider_first_eigenvalues_only=False,
                                              single_color=None, square_mode=False):
    """
    Plot eigenvalue contributions for multiple networks and a comparative bar chart
    of cumulative variance for the first d eigenvalues.

    :param eigenvalues_list: List of arrays, where each array contains the eigenvalues of a network.
    :param args_list: List of args objects, used for labeling.
    """
    # Create figure and subplots
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.5), gridspec_kw={'width_ratios': [1, 1]})

    multicolor = True

    if multicolor:
        num_colors = len(args_list)
        colors = []
        default_colors = get_maximally_separated_colors(num_colors)
        default_index = 0
        for arg in args_list:
            if hasattr(arg, 'color'):
                colors.append(arg.color)
            else:
                colors.append(default_colors[default_index])
                default_index += 1

    else:
        # unicolor (comment if you want rainbow color)
        colors = ['#009ADE'] * len(args_list)



    cumulative_variances = []

    for i, (S, args) in enumerate(zip(eigenvalues_list, args_list)):
        network_name = args.network_name

        if consider_first_eigenvalues_only:
            S = S[:10]
        total_variance = np.sum(S)
        variance_proportion = S / total_variance
        cumulative_variance = np.cumsum(variance_proportion)
        cumulative_variance_first_d_eigenvalues = cumulative_variance[args.dim - 1]

        selected_cumulative_variances = cumulative_variance[:args.dim]




        color = colors[i]

        # Plot on the first subplot
        axs[0].plot(range(1, len(S) + 1), cumulative_variance, '-o' , color=color)
        axs[0].axvline(x=args.dim, linestyle='--')

        # Append the list of selected cumulative variances instead of a single value
        cumulative_variances.append((selected_cumulative_variances, color))
        # cumulative_variances.append((cumulative_variance_first_d_eigenvalues, color))

    # Setting for the first plot
    axs[0].set_xlabel('Eigenvalue Rank')
    axs[0].set_ylabel('Eigenvalue Contribution')
    axs[0].set_xscale('log')
    # axs[0].legend()

    # # Bar chart for cumulative variance comparison, using the same colors
    # for i, (cumulative_variance, color) in enumerate(cumulative_variances):
    #     axs[1].bar(i, cumulative_variance, color=color)

    for i, (variances, base_color) in enumerate(cumulative_variances):
        # Bottom of the bar stack
        bottom = 0
        color_gradient = [mcolors.to_rgba(base_color, alpha=0.5 + 0.5 * (1 - j / (len(variances) - 1))) if len(
            variances) > 1 else base_color for j in range(len(variances))]
        # Iterate over each cumulative variance up to args.dim
        for j in range(len(variances)):
            # Plot the segment of the stacked bar
            if j == 0:
                height = variances[j]
            else:
                height = variances[j] - variances[j - 1]

            color = color_gradient[j]
            axs[1].bar(i, height,  bottom=bottom, color=color)
            # Update the bottom to the top of the last bar
            bottom = variances[j]

    # Create custom legend
    if args.dim == 3:
        legend_labels = ['1st eigenvalue', '2nd eigenvalue', '3rd eigenvalue']

    elif args.dim == 2:
        legend_labels = ['1st eigenvalue', '2nd eigenvalue']

    color = '#009ADE'  #TODO: change this if there is multicolor, maybe change it to black
    legend_patches = [mpatches.Patch(color=color, alpha=0.5 + 0.5 * (1 - i / (args.dim - 1)), label=label) for i, label in
                      enumerate(legend_labels)]
    axs[1].legend(handles=legend_patches)

    axs[1].set_ylabel('Variance Contribution')
    axs[1].set_xticks(range(len(args_list)))
    axs[1].set_xticklabels([args.network_name for args in args_list], rotation=0, ha="center")
    axs[1].set_ylim(0, 1)

    plt.tight_layout()
    plot_folder = f"{args_list[0].directory_map['mds_dim']}"
    prefix = 'first_' if consider_first_eigenvalues_only else ''
    plt.savefig(f"{plot_folder}/comparative_{prefix}eigenvalue_contributions_{title}.svg")
    plot_folder2 = f"{args_list[0].directory_map['comparative_plots']}"
    plt.savefig(f"{plot_folder2}/comparative_{prefix}eigenvalue_contributions_{title}.svg")

    column_names = [args.network_name for args in args_list]
    data = cumulative_variances

    data = [item[0] for item in data]  # ignore the color tuple (2nd element)
    save_plotting_data(column_names=column_names, data=data,
                       csv_filename=f"{plot_folder2}/comparative_{prefix}eigenvalue_contributions_{title}.csv")
    if args.show_plots:
        plt.show()

def plot_eigenvalue_contributions_comparative(eigenvalues_list, args_list, title='', consider_first_eigenvalues_only=False,
                                              single_color=None, square_mode=False):
    """
    Plot eigenvalue contributions for multiple networks and a comparative bar chart
    of cumulative variance for the first d eigenvalues.
    :param eigenvalues_list: List of arrays, where each array contains the eigenvalues of a network.
    :param args_list: List of args objects, used for labeling.
    :param title: Optional title for the plots.
    :param consider_first_eigenvalues_only: Whether to consider only the first few eigenvalues.
    :param single_color: If specified, all plots will use this single color.
    :param square_mode: If True, plots will have a square aspect ratio.
    """
    # Create figure and subplots
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.5), gridspec_kw={'width_ratios': [1, 1]})

    if single_color:
        colors = [single_color] * len(args_list)
    else:
        num_colors = len(args_list)
        colors = get_maximally_separated_colors(num_colors)

    cumulative_variances = []
    max_dim = 0  # To track the maximum dimension needed for the legend

    for i, (S, args) in enumerate(zip(eigenvalues_list, args_list)):
        network_name = args.network_name

        if consider_first_eigenvalues_only:
            S = S[:10]
        total_variance = np.sum(S)
        variance_proportion = S / total_variance
        cumulative_variance = np.cumsum(variance_proportion)
        selected_cumulative_variances = cumulative_variance[:args.dim]

        max_dim = max(max_dim, args.dim)  # Update max dimension observed

        color = colors[i]

        # Plot on the first subplot
        axs[0].plot(range(1, len(S) + 1), cumulative_variance, '-o', color=color)

        cumulative_variances.append((selected_cumulative_variances, color))

    # Setting for the first plot
    axs[0].set_xlabel('Eigenvalue Rank')
    axs[0].set_ylabel('Eigenvalue Contribution')
    axs[0].set_xscale('log')

    # Bar chart for cumulative variance comparison, using the same colors
    for i, (variances, base_color) in enumerate(cumulative_variances):
        bottom = 0
        for j in range(len(variances)):
            height = variances[j] - bottom if j > 0 else variances[j]
            axs[1].bar(i, height, bottom=bottom, color=colors[i], alpha=0.5 + 0.5 * ((len(variances) - j - 1) / (len(variances) - 1)))
            bottom = variances[j]

    axs[1].set_ylabel('Variance Contribution')
    axs[1].set_xticks(range(len(args_list)))
    axs[1].set_xticklabels([args.network_name for args in args_list], rotation=45 if len(args_list) > 3 else 0, ha="right")
    axs[1].set_ylim(0, 1)

    # Create custom legend based on max_dim
    legend_labels = [f'{n+1}st eigenvalue' if n == 0 else f'{n+1}nd eigenvalue' if n == 1 else f'{n+1}rd eigenvalue' for n in range(max_dim)]
    print("legend_labels", legend_labels)

    if single_color:
        legend_patches = [mpatches.Patch(color=single_color, alpha=0.5 + 0.5 * (1 - i / (max_dim - 1)), label=label) for i, label in enumerate(legend_labels)]
    else:
        legend_patches = [mpatches.Patch(color=colors[i], alpha=0.5 + 0.5 * (1 - i / (max_dim - 1)), label=label) for i, label in enumerate(legend_labels)]
    axs[1].legend(handles=legend_patches, loc='upper right')

    if square_mode:
        axs[0].set_box_aspect(1)
        axs[1].set_box_aspect(1)

    plt.tight_layout()
    plot_folder = f"{args_list[0].directory_map['mds_dim']}"
    prefix = 'first_' if consider_first_eigenvalues_only else ''
    plt.savefig(f"{plot_folder}/comparative_{prefix}eigenvalue_contributions_{title}.svg")
    plot_folder2 = f"{args_list[0].directory_map['comparative_plots']}"
    plt.savefig(f"{plot_folder2}/comparative_{prefix}eigenvalue_contributions_{title}.svg")

    column_names = [args.network_name for args in args_list]
    data = [item[0] for item in cumulative_variances]
    save_plotting_data(column_names=column_names, data=data,
                       csv_filename=f"{plot_folder2}/comparative_{prefix}eigenvalue_contributions_{title}.csv")

    if args_list[0].show_plots:
        plt.show()

def calculate_spectral_score(eigenvalues, args, method):
    from sklearn.metrics.pairwise import cosine_similarity
    eigenvalues_sorted = np.sort(eigenvalues)[::-1]
    positive_eigenvalues = eigenvalues_sorted[eigenvalues_sorted > 0]
    score = 0

    if method == 'a':
        # Relative Contribution Score
        score = np.sum(positive_eigenvalues[:args.dim]) / np.sum(positive_eigenvalues)
    elif method == 'b':
        # Exponential Decay Score
        penalty = np.exp(-np.sum(positive_eigenvalues[args.dim:])) / np.exp(-np.sum(positive_eigenvalues[:args.dim]))
        score = penalty
    elif method == 'c':
        # Harmonic Mean of Contributions
        contributions = positive_eigenvalues[:args.dim] / np.sum(positive_eigenvalues)
        score = len(contributions) / np.sum(1.0 / contributions)
    elif method == 'd':
        # Squared Difference Score
        ideal_contrib = np.zeros_like(positive_eigenvalues)
        ideal_contrib[:args.dim] = positive_eigenvalues[:args.dim]
        # ideal_contrib[:args.dim] = np.ones(args.dim)
        # print(ideal_contrib)
        score = 1 - (np.sum((ideal_contrib - positive_eigenvalues) ** 2) / np.sum(positive_eigenvalues ** 2))
    elif method == 'e':
        # Cosine Similarity Score
        actual_vector = np.hstack([positive_eigenvalues[:args.dim], np.zeros(len(positive_eigenvalues) - args.dim)])
        ideal_vector = np.zeros_like(actual_vector)
        ideal_vector[:args.dim] = positive_eigenvalues[:args.dim]
        score = cosine_similarity([actual_vector], [ideal_vector])[0][0]
    elif method == 'f':
        # 1st original method, just gap between d and d+1 value
        spectral_gaps = (positive_eigenvalues[:-1] - positive_eigenvalues[1:]) / positive_eigenvalues[:-1]
        score = spectral_gaps[args.dim - 1]
    elif method == 'g':
        # Normalizing using only 1st eigenvalue
        score = (positive_eigenvalues[0] - positive_eigenvalues[args.dim-1]) / positive_eigenvalues[0]

    elif method == 'h':  # squared difference, all eigenvalues d+1 should be 0
        ideal_contrib = np.zeros_like(eigenvalues_sorted[args.dim:])
        score = 1 - (np.sum((ideal_contrib - eigenvalues_sorted[args.dim:]) ** 2) / np.sum(eigenvalues_sorted[:args.dim] ** 2))

    elif method == 'i':
        # Gab between the mean of the first d eigenvalues and the d+1 value --> This seems to work quite well
        # THIS IS THE METHOD I CHOOSE TO USE
        d_values = np.mean(positive_eigenvalues[:args.dim])
        gap = (d_values - positive_eigenvalues[args.dim+1]) / d_values
        score = gap
    elif method == 'negative_mass_fraction':
        # Mass fraction of negative eigenvalues
        negative_eigenvalues = eigenvalues_sorted[eigenvalues_sorted < 0]
        score = np.sum(np.abs(negative_eigenvalues)) / (np.sum(positive_eigenvalues) + np.sum(np.abs(negative_eigenvalues)))
    else:
        raise ValueError("Invalid scoring method specified.")

    return score


def plot_spectral_gap_comparative(args_list, eigenvalues_list, score_method='i', title='', single_color=None, square_mode=False):
    """
    Plot spectral gap for multiple networks, presenting comparative data and a bar chart of spectral gap scores.
    :param args_list: List of args objects, used for labeling.
    :param eigenvalues_list: List of eigenvalue arrays for each network.
    :param score_method: 'i' for mean of all first eigenvalues, 'f' for just the last relevant one.
    :param title: Optional title for the plots.
    :param single_color: If specified, all plots will use this single color.
    :param square_mode: If True, plots will have a square aspect ratio.
    """
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.5), gridspec_kw={'width_ratios': [1, 1]})

    if single_color:
        colors = [single_color] * len(args_list)
    else:
        colors = get_maximally_separated_colors(len(args_list))

    spectral_gap_scores = []

    for i, (eigenvalues, args) in enumerate(zip(eigenvalues_list, args_list)):
        eigenvalues_sorted = np.sort(eigenvalues)[::-1]
        positive_eigenvalues = eigenvalues_sorted[eigenvalues_sorted > 0]
        positive_eigenvalues_short = positive_eigenvalues[:5]
        spectral_gaps = (positive_eigenvalues_short[:-1] - positive_eigenvalues_short[1:]) / positive_eigenvalues_short[:-1]
        color = colors[i]

        axs[0].plot(range(1, len(spectral_gaps) + 1), spectral_gaps, marker='o', linestyle='-', linewidth=2, markersize=8,
                    label=args.network_name, color=color)

        spectral_gap_score = calculate_spectral_score(eigenvalues, args, method=score_method)
        spectral_gap_scores.append(spectral_gap_score)

    axs[0].set_xlabel('Eigenvalue Rank')
    axs[0].set_ylabel('Spectral Gap Ratio')
    axs[0].legend()

    for j, spectral_gap_score in enumerate(spectral_gap_scores):
        axs[1].bar(j, spectral_gap_score, color=colors[j])

    axs[1].set_ylabel('Spectral Gap Score')
    axs[1].set_xticks(range(len(args_list)))
    axs[1].set_xticklabels([args.network_name for args in args_list], rotation=45 if len(args_list) > 3 else 0, ha="right")
    axs[1].set_ylim(0, 1)

    if square_mode:
        axs[0].set_box_aspect(1)
        axs[1].set_box_aspect(1)

    plt.tight_layout()

    plot_folder = f"{args_list[0].directory_map['mds_dim']}"
    plt.savefig(f"{plot_folder}/comparative_spectral_gap_{title}.svg")
    plot_folder2 = f"{args_list[0].directory_map['comparative_plots']}"
    plt.savefig(f"{plot_folder2}/comparative_spectral_gap_{title}.svg")

    column_names = [args.network_name for args in args_list]
    data = [[spectral_gap_score] for spectral_gap_score in spectral_gap_scores]
    print("Spectral gap scores: ", spectral_gap_scores)
    save_plotting_data(column_names=column_names, data=data,
                       csv_filename=f"{plot_folder2}/comparative_spectral_gap_{title}.csv")

    if args_list[0].show_plots:
        plt.show()


def plot_pos_neg_eigenvalue_proportions_comparative(args_list, eigenvalues_list):
    fig, axs = plt.subplots(figsize=(10, 6))

    # Retrieve the default color cycle
    colors = get_maximally_separated_colors(len(args_list))
    proportions = []

    # Iterate over each network's eigenvalues
    for i, (eigenvalues, args) in enumerate(zip(eigenvalues_list, args_list)):

        ## TODO: option 1 ratio neg/pos and use all eigenvalues
        ## todo: option 2 use only eigenvalues > 0 till args.dim and all negative eigenvalues, and ratio pos/neg
        ## TODO: option 3 ratio contribution dim eigenvalues divided by all the rest (using absolute value for the negative)
        # Count positive and negative eigenvalues
        num_positive = np.sum(eigenvalues[eigenvalues > 0])
        num_positive_dim = np.sum(eigenvalues[eigenvalues > 0][:args.dim])
        num_positive_nondim = np.sum(eigenvalues[eigenvalues > 0][args.dim:])
        num_negative = np.abs(np.sum(eigenvalues[eigenvalues < 0]))  # Use absolute sum for negative eigenvalues
        print("positive", num_positive, "negative", num_negative)
        print("positive dim", num_positive_dim)

        # Calculate the proportion of positive to negative eigenvalues
        # If there are no negative eigenvalues, set the proportion to the number of positive eigenvalues
        if num_negative > 0:
            # proportion = num_negative / num_positive
            proportion = num_positive_dim / (num_negative + num_positive_nondim)
            proportion = (num_negative + num_positive_nondim) / num_positive_dim
            proportion =  num_negative / (num_positive + num_negative)  # proportion of badness (negative mass ratio)
            proportion = np.max(num_negative) / np.max(num_positive)   # same but taking into account biggest eigenvalues only
            print("proportion", proportion)
            print("num positive", num_positive, "num negative", num_negative)
        else:
            proportion = num_positive

        proportions.append(proportion)

        # Use the same color for the current network in the bar plot
        color = colors[i]

        # Plot the proportion in the bar plot
        axs.bar(i, proportion, color=color, label=args.network_name)

    axs.set_xlabel('Network')
    axs.set_ylabel('Proportion of Negative/Positive Eigenvalues')
    axs.set_xticks(range(len(args_list)))
    axs.set_xticklabels([args.network_name for args in args_list], rotation=45, ha="right")
    axs.legend()

    plt.tight_layout()
    plt.show()


# --- Constants ---
TRI_COLOR_MODE = True
SP_CONSTANT_COLOR = "#009ADE" if TRI_COLOR_MODE else None
DIM_PRED_COLOR = "#009ADE" if TRI_COLOR_MODE else None
EIGENVALUES_COLOR = "#009ADE" if TRI_COLOR_MODE else None


# --- Configuration Functions ---

def get_simulation_args(show_plots=False):
    proximity_mode = "delaunay_corrected"
    args_list = generate_several_graphs(from_one_graph=True, proximity_mode=proximity_mode, show_plots=show_plots)
    # title = f"False Edge Comparison v2 {proximity_mode}"
    title = f"False Edge Comparison"
    return args_list, title


def get_pixelgen_args(show_plots=False):
    title = "MPX"
    edge_list_titles_dict = {
        "Sample01_human_pbmcs_unstimulated_component_RCVCMP0001392_edgelist.csv": ('PBMC 1', None),
        "Sample01_human_pbmcs_unstimulated_component_RCVCMP0002024_edgelist.csv": ('PBMC 2', None),
        "Sample01_human_pbmcs_unstimulated_component_RCVCMP0000120_edgelist.csv": ('PBMC 3', None)
    }
    args_list = generate_experimental_graphs(edge_list_titles_dict=edge_list_titles_dict, add_2d_simulation=True, show_plots=show_plots)
    return args_list, title

def get_swissroll_args(show_plots=False):
    title = "swissroll"
    edge_list_titles_dict = {
        "edge_list_N=2000_dim=3_knn_k=7_swissroll.csv": ('classic SR', None),
        "edge_list_N=2000_dim=3_knn_k=50_swissroll.csv": ('interconnected SR', None),
        "edge_list_N=2000_dim=3_knn_with_false_edges=100_k=7_swissroll.csv": ('noisy SR', None)
    }
    # args_list = generate_experimental_graphs(edge_list_titles_dict=edge_list_titles_dict, add_2d_simulation=False, show_plots=show_plots)

    args_list = generate_experimental_graphs(edge_list_titles_dict=edge_list_titles_dict, add_2d_simulation=False,
                                             show_plots=show_plots, force_dim=2)   # if you want spatial constant to have 2 as exponent instead of 3
    return args_list, title

def get_dna_mic_args(show_plots=False):
    title = "DNA_Mic"
    threshold_list = [1, 3, 6]
    edge_list_titles_dict = {
        "weinstein_data_corrected_february.csv": ('DNA_M', threshold_list)
    }
    args_list = generate_experimental_graphs(edge_list_titles_dict=edge_list_titles_dict, show_plots=show_plots, add_2d_simulation=False)
    return args_list, title

def get_weinstein_squarebipartite(show_plots=False):
    title = "Weinstein_SquareBipartite"
    # edge_list_titles_dict = {
    #     "edgelist_dnamic_N=4093_E=74752_fltpwr=85.csv": ('pwr 85', None),
    #     "edgelist_dnamic_N=3261_E=59816_fltpwr=88.csv": ('pwr 88', None),
    #
    # }
    # edge_list_titles_dict = {
    #     "weinstein_february_corrected_N=4093_E=74752_fltpwr=85.csv": ('pwr 85', None),
    #     "weinstein_february_corrected_N=10177_E=159404_fltpwr=68.csv": ('pwr 68', None),
    #     "weinstein_february_corrected_N=15515_E=219121_fltpwr=56.csv": ('pwr 56', None),
    #     "weinstein_february_corrected_N=20701_E=269002_fltpwr=46.csv": ('pwr 46', None),
    #     "weinstein_february_corrected_N=30193_E=348657_fltpwr=30.csv": ('pwr 30', None),
    #     "weinstein_february_corrected_N=40237_E=417779_fltpwr=16.csv": ('pwr 16', None),
    #     "weinstein_february_corrected_N=52672_E=477519_fltpwr=4.csv": ('pwr 4', None),
    # }

    edge_list_titles_dict = {
        "weinstein_february_corrected_N=11309_E=29909_fltpwr=94.csv": ('pwr 94', None),
        "weinstein_february_corrected_N=6126_E=19940_fltpwr=96.csv": ('pwr 96', None),
        "weinstein_february_corrected_N=4303_E=14955_fltpwr=97.csv": ('pwr 97', None),
        "weinstein_february_corrected_N=2882_E=9970_fltpwr=98.csv": ('pwr 98', None),
        "weinstein_february_corrected_N=1776_E=4985_fltpwr=99.csv": ('pwr 99', None),
        #"weinstein_february_corrected_N=29763_E=74772_fltpwr=85.csv": ('pwr 85', None),
        #"weinstein_february_corrected_N=42378_E=134589_fltpwr=73.csv": ('pwr 73', None),
        #"weinstein_february_corrected_N=49623_E=194406_fltpwr=61.csv": ('pwr 61', None),
        #"weinstein_february_corrected_N=53424_E=244254_fltpwr=51.csv": ('pwr 51', None),
        #"weinstein_february_corrected_N=56554_E=309056_fltpwr=38.csv": ('pwr 38', None),
        #"weinstein_february_corrected_N=59439_E=493492_fltpwr=1.csv": ('pwr 1', None),
    }
    args_list = generate_experimental_graphs(edge_list_titles_dict=edge_list_titles_dict, show_plots=show_plots, add_2d_simulation=False)
    return args_list, title

def get_snake_latticecomparison(show_plots=False, false_edge_prc=0):


    if false_edge_prc == 0:
        title = "Snake_LatticeComparison_prc=0"
        edge_list_titles_dict = {
        "edge_list_N=1024_dim=2_lattice_snake_k=7.csv": ("snake 0%", None),
        "edge_list_N=1024_dim=2_lattice_k=7.csv": ("lattice 0%", None),
        }
    elif false_edge_prc == 5:
        title = "Snake_LatticeComparison_prc=5"
        edge_list_titles_dict = {
        "edge_list_N=1024_dim=2_lattice_snake_with_false_edges=50_k=7.csv": ("snake 5%", None),
        "edge_list_N=1024_dim=2_lattice_with_false_edges=100_k=7.csv": ("lattice 5%", None),
        }
    elif false_edge_prc == 10:
        title = "Snake_LatticeComparison_prc=10"
        edge_list_titles_dict = {
        "edge_list_N=1024_dim=2_lattice_snake_with_false_edges=100_k=7.csv": ("snake 10%", None),
        "edge_list_N=1024_dim=2_lattice_with_false_edges=200_k=7.csv": ("lattice 10%", None),
        }
    else:
        raise ValueError("false_edge_prc must be 0, 5, or 10")
    args_list = generate_experimental_graphs(edge_list_titles_dict=edge_list_titles_dict, show_plots=show_plots, add_2d_simulation=False)
    return args_list, title

def run_all_plots(args_list, title, square_mode=False):
    # make_spatial_constant_comparative_plot(args_list, title=title, single_color=SP_CONSTANT_COLOR,
    #                                       square_mode=square_mode)  # TODO: can set square mode to false for square plots
    make_dimension_prediction_comparative_plot(args_list, title=title, single_color=DIM_PRED_COLOR, square_mode=square_mode)
    # make_gram_matrix_analysis_comparative_plot(args_list, title=title, single_color=EIGENVALUES_COLOR, square_mode=square_mode)

# --- Main Comparative Pipeline Function ---

def comparative_plots(dataset_type="simulation", show_plots=False):
    if dataset_type == "simulation":
        args_list, title = get_simulation_args(show_plots=show_plots)
    elif dataset_type == "pixelgen":
        args_list, title = get_pixelgen_args(show_plots=show_plots)
    elif dataset_type == "dna_mic":
        args_list, title = get_dna_mic_args(show_plots=show_plots)
    elif dataset_type == "wei_sqbip":
        args_list, title = get_weinstein_squarebipartite(show_plots=show_plots)
    elif dataset_type == "swissroll":
        args_list, title = get_swissroll_args(show_plots=show_plots)
    elif dataset_type == "snake_latticecomparison":
        for false_edge_prc in [0, 5, 10]:
            args_list, title = get_snake_latticecomparison(show_plots=show_plots, false_edge_prc=false_edge_prc)  # 0, 5, or 10 percent of false edges
            run_all_plots(args_list, title, square_mode=True)
    else:
        raise ValueError("dataset_type must be 'simulation', 'pixelgen', or 'dna_mic'")

    if not dataset_type == "snake_latticecomparison": # Normal case
        make_spatial_constant_comparative_plot(args_list, title=title, single_color=SP_CONSTANT_COLOR, square_mode=False)  # TODO: can set square mode to false for square plots
        make_dimension_prediction_comparative_plot(args_list, title=title, single_color=DIM_PRED_COLOR, square_mode=False)
        make_gram_matrix_analysis_comparative_plot(args_list, title=title, single_color=EIGENVALUES_COLOR, square_mode=True)
        plt.show()

if __name__ == "__main__":

    ### This function is a simplified version of what comes below
    dataset_type = 'snake_latticecomparison'  # simulation, pixelgen, dna_mic, wei_sqbip, swissroll, snake_latticecomparison
    comparative_plots(dataset_type=dataset_type, show_plots=False)

    ### Below:


    # what_to_run = "simulation"  # simulation or experimental
    #
    #
    # if what_to_run == "simulation":
    #     ## Simulation with False Edges
    #     proximity_mode = "delaunay_corrected"
    #     args_list = generate_several_graphs(from_one_graph=True, proximity_mode=proximity_mode)
    #     title = f"False Edge Comparison v2 {proximity_mode}"
    #
    # elif what_to_run == "experimental":
    #     ### Experimental
    #     # pixelgen_processed_edgelist_Sample04_Raji_Rituximab_treated_cell_3_RCVCMP0001806.csv
    #     # pixelgen_example_graph.csv
    #
    #     ### All experimental data
    #     # edge_list_titles_dict = {"weinstein_data_corrected_february.csv": ('W', [5, 10, 15]),
    #     #                     "pixelgen_processed_edgelist_Sample04_Raji_Rituximab_treated_cell_3_RCVCMP0001806.csv": ('PXL', None),
    #     #                     "subgraph_8_nodes_160_edges_179_degree_2.24.pickle": ('HL-S', None),
    #     #                     "subgraph_0_nodes_2053_edges_2646_degree_2.58.pickle": ('HL-E', None)}
    #
    #     # ### Just Weinstein's
    #     # edge_list_titles_dict = {"weinstein_data_corrected_february.csv": [5, 10, 15],
    #     #                          }
    #
    #     # # Weinstein subgraphs with quantile 0.15
    #     # edge_list_titles_dict = {
    #     # "weinstein_data_corrected_february_original_image_subgraphs_quantile=0.15.png_12893_subgraph_1.csv": ('S1', None),
    #     # "weinstein_data_corrected_february_original_image_subgraphs_quantile=0.15.png_3796_subgraph_2.csv": ('S2', None),
    #     # "weinstein_data_corrected_february_original_image_subgraphs_quantile=0.15.png_2211_subgraph_3.csv": ('S3', None),
    #     # "weinstein_data_corrected_february_original_image_subgraphs_quantile=0.15.png_1880_subgraph_4.csv": ('S4', None),
    #     # "weinstein_data_corrected_february_original_image_subgraphs_quantile=0.15.png_1156_subgraph_5.csv": ('S5', None),
    #     # }
    #
    #     # # Pixelgen different datasets
    #     # title_experimental = "MPX 1"  # "Experimental Comparison"
    #     # edge_list_titles_dict = {
    #     #     "pixelgen_processed_edgelist_Sample04_Raji_Rituximab_treated_cell_3_RCVCMP0001806.csv": ('Raji', None),
    #     #     "pixelgen_processed_edgelist_Sample07_pbmc_CD3_capped_cell_3_RCVCMP0000344.csv": ('CD3', None),
    #     #     "pixelgen_example_graph.csv": ('Uro', None)
    #     # }
    #
    #     # Pixelgen pbmc dataset good, bad, ugly (different gradients of spatial coherence)
    #     title_experimental = "MPX" # "Experimental Comparison"
    #     edge_list_titles_dict = {
    #         "Sample01_human_pbmcs_unstimulated_component_RCVCMP0001392_edgelist.csv": ('PBMC 1', None),
    #         "Sample01_human_pbmcs_unstimulated_component_RCVCMP0002024_edgelist.csv": ('PBMC 2', None),
    #         "Sample01_human_pbmcs_unstimulated_component_RCVCMP0000120_edgelist.csv": ('PBMC 3', None)
    #     }
    #
    #     # # # Weinstein different thresholds
    #     # title_experimental = "DNA_Mic"
    #     # threshold_list = [1, 3, 6]
    #     # edge_list_titles_dict = {"weinstein_data_corrected_february.csv": ('DNA_M', threshold_list)}
    #     # title = title_experimental
    #     # args_list = generate_experimental_graphs(edge_list_titles_dict=edge_list_titles_dict)
    #
    #
    #     # # # Different proximity modes
    #     # title_experimental = "simulation_various_prox_modes_with_us"
    #     #
    #     # # with colors:
    #     # edge_list_titles_dict = {
    #     #     "edge_list_us_counties.csv": ('US', None, '#8da0cb'),
    #     #     "edge_list_N=1000_dim=2_distance_decay_k=200_q=0.01.csv": ('Decay 1', None, '#440154'),
    #     #     "edge_list_N=1000_dim=2_distance_decay_k=200_q=0.02.csv": ('Decay 2', None, '#31688e'),
    #     #     "edge_list_N=1000_dim=2_distance_decay_k=200_q=0.03.csv": ('Decay 3', None, '#35b779'),
    #     #     # "edge_list_N=1000_dim=2_distance_decay_k=200_q=0.04.csv": ('Decay 4', None, '#fde725'),
    #     #     "edge_list_N=1000_dim=2_knn_k=10.csv": ('Uni 2D', None, '#fc8d62'),
    #     #     "edge_list_N=1000_dim=2_knn_bipartite_k=10.csv": ('Bip 2D', None, '#66c2a5'),
    #     #     "edge_list_N=1000_dim=3_knn_k=10.csv": ('Uni 3D', None, '#e78ac3'),
    #     #     "edge_list_N=1000_dim=3_knn_bipartite_k=10.csv": ('Bip 3D', None, '#8da0cb'),
    #     #
    #     #
    #     # }
    #
    #
    #     title = title_experimental
    #     args_list = generate_experimental_graphs(edge_list_titles_dict=edge_list_titles_dict, add_2d_simulation=True)
    #     # args_list = generate_experimental_graphs(edge_list_titles_dict=edge_list_titles_dict, add_2d_simulation=True)
    #
    # else:
    #     raise ValueError("what_to_run must be 'simulation' or 'experimental'")
    #
    # tri_color_mode = True
    # # square_mode = True
    # if tri_color_mode:
    #     sp_constant_color = "#009ADE" # "#00CD6C"
    #     dim_pred_color = "#009ADE" #"#F28522"
    #     eigenvalues_color = "#009ADE"
    # else:
    #     sp_constant_color = None
    #     dim_pred_color = None
    #     eigenvalues_color = None
    #
    # ## Comparative Pipeline
    # make_spatial_constant_comparative_plot(args_list, title=title, single_color=sp_constant_color, square_mode=False)
    # make_dimension_prediction_comparative_plot(args_list, title=title, single_color=dim_pred_color, square_mode=False)
    # make_gram_matrix_analysis_comparative_plot(args_list, title=title, single_color=eigenvalues_color, square_mode=True)
