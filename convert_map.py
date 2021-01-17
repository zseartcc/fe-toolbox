# Convert between ATC client video map formats
# REQUIRES PYTHON 3.6+ (sorry python2-ers)
#
#
# This script works by converting an entire map into a Python list first:
#   [
#       (lat1, lon1, lat2, lon2, color),
#       (lat1, lon1, lat2, lon2, color),
#       ...
#   ]
#
# Once in this intermediate state, it can be written to any of these formats:
#   VRC diagram
#   vSTARS VideoMap
#   vERAM GeoMap


from tkinter import Tk
from tkinter.filedialog import askopenfile, asksaveasfile
from sys import exit
import re
import os


##########################
# Helper functions
##########################

def pause():
    if os.name == "nt":
        print()
        os.system("pause")
    else:
        input("\nPress Enter to continue . . . ")

def err(msg):
    print(msg)
    pause()
    exit()

def ddToDms(lat: float, lon: float):
    """ Convert coord pair from decimal degrees to Xddd.mm.ss.sss """
    # Get NESW
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    # Make positive
    lat = abs(lat)
    lon = abs(lon)
    # Floor to get degrees
    latD = int(lat)
    lonD = int(lon)
    # Get minutes
    latM = 60*(lat - latD)
    lonM = 60*(lon - lonD)
    # Get seconds
    latS = 60*(latM - int(latM))
    lonS = 60*(lonM - int(lonM))
    # Assemble the strings
    latOut = "%s%03.f.%02.f.%06.3f" % (ns, latD, int(latM), latS)
    lonOut = "%s%03.f.%02.f.%06.3f" % (ew, lonD, int(lonM), lonS)
    return (latOut, lonOut)


##########################
# Map readers
##########################

def readVMGM(text, *, nameTag, getColors):
    """ (Reduces duplicate code) """
    result = []
    mapName = re.search(fr'{nameTag}="([^"]*)"', text)
    lat1s = re.findall(r'StartLat="([^"]*)"', text)
    lon1s = re.findall(r'StartLon="([^"]*)"', text)
    lat2s = re.findall(r'EndLat="([^"]*)"', text)
    lon2s = re.findall(r'EndLon="([^"]*)"', text)
    # Only get colors when told to
    if getColors: colors = re.findall(r'Color="([^"]*)"', text)
    # Note: each list returned by these "re.findall" will be the same size
    # (assuming the VideoMap is formatted correctly)
    for i in range(len(lat1s)):
        # Get lat/lon and color
        lat1, lat2 = lat1s[i], lat2s[i]
        lon1, lon2 = lon1s[i], lon2s[i]
        # Default 'color' to ""
        color = colors[i] if getColors else ""
        result.append((lat1, lon1, lat2, lon2, color))
    # Default mapName to ""
    return mapName.group(1) if mapName else "Untitled Map", result

def readVideoMap(text):
    return readVMGM(text, nameTag="LongName", getColors=True)

def readGeoMap(text):
    return readVMGM(text, nameTag="Description", getColors=False)


##########################
# Map writers
##########################

def writeSct2(file, mapName, coords):
    # Warn user if map name is too long
    if len(mapName) > 26:
        print(repr(mapName) + " is too long (max 26 chars). It will be truncated.")
        pause()
    # Limit to 26 chars and pad with spaces
    file.write(mapName[:26].ljust(26))
    file.write("N000.00.00.000 E000.00.00.000 N000.00.00.000 E000.00.00.000\n")
    for segment in coords:
        lat1, lon1 = ddToDms(float(segment[0]), float(segment[1]))
        lat2, lon2 = ddToDms(float(segment[2]), float(segment[3]))
        # Don't create trailing spaces if no color exists
        color = " "+segment[4] if segment[4] else ''
        file.write(" "*26 + f"{lat1} {lon1} {lat2} {lon2}{color}\n")

