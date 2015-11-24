User guide
==========

To create phase maps from elemental maps, the user have to create a python script for each data set.
The script should contain three main parts:

#. Read the input data (elemental maps)
#. Display elemental maps
#. Create each phase.
#. Create phase maps.

This guide explain the basic of these three parts, more advance features are describe in
the :ref:`api-documentation-label`.

Read the input data
-------------------

First you need to create a :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis` object using a filepath to save
the data into an HDF5 file::

   from pyxrayphasemap.analysis import PhaseAnalysis
   project_filepath = r"D:\results\experiments\1-LFS4-2.hdf5"
   phase_analysis = PhaseAnalysis(project_filepath)

The `HDF5 <https://www.hdfgroup.org/HDF5>`_ is a data model, library, and file format for storing and managing
data and it is fast for large amount of data like x-ray maps. `HDFView <https://www.hdfgroup.org/products/java/release/download.html>`_
viewer is available to read HDF5 file, usefull when developing a script to see which data is in the file.

Next you add data to the :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis` object by specifiy the type of data,
a label and a filepath to the data::

    dataType = DATA_TYPE_INTENSITY_DECONVOLUTION
    label = "C"
    filepath = r"D:\results\experiments\1-LFS4-2_countsDeconvolution_C.txt"
    phase_analysis.readElementData(data_type, label, filepath)

You are going to use the data type and label later to define each phase.
The following data type are define, but you can define your own data type:

* :py:const:`~pyxrayphasemap.analysis.DATA_TYPE_ATOMIC_NORMALIZED`
* :py:const:`~pyxrayphasemap.analysis.DATA_TYPE_WEIGHT_NORMALIZED`
* :py:const:`~pyxrayphasemap.analysis.DATA_TYPE_INTENSITY_DECONVOLUTION`
* :py:const:`~pyxrayphasemap.analysis.DATA_TYPE_RAW_INTENSITY`
* :py:const:`~pyxrayphasemap.analysis.DATA_TYPE_NET_INTENSITY`

To add more than one file you can use a loop::

    labels = ['C', 'Fe', 'O', 'Si']
    basepath = r"D:\results\experiments\20150423"
    for label in labels:
        filename = "1-LFS4-2_countsDeconvolution_%s.txt" % (label)
        filepath = os.path.join(basepath, filename)
        phase_analysis.readElementData(dataType, label, filepath)

You can also add a micrograph as data::

   filepath = r"D:\results\experiments\1-LFS4-2_countsDeconvolution_SE.txt"
   phase_analysis.readMicrographData(DATA_TYPE_SE, filepath)

The following micrograph data are define, but you can define your own data type as the first parameter is just
a string label:

* :py:const:`~pyxrayphasemap.analysis.DATA_TYPE_SE`
* :py:const:`~pyxrayphasemap.analysis.DATA_TYPE_BSE`

TODO import raw file

Display elemental maps
----------------------

To help define each phase you can display each elemental map and micrograph with an histogram of the pixel intensity.
Using the :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis` object, you can:

* :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis.display_histogram_all`
* :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis.save_histogram_all`
* :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis.display_histogram_one`
* :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis.save_histogram_one`

Examples of each method::

    data_type = DATA_TYPE_WEIGHT_NORMALIZED
    label = 'C'
    phase_analysis.display_histogram_one(data_type, label)

    phase_analysis.display_histogram_all()

    figures_path = r"D:\results\experiments\20150423\analysis"
    phase_analysis.save_histogram_one(data_type, label, figures_path)

    phase_analysis.save_histogram_all(figures_path)

All methods take an optional parameter to specify the number of bins used to create the histogram and
the display methods can specify if you want to display the graphic now or later by either calling yourself
:py:class:`~pyxrayphasemap.analysis.PhaseAnalysis.show`::

    data_type = DATA_TYPE_WEIGHT_NORMALIZED
    label = 'C'
    phase_analysis.display_histogram_one(data_type, label, num_bins=100, display_now=True)

    figures_path = r"D:\results\experiments\20150423\analysis"
    phase_analysis.save_histogram_one(data_type, label, figures_path, num_bins=100)

    data_type = DATA_TYPE_WEIGHT_NORMALIZED
    label = 'C'
    phase_analysis.display_histogram_one(data_type, label, num_bins=100, display_now=False)

    phase_analysis.show()

When a graphic is display now, the script stop until you close all graphic windows. Calling :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis.show`
will only show new graphic created after the last display with ``display_now=True``.
