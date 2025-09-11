# Network Spatial Coherence
How good is your network? This package measures the spatial coherence of a network—how closely it resembles a physical network—. Additionally, it can reconstruct the network's original positions in space using the STRND algorithm. Networks can be simulated (if you don't have any) or imported, and weighted and bipartite networks are supported. For details, see [Spatial Coherence](https://www.biorxiv.org/content/10.1101/2024.05.12.593725v1.abstract) and [STRND](https://pubs.rsc.org/en/content/articlehtml/2023/nr/d2nr05435c) papers.

## Features
- Analyze the spatial coherence of a network
- Reconstruct images from purely network information - like drawing a country by only knowing which train stations are connected
- Efficient graph loading and processing (sparse matrices)
- Handles simulated graphs, custom graphs, unweighted graphs, weighted graphs, bipartite graphs


## Install
Python 3.11 is reccomended, although older versions should work. See `requirements.txt` for dependencies.

```bash
pip install network_spatial_coherence
```


## Example Results

<table>
  <thead>
    <tr>
      <th></th> <!-- Empty header for the first column -->
      <th>OG Image</th>
      <th>SP Constant</th>
      <th>Net Dim</th>
      <th>Gram Mat</th>
      <th>REC Image</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Coherent Network</strong></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_coherent/1.png" alt="OG Image" width="200"/></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_coherent/2.svg" alt="SP Constant" width="200"/></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_coherent/3.svg" alt="Net Dim" width="200"/></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_coherent/4.svg" alt="Gram Mat" width="200"/></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_coherent/5.png" alt="REC Image" width="200"/></td>
    </tr>
    <tr>
      <td><strong>Incoherent Network</strong></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_incoherent/1.png" alt="OG Image" width="200"/></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_incoherent/2.svg" alt="SP Constant" width="200"/></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_incoherent/3.svg" alt="Net Dim" width="200"/></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_incoherent/4.svg" alt="Gram Mat" width="200"/></td>
      <td><img src="./network_spatial_coherence/example_plots/spatially_incoherent/5.png" alt="REC Image" width="200"/></td>
    </tr>
  </tbody>
</table>

## Quick Intro
For a quick introduction refer to [Usage and Examples](./network_spatial_coherence/markdown_files/usage.md)!


## Detailed information
- [Notebook](./network_spatial_coherence/notebook/run_synthetic_and_exp_pipeline.ipynb)
- [Directory Structure](./network_spatial_coherence/markdown_files/directory_structure.md)
- [GraphArgs Configuration](./network_spatial_coherence/markdown_files/graph_args.md)
- [Results Location](./network_spatial_coherence/markdown_files/results.md)

## Interactive Network Viz
- [Interactive Visualization](https://DavidFernandezBonet.github.io/Network_Spatial_Coherence/network_spatial_coherence/viz_3d.html)

## Citation
If you use this method or refer to its concepts in your research, please cite:  

Bonet, D. F., Blumenthal, J. I., Lang, S., Dahlberg, S. K., & Hoffecker, I. T. (2024). *Spatial coherence of DNA barcode networks*. *bioRxiv*. [https://doi.org/10.1101/2024.05.12.593725](https://doi.org/10.1101/2024.05.12.593725)

Bonet, D. F., & Hoffecker, I. T. (2023). *Image recovery from unknown network mechanisms for DNA sequencing-based microscopy*. *Nanoscale, 15*(18), 8153–8157. [https://doi.org/10.1039/D2NR05435C](https://doi.org/10.1039/D2NR05435C)







## Contact
[dfb@kth.se]