def writeVideoMap(file, mapName, coords):
    # Create VideoMap tag (root)
    file.write(f'<VideoMap ShortName="{mapName.strip()[:6]}" LongName="{mapName.strip()}"')
    file.write(' STARSGroup="A" STARSTDMOnly="false" VisibleInList="true">\n')
    # Create empty 'Colors' section
    file.write('  <Colors>\n    <NamedColor Red="" Green="" Blue=""')
    file.write(' Name="Change this line to create colors"/>\n  </Colors>\n')
    # Write Elements
    file.write('  <Elements>\n')
    for segment in coords:
        # Get lat/lon and color
        lat1, lon1 = str(segment[0]), str(segment[1])
        lat2, lon2 = str(segment[2]), str(segment[3])
        color = segment[4]
        # Write Element
        file.write(f'    <Element xsi:type="Line" Color="{color}" StartLon="{lon1}"')
        file.write(f' StartLat="{lat1}" EndLon="{lon2}" EndLat="{lat2}" Style="Solid"')
        file.write(' Thickness="0"/>\n')
    # Close Elements, VideoMap
    file.write("  </Elements>\n</VideoMap>\n")

def writeGeoMap(file, mapName, coords):
    # Create GeoMapObject tag (root)
    file.write(f'<GeoMapObject Description="{mapName.strip()}"')
    file.write(' TdmOnly="false">\n')
    # Create LineDefaults tag
    file.write('  <LineDefaults Bcg="1" Filters="1" Style="Solid" Thickness="1"/>\n')
    # Write Elements
    file.write('  <Elements>\n')
    for segment in coords:
        # Get lat/lon and color
        lat1, lon1 = str(segment[0]), str(segment[1])
        lat2, lon2 = str(segment[2]), str(segment[3])
        color = segment[4]
        # Write Element
        file.write(f'    <Element xsi:type="Line" Filters="" StartLat="{lat1}" StartLon="{lon1}"')
        file.write(f' EndLat="{lat2}" EndLon="{lon2}"/>\n')
    # Close Elements, GeoMapObject
    file.write("  </Elements>\n</GeoMapObject>\n")

def writeAutoCad(file, mapName, coords):
    file.write(f"; {mapName}\n")
    for segment in coords:
        lat1, lon1, lat2, lon2, color = segment
        file.write(f"LINE {lat1},{lon1} {lat2},{lon2}\n")


##########################
# Main
##########################

# (Hide tkinter window)
Tk().withdraw()

#
# Read map
#

# Get input file
print("See file dialog to import video map.")
with askopenfile(title="Import map", filetypes=[("VideoMap/GeoMap","*.xml")]) as f:
    # Exit if nothing selected
    if not f:
        exit()
    inText = f.read()

if "<VideoMap" in inText:
    if "ASDEX" in inText:
        err("vSTARS ASDEX maps are not yet supported.")
    # Read VideoMap
    mapName, coords = readVideoMap(inText)
elif "<GeoMapObject" in inText:
    # Read GeoMap
    mapName, coords = readGeoMap(inText)
else:
    err("Selected file does not appear to be a valid video map.")


#
# Write map
#

# Determine target client
print(f"\nWhich format should I convert '{mapName.strip()}' to?\n")
print("  [1] VRC")
print("  [2] vSTARS")
print("  [3] vERAM")
print("  [4] AutoCAD")
while True:
    choice = input("Press Enter when done: ")
    if choice in ('1','2','3', '4'):
        break

# Write converted map
if choice == '1':
    # Write sct2 diagram
    outFile = asksaveasfile(
        title="Save map",
        filetypes=[("VRC diagrams","*.sct2")],
        defaultextension=".sct2",
        initialfile=mapName)
    if not outFile:
        exit()
    writeSct2(outFile, mapName, coords)
elif choice == '2':
    # Write VideoMap
    outFile = asksaveasfile(
        title="Save map",
        filetypes=[("VideoMap","*.xml")],
        defaultextension=".xml",
        initialfile=mapName + ".xml")
    if not outFile:
        exit()
    writeVideoMap(outFile, mapName, coords)
elif choice == '3':
    # Write GeoMap
    outFile = asksaveasfile(
        title="Save map",
        filetypes=[("GeoMap","*.xml")],
        defaultextension=".xml",
        initialfile=mapName + ".xml")
    if not outFile:
        exit()
    writeGeoMap(outFile, mapName, coords)
elif choice == '4':
    # Write AutoCAD
    outFile = asksaveasfile(
        title="Save map",
        filetypes=[("AutoCAD script","*.scr")],
        defaultextension=".scr",
        initialfile=mapName + ".scr")
    if not outFile:
        exit()
    writeAutoCad(outFile, mapName, coords)

outFile.close()

print("\nCompleted! Be sure to verify the converted map's name and colors.")
print("(For vERAM and vSTARS, also check group and TdmOnly settings.)")
pause()