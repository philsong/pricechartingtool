#!/usr/bin/env python3
##############################################################################
# Description:
#
#   This takes a generic ephemeris spreadsheet as produced by
#   createGenericEphemerisSpreadsheet.py and does the work to add
#   2-planet combinations, for both geocentric and heliocentric.
#
#   Formula used for both geocentric and heliocentric calculations of
#   2-planet cycles is:
# 
#       (faster planet) + 360 - (slower planet).
#
#   Adjustments are required periodically when there is a 'gap' in
#   the calculated value for the planet combination.
# 
# Usage:
#
#   1) As long as there have been no modifications to the script that
#   produces the input CSV file, then the Global Variables are correct
#   by default.  Otherwise, the variables will need to be tweaked so
#   that it corresponds correctly with the input CSV file, and the
#   columns in that file.
#
#   2) Simply run the script from the directory:
#
#      python3 makeFilledMasterEphemeris_2p.py
#
##############################################################################

# For obtaining current directory path information, and creating directories
import os
import sys 
import errno

# For dates.
#import datetime

# For logging.
import logging

# For math.floor()
#import math

##############################################################################
# Global variables

# Input CSV file.  See the BA ACCE5S lesson document for details.
inputFilename = "/home/rluu/programming/pricechartingtool/master/misc/EphemerisGeneration/cycleHuntingGeneric/generic_daily_ephemeris_nyc_noon.csv"

# Ouptut CSV file.  This is the CSV file with all the calculations completed, per the homework.  
outputFilename = "/home/rluu/programming/pricechartingtool/master/misc/EphemerisGeneration/cycleHuntingGeneric/master_2p_ephemeris_nyc_noon.csv"

# Lines to skip in the input file.
linesToSkip = 1

# Dictionary for input column values for each planet.
# Cell values in these columns are in range [0, 360).
planetGeocentricLongitudeColumn = \
{
    "Sun"           : 18,
    "Moon"          : 19,
    "Mercury"       : 20,
    "Venus"         : 21,
    "Mars"          : 22,
    "Jupiter"       : 23,
    "Saturn"        : 24,
    "Uranus"        : 25,
    "Neptune"       : 26,
    "Pluto"         : 27,
    "TrueNorthNode" : 28,
    "Chiron"        : 29,
    "Isis"          : 30,
  }

# Dictionary for input column values for each planet.
# Cell values in these columns are in range [0, 360).
planetHeliocentricLongitudeColumn = \
{
    "Mercury" : 55,
    "Venus"   : 56,
    "Earth"   : 57,
    "Mars"    : 58,
    "Jupiter" : 59,
    "Saturn"  : 60,
    "Uranus"  : 61,
    "Neptune" : 62,
    "Pluto"   : 63,
    "Chiron"  : 64,
    "Isis"    : 65,
  }


# For logging.
logging.basicConfig(format='%(levelname)s: %(message)s')
moduleName = globals()['__name__']
log = logging.getLogger(moduleName)
#log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)

##############################################################################

def shutdown(rc):
    """Exits the script, but first flushes all logging handles, etc."""
    
    # Close the Ephemeris so it can do necessary cleanups.
    #Ephemeris.closeEphemeris()
    
    logging.shutdown()
    
    sys.exit(rc)


