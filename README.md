# Mill-to-EDM Converter
Autodesk Fusion makes it difficult to write Wire EDM specific NC code, but I can approximate it with a Mill machine and a very thin cutting tool. This script takes the Fusion output and makes it EDM compatible for our FANUC EDM using incremental positioning.

Install the python package pygcode, available here: https://github.com/fragmuffin/pygcode

The included files in the modified_package folder are modified package files, replace the ones in your package directory with these. The changes I made were adding in an M31 code and increasing the precision of how some of the values were being converted.

The script will do a few things in order:

>Iterate through all rows of the input .nc file

>Prefix every floating X and Y command with a cut command (G01)

>Prefix every comment indicating right or left cutter compensation with the appropriate Gcode (G41, G42)

>Add an M31 code to the start of the script

>Add a G40 code to the end of the script

>Use pygcode to parse all of the Gcode commands present in each row

>Remove all Z moves (as milling operations involve Z moves, while we're doing 2D EDM)

>Ensure that the % characters and comments make it into the final file

>Write the final file while discarding all unnecessary Gcodes

>Ensure that the initial rapid move (G0) is still present, as well as maintaining one incremental positioning command (G91) at the start of the script with no repeats

Will add a few more features, maybe potentially to have this act as a post-processing script for Fusion so that it is automatically applied. Would love a script that can just convert a DXF to gcode too.
