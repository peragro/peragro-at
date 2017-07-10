Welcome to peragro-at's documentation!
===================================

The general process::

                 
                       user requested format-\
                                        ______\______         
         ___________                    |            |
         |          |/---> Asset 1  --->| Transcoder |--> Asset 1 in user requested format
 File -->| Analyzer |----> Asset 2      |____________|
         |__________|\---> Asset 3
               \             /
                \--Metadata-/    
 

Example: A blend file is given to the analyzer, the analyzer looks up the plugin for .blend files by mimetype. The plugin then begins to scan the file, and it will output a list of all blender objects(which from now on will be called assets), the assets are given an internal mimetype of 'x-blender/object' and additional information like face/vertex count, number of materials, etc is scanned and added to the asset as metadata. All this information is stored in the database. Note: at this point we haven't done anything with the file except for having scanned it. An asset is just an unique ID combined with a file reference, a name(unique for that file), an internal mimetype and some metadata!

Now say a user wants asset 1 in CS format, he'd request it with the mimetype 'application/x-crystalspace.library+xml', asset 1 is then looked up in the database, this tells us it has the internal mimetype of 'x-blender/object' , so now we can lookup a transcoder for 'application/x-crystalspace.library+xml' -->'x-blender/object'. The asset is passed to the transcoder plugin, it reads the file, finds the object by name and extracts its data and converts it to the CS format.

.. toctree::
   :maxdepth: 2

   autodoc/peragro-at
   

Analyzers
----------

.. autoclass:: peragro-at.pluginmanager.IAnalyzer
   :members:

.. toctree::
   :maxdepth: 1

   autodoc/peragro-at.analyzers


Transcoders
-----------

.. autoclass:: peragro-at.pluginmanager.ITranscoder
   :members:

Any .py file in the transcoders/ directory will be automatically scanned on startup and registered as a plugin if it has the following requirements: It has a function 'transcode(self, anAsset, aFormat, kwargs)' It has a member dictionary **convert_map** and it has a member dictionary **options_map**

convert_map
***********

This specifies the source and destination mimetypes this transcoder supports. Each entry describes a 'source --> destination'-mapping and is of the format::

"source-mimetype": "destination-mimetype"

or::

"source-mimetype": ["destination-mimetype1", "destination-mimetype2", ...]

Example::

 convert_map = {"image/png" : "image/jpeg", "image/tga" : ["image/jpeg", "image/png"]}

It can convert png to jpeg or convert tga to either jpeg or png.

options_map
***********

This specifies what options/arguments can be given when transcoding an asset. Each entry specifies a source mimetype(corresponding to one in the convert_map) and a dictionary of options; each tuple consists of the option's name and a function used to convert the input to the correct type(all inputs are string).

Example::

 convert_map = {"x-blender/object" : "image/jpeg"}
 options_map = {"x-blender/object" : {'sizex': int, 'sizey': int, 'angley': float, 'cameraType': str, 'cameraAngley': float, 'anglesy': floatArray}}
 

This one renders a blender object to a jpeg, it's options are size(x/y): specifying the width and height of the rendered image. angley: the rotation around the Y axis of the object. cameraType: blender options for camera type, ORTHO or PERSP. cameraAngley: the angle of the camera.

(This transcoder is used for the 2D previews of blender objects in the DAMN interface, it can also be used for sprites for a 2D game(use ortho and a camera angle to get top-down views of the asset)) 

.. toctree::
   :maxdepth: 4

   autodoc/peragro-at.transcoders


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

