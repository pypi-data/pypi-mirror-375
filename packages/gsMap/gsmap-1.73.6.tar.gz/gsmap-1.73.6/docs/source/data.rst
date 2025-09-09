gsMap Resources Download
=========================

Download gsMap Running Resources
----------------------------------

You can download the necessary resources for running gsMap from the following link:

.. _gsMap running dependencies: https://yanglab.westlake.edu.cn/data/gsMap/gsMap_resource.tar.gz

`gsMap running dependencies <https://yanglab.westlake.edu.cn/data/gsMap/gsMap_resource.tar.gz>`_


- **LD Reference Panel**:

  - The 1000 Genomes Project Phase 3 panel.

- **Gene Annotation**:

  - **GTF File**: Contains the gene transcript coordinates.

  - **Enhancer Data**: Enhancer annotation by each tissue.

- **LDSC Resources**

- **Homologous Gene Transformations Data**:

  - Derived from the biomaRt (V3.18) R package, this data is used to transform gene names across species.

.. note::
   These data are curated to ensure compatibility and ease of use. You can use your own reference panel and gene annotation data, but it is important to ensure that the data is compatible with the gsMap pipeline.

.. _download-example-data:

Download Example Data
-----------------------------------

To illustrate how to use gsMap, we provide some example GWAS and ST data. You can download the example data from the following link:

`gsMap Example Data <https://yanglab.westlake.edu.cn/data/gsMap/gsMap_example_data.tar.gz>`_

.. _data-availability:

Data Availability
-------------------
.. list-table::
   :header-rows: 1

   * - Category
     - Description
   * - GWAS Data
     - - The 110 GWAS summary statistics used in the paper in in Supplementary Table.1
       - You could download the GWAS summary statistics from the GWAS catalog: `https://www.ebi.ac.uk/gwas/ <https://www.ebi.ac.uk/gwas/>`_
   * - ST Data
     - - Mouse embryo and brain ST datasets: `https://db.cngb.org/search/project/CNP0001543/ <https://db.cngb.org/search/project/CNP0001543/>`_
       - Human embryo ST datasets: `https://ngdc.cncb.ac.cn/gsa-human/browse/HRA005567 <https://ngdc.cncb.ac.cn/gsa-human/browse/HRA005567>`_
       - Macaque cortex ST datasets: `https://db.cngb.org/search/project/CNP0002035/ <https://db.cngb.org/search/project/CNP0002035/>`_
       - Human DLPFC ST datasets: `https://research.libd.org/globus/ <https://research.libd.org/globus/>`_
   * - LDSC Data
     - - LD reference panel from 1000 Genomes Project Phase 3: `ftp://ftp.1000genomes.ebi.ac.uk <ftp://ftp.1000genomes.ebi.ac.uk>`_
       - LDSC baseline annotations: `https://data.broadinstitute.org/alkesgroup/LDSCORE <https://data.broadinstitute.org/alkesgroup/LDSCORE>`_
   * - Enhancer Data
     - - Enhancer data from ABC and Roadmap are curated and available at: `https://github.com/kkdey/GSSG/ <https://github.com/kkdey/GSSG/>`_