def doCalculationsForColumn(listOfDataValues,
                            planetColumn):
    """Calculations for single-planet movement.  This method can work for
    both geocentric and heliocentric planet longitude.
    The data values computed are for a column of data in the spreadsheet.
    
    The data in this column is the planet longitude such that the
    values have a 360 degrees added each time the longitude crosses 0 from
    below to above, and 360 degrees removed each time the longitude crosses
    0 from above to below.  That way the formula can work for both
    geocentric and heliocentric longitudes.

    The calculated value is placed as text into 'listOfDataValues' in an
    appended column.

    Arguments:
    listOfDataValues - list of lists.  Each item in the list is a row of data.

    planetColumn - int value holding the column number (index value)
                   of the planet to do calculations for.  Input values are
                   read from this column.
    
    Returns:
    Reference to the modified 'listOfDataValues'.
    """
    
    # Holds the calculated value for the previous row.
    # This is needed so we can determine if we crossed 360 degrees,
    # and in what direction we crossed it.
    prevCalculatedValue = None
    
    # Values increasing or decreasing day to day, should not exceed this value.
    maximumIncrement = 330

    
    for i in range(len(listOfDataValues)):

        log.debug("Curr timestamp is: {}".format(listOfDataValues[i][0]))
        
        planetLongitude = float(listOfDataValues[i][planetColumn])
        
        log.debug("planetLongitude == {}".format(planetLongitude))
        
        currCalculatedValue = planetLongitude
        
        log.debug("prevCalculatedValue == {}".format(prevCalculatedValue))
        log.debug("currCalculatedValue == {}".format(currCalculatedValue))
        
        # See if we need to make any adjustments to the calculated value.
        if prevCalculatedValue == None:
            # No need for any adjustment.
            pass
            
        elif prevCalculatedValue < currCalculatedValue - maximumIncrement:
            # Adjustment required.
            while prevCalculatedValue < currCalculatedValue - maximumIncrement:
                currCalculatedValue -= 360.0
            
        elif prevCalculatedValue >= currCalculatedValue + maximumIncrement:
            # Adjustment required.
            while prevCalculatedValue >= currCalculatedValue + maximumIncrement:
                currCalculatedValue += 360.0

        else:
            # Adjustment not required.
            pass

        log.debug("After adj.: prevCalculatedValue == {}".\
                  format(prevCalculatedValue))
        log.debug("After adj.: currCalculatedValue == {}".\
                  format(currCalculatedValue))
        

        # Any required adjustments should have now been made.
        
        # Store the result as text.
        listOfDataValues[i].append("{}".format(currCalculatedValue))
        
        # Save the calculated value for the next iteration.
        prevCalculatedValue = currCalculatedValue
        currCalculatedValue = None
        
    return listOfDataValues

    
def doCalculationsForColumns(listOfDataValues,
                             fasterPlanetColumn,
                             slowerPlanetColumn):
    """Does a calculation for a 2-planet combination.  This function
    works for both geocentric and heliocentric.

    The generic formula used is:
    
      (faster planet) + 360 - (slower planet).

    The result is then placed as text into 'listOfDataValues' in an
    appended column.

    The data in this column is the 2-planet longitude calculation such
    that the values have a 360 degrees added each time the computed
    longitude value crosses 0 from below to above, and 360 degrees
    removed each time the computed longitude value crosses 0 from
    above to below.  That way the formula can work for both
    geocentric and heliocentric.

    Arguments:
    listOfDataValues - list of lists.  Each item in the list is a row of data.

    fasterPlanetColumn - int value holding the column number (index value)
                         of the faster-moving planet.  Input values are
                         read from this column.
    
    slowerPlanetColumn - int value holding the column number (index value)
                         of the faster-moving planet.  Input values are
                         read from this column.
    
    Returns:
    Reference to the modified 'listOfDataValues'.
    """
    
    # Holds the calculated value for the previous row.
    # This is needed so we can determine if we crossed 360 degrees,
    # and in what direction we crossed it.
    prevCalculatedValue = None
    
    # Values increasing or decreasing day to day, should not exceed this value.
    maximumIncrement = 330


    
    for i in range(len(listOfDataValues)):

        log.debug("Curr timestamp is: {}".format(listOfDataValues[i][0]))
        
        fasterPlanetLongitude = float(listOfDataValues[i][fasterPlanetColumn])
        slowerPlanetLongitude = float(listOfDataValues[i][slowerPlanetColumn])

        log.debug("fasterPlanetLongitude == {}".format(fasterPlanetLongitude))
        log.debug("slowerPlanetLongitude == {}".format(slowerPlanetLongitude))
        
        currCalculatedValue = \
            fasterPlanetLongitude + 360 - slowerPlanetLongitude
        
        log.debug("prevCalculatedValue == {}".format(prevCalculatedValue))
        log.debug("currCalculatedValue == {}".format(currCalculatedValue))
        
        # See if we need to make any adjustments to the calculated value.
        if prevCalculatedValue == None:
            # No need for any adjustment.
            pass
            
        elif prevCalculatedValue < currCalculatedValue - maximumIncrement:
            # Adjustment required.
            while prevCalculatedValue < currCalculatedValue - maximumIncrement:
                currCalculatedValue -= 360.0
            
        elif prevCalculatedValue >= currCalculatedValue + maximumIncrement:
            # Adjustment required.
            while prevCalculatedValue >= currCalculatedValue + maximumIncrement:
                currCalculatedValue += 360.0

        else:
            # Adjustment not required.
            pass

        log.debug("After adj.: prevCalculatedValue == {}".\
                  format(prevCalculatedValue))
        log.debug("After adj.: currCalculatedValue == {}".\
                  format(currCalculatedValue))
        

        # Any required adjustments should have now been made.
        
        # Store the result as text.
        listOfDataValues[i].append("{}".format(currCalculatedValue))
        
        # Save the calculated value for the next iteration.
        prevCalculatedValue = currCalculatedValue
        currCalculatedValue = None
        
    return listOfDataValues

