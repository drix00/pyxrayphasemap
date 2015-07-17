User guide
==========

To create phase maps from elemental maps, the user have to create a python script for each data set.
The script should contain three main parts:

#. Read the input data (elemental maps)
#. Create each phase.
#. Create phase maps.

This guide explain the basic of these three parts, more advance features are describe in the :ref:`api-documentation-label`.

Read the input data
-------------------

First you need to create a :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis` object using a filepath to save the data into an HDF5 file::

   from pyxrayphasemap.analysis import PhaseAnalysis
   project_filepath = r"D:\results\experiments\1-LFS4-2.hdf5"
   phase_analysis = PhaseAnalysis(project_filepath)

Next you add data to the :py:class:`~pyxrayphasemap.analysis.PhaseAnalysis` object by specifiy the type of data, a label and a filepath to the data::

    dataType = DATA_TYPE_INTENSITY_DECONVOLUTION
    label = "C"
    filepath = r"D:\results\experiments\1-LFS4-2_countsDeconvolution_C.txt"
    phase_analysis.readElementData(dataType, label, filepath)

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

The folowwing micrograph data are define, but you can define your own data type:

* :py:const:`~pyxrayphasemap.analysis.DATA_TYPE_SE`
* :py:const:`~pyxrayphasemap.analysis.DATA_TYPE_BSE`