##############################################################################

# Holds the header line of the input file.  We will use this header
# line in the output file.
headerLine = ""

# List of lists.  Each item in this list is a list containing the
# fields of text of the input CSV file.
listOfDataValues = []


# Read in the input file:
log.info("Reading from input file: '{}' ...".format(inputFilename))
try:
    with open(inputFilename, "r") as f:
        i = 0
        for line in f:
            line = line.strip()
            if line == "":
                # Empty line, do nothing for thi sline.
                # Go to next line.
                i += 1
            elif i < linesToSkip:
                # Header line.
                headerLine = line
                i += 1
            else:
                # Normal data line.
                dataValues = line.split(",")
                listOfDataValues.append(dataValues)
                i += 1
        
except IOError as e:
    errStr = "I/O Error while trying to read file '" + \
             inputFilename + "':" + os.linesep + str(e)
    log.error(errStr)
    shutdown(1)


# Do each planet combination.
log.info("Doing planet calculations...")

# G.Moon
columnName = "G.Moon"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Moon"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Mercury
columnName = "G.Mercury"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Mercury"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Venus
columnName = "G.Venus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Venus"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Sun
columnName = "G.Sun"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Sun"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Mars
columnName = "G.Mars"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Mars"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Jupiter
columnName = "G.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.TrueNorthNode
columnName = "G.TrueNorthNode"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Saturn
columnName = "G.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Chiron
columnName = "G.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Uranus
columnName = "G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Neptune
columnName = "G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Pluto
columnName = "G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Isis
columnName = "G.Isis"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetGeocentricLongitudeColumn["Isis"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Mercury
columnName = "H.Mercury"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Mercury"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Venus
columnName = "H.Venus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Venus"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Earth
columnName = "H.Earth"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Earth"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Mars
columnName = "H.Mars"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Mars"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Jupiter
columnName = "H.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Saturn
columnName = "H.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Chiron
columnName = "H.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Uranus
columnName = "H.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Neptune
columnName = "H.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Pluto
columnName = "H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# H.Isis
columnName = "H.Isis"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
planetColumn = planetHeliocentricLongitudeColumn["Isis"]
listOfDataValues = doCalculationsForColumn(listOfDataValues,
                                           planetColumn)

# G.Moon/G.Mercury
columnName = "G.Moon/G.Mercury"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Moon"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Moon/G.Venus
columnName = "G.Moon/G.Venus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Moon"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Moon/G.Sun
columnName = "G.Moon/G.Sun"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Moon"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Moon/G.Mars
columnName = "G.Moon/G.Mars"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Moon"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Moon/G.Jupiter
columnName = "G.Moon/G.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Moon"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Moon/G.TrueNorthNode
columnName = "G.Moon/G.TrueNorthNode"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Moon"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Moon/G.Saturn
columnName = "G.Moon/G.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Moon"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Moon/G.Uranus
columnName = "G.Moon/G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Moon"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.Venus
columnName = "G.Mercury/G.Venus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.Sun
columnName = "G.Mercury/G.Sun"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.Mars
columnName = "G.Mercury/G.Mars"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.Jupiter
columnName = "G.Mercury/G.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.TrueNorthNode
columnName = "G.Mercury/G.TrueNorthNode"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.Saturn
columnName = "G.Mercury/G.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.Chiron
columnName = "G.Mercury/G.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.Uranus
columnName = "G.Mercury/G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.Neptune
columnName = "G.Mercury/G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mercury/G.Pluto
columnName = "G.Mercury/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.Mercury/G.Isis
#columnName = "G.Mercury/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Mercury"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# G.Venus/G.Sun
columnName = "G.Venus/G.Sun"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Venus/G.Mars
columnName = "G.Venus/G.Mars"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Venus/G.Jupiter
columnName = "G.Venus/G.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Venus/G.TrueNorthNode
columnName = "G.Venus/G.TrueNorthNode"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Venus/G.Saturn
columnName = "G.Venus/G.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Venus/G.Chiron
columnName = "G.Venus/G.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Venus/G.Uranus
columnName = "G.Venus/G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Venus/G.Neptune
columnName = "G.Venus/G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Venus/G.Pluto
columnName = "G.Venus/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.Venus/G.Isis
#columnName = "G.Venus/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Venus"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# G.Sun/G.Mars
columnName = "G.Sun/G.Mars"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Sun/G.Jupiter
columnName = "G.Sun/G.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Sun/G.TrueNorthNode
columnName = "G.Sun/G.TrueNorthNode"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Sun/G.Saturn
columnName = "G.Sun/G.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Sun/G.Chiron
columnName = "G.Sun/G.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Sun/G.Uranus
columnName = "G.Sun/G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Sun/G.Neptune
columnName = "G.Sun/G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Sun/G.Pluto
columnName = "G.Sun/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.Sun/G.Isis
#columnName = "G.Sun/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Sun"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# G.Mars/G.Jupiter
columnName = "G.Mars/G.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mars/G.TrueNorthNode
columnName = "G.Mars/G.TrueNorthNode"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mars/G.Saturn
columnName = "G.Mars/G.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mars/G.Chiron
columnName = "G.Mars/G.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mars/G.Uranus
columnName = "G.Mars/G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mars/G.Neptune
columnName = "G.Mars/G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Mars/G.Pluto
columnName = "G.Mars/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.Mars/G.Isis
#columnName = "G.Mars/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Mars"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# G.Jupiter/G.TrueNorthNode
columnName = "G.Jupiter/G.TrueNorthNode"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Jupiter/G.Saturn
columnName = "G.Jupiter/G.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Jupiter/G.Chiron
columnName = "G.Jupiter/G.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Jupiter/G.Uranus
columnName = "G.Jupiter/G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Jupiter/G.Neptune
columnName = "G.Jupiter/G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Jupiter/G.Pluto
columnName = "G.Jupiter/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.Jupiter/G.Isis
#columnName = "G.Jupiter/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Jupiter"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# G.TrueNorthNode/G.Saturn
columnName = "G.TrueNorthNode/G.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.TrueNorthNode/G.Chiron
columnName = "G.TrueNorthNode/G.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.TrueNorthNode/G.Uranus
columnName = "G.TrueNorthNode/G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.TrueNorthNode/G.Neptune
columnName = "G.TrueNorthNode/G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.TrueNorthNode/G.Pluto
columnName = "G.TrueNorthNode/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.TrueNorthNode/G.Isis
#columnName = "G.TrueNorthNode/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["TrueNorthNode"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# G.Saturn/G.Chiron
columnName = "G.Saturn/G.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Saturn/G.Uranus
columnName = "G.Saturn/G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Saturn/G.Neptune
columnName = "G.Saturn/G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Saturn/G.Pluto
columnName = "G.Saturn/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.Saturn/G.Isis
#columnName = "G.Saturn/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Saturn"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# G.Chiron/G.Uranus
columnName = "G.Chiron/G.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Chiron/G.Neptune
columnName = "G.Chiron/G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Chiron/G.Pluto
columnName = "G.Chiron/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.Chiron/G.Isis
#columnName = "G.Chiron/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Chiron"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# G.Uranus/G.Neptune
columnName = "G.Uranus/G.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# G.Uranus/G.Pluto
columnName = "G.Uranus/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.Uranus/G.Isis
#columnName = "G.Uranus/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Uranus"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# G.Neptune/G.Pluto
columnName = "G.Neptune/G.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
slowerPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## G.Neptune/G.Isis
#columnName = "G.Neptune/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Neptune"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

## G.Pluto/G.Isis
#columnName = "G.Pluto/G.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetGeocentricLongitudeColumn["Pluto"]
#slowerPlanetColumn = planetGeocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# H.Mercury/H.Venus
columnName = "H.Mercury/H.Venus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mercury/H.Earth
columnName = "H.Mercury/H.Earth"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mercury/H.Mars
columnName = "H.Mercury/H.Mars"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mercury/H.Jupiter
columnName = "H.Mercury/H.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mercury/H.Chiron
columnName = "H.Mercury/H.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mercury/H.Saturn
columnName = "H.Mercury/H.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mercury/H.Uranus
columnName = "H.Mercury/H.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mercury/H.Neptune
columnName = "H.Mercury/H.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mercury/H.Pluto
columnName = "H.Mercury/H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## H.Mercury/H.Isis
#columnName = "H.Mercury/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mercury"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# H.Venus/H.Earth
columnName = "H.Venus/H.Earth"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Venus/H.Mars
columnName = "H.Venus/H.Mars"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Venus/H.Jupiter
columnName = "H.Venus/H.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Venus/H.Chiron
columnName = "H.Venus/H.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Venus/H.Saturn
columnName = "H.Venus/H.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Venus/H.Uranus
columnName = "H.Venus/H.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Venus/H.Neptune
columnName = "H.Venus/H.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Venus/H.Pluto
columnName = "H.Venus/H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## H.Venus/H.Isis
#columnName = "H.Venus/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Venus"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# H.Earth/H.Mars
columnName = "H.Earth/H.Mars"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Earth/H.Jupiter
columnName = "H.Earth/H.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Earth/H.Chiron
columnName = "H.Earth/H.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Earth/H.Saturn
columnName = "H.Earth/H.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Earth/H.Uranus
columnName = "H.Earth/H.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Earth/H.Neptune
columnName = "H.Earth/H.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Earth/H.Pluto
columnName = "H.Earth/H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## H.Earth/H.Isis
#columnName = "H.Earth/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Earth"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# H.Mars/H.Jupiter
columnName = "H.Mars/H.Jupiter"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mars/H.Chiron
columnName = "H.Mars/H.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mars/H.Saturn
columnName = "H.Mars/H.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mars/H.Uranus
columnName = "H.Mars/H.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mars/H.Neptune
columnName = "H.Mars/H.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Mars/H.Pluto
columnName = "H.Mars/H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## H.Mars/H.Isis
#columnName = "H.Mars/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Mars"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# H.Jupiter/H.Chiron
columnName = "H.Jupiter/H.Chiron"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Jupiter/H.Saturn
columnName = "H.Jupiter/H.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Jupiter/H.Uranus
columnName = "H.Jupiter/H.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Jupiter/H.Neptune
columnName = "H.Jupiter/H.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Jupiter/H.Pluto
columnName = "H.Jupiter/H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## H.Jupiter/H.Isis
#columnName = "H.Jupiter/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Jupiter"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# H.Chiron/H.Saturn
columnName = "H.Chiron/H.Saturn"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Chiron/H.Uranus
columnName = "H.Chiron/H.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Chiron/H.Neptune
columnName = "H.Chiron/H.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Chiron/H.Pluto
columnName = "H.Chiron/H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## H.Chiron/H.Isis
#columnName = "H.Chiron/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Chiron"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# H.Saturn/H.Uranus
columnName = "H.Saturn/H.Uranus"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Saturn/H.Neptune
columnName = "H.Saturn/H.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Saturn/H.Pluto
columnName = "H.Saturn/H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## H.Saturn/H.Isis
#columnName = "H.Saturn/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Saturn"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# H.Uranus/H.Neptune
columnName = "H.Uranus/H.Neptune"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

# H.Uranus/H.Pluto
columnName = "H.Uranus/H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## H.Uranus/H.Isis
#columnName = "H.Uranus/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Uranus"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

# H.Neptune/H.Pluto
columnName = "H.Neptune/H.Pluto"
headerLine += "," + columnName
log.info("Calculating data for column: {}".format(columnName))
fasterPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
slowerPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
listOfDataValues = doCalculationsForColumns(listOfDataValues,
                                            fasterPlanetColumn,
                                            slowerPlanetColumn)

## H.Neptune/H.Isis
#columnName = "H.Neptune/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Neptune"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)

## H.Pluto/H.Isis
#columnName = "H.Pluto/H.Isis"
#headerLine += "," + columnName
#log.info("Calculating data for column: {}".format(columnName))
#fasterPlanetColumn = planetHeliocentricLongitudeColumn["Pluto"]
#slowerPlanetColumn = planetHeliocentricLongitudeColumn["Isis"]
#listOfDataValues = doCalculationsForColumns(listOfDataValues,
#                                            fasterPlanetColumn,
#                                            slowerPlanetColumn)



# Write to output file.
log.info("Writing to output file: '{}' ...".format(outputFilename))
try:
    with open(outputFilename, "w", encoding="utf-8") as f:
        endl = "\n"
        f.write(headerLine + endl)
        
        for rowData in listOfDataValues:
            line = ""
            for i in range(len(rowData)):
                line += rowData[i] + ","

            # Remove trailing comma.
            line = line[:-1]

            f.write(line + endl)

except IOError as e:
    errStr = "I/O Error while trying to write file '" + \
             outputFilename + "':" + os.linesep + str(e)
    log.error(errStr)
    shutdown(1)


log.info("Done.")
shutdown(0)
    

##############################################################################
