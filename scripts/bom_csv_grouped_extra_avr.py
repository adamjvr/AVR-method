#
# KiCad BOM (Bill of Materials) generation script with AVR-KiCAD-Method metadata
#
# This script extends the standard KiCad BOM Python exporter by including
# all "property" fields typically used in the AVR-KiCAD-Method libraries.
# These metadata fields contain manufacturer information, vendor details,
# cost breakdowns, and other descriptive attributes useful in procurement,
# documentation, and lifecycle management.
#
# Output format: CSV (comma-separated values)
#
# Grouping: Components are grouped by Value, Footprint, DNP, and metadata
# Sorting:   By Reference
#
# Each row in the generated CSV corresponds to a unique group of components,
# with fields describing that component type, and the "Reference" column
# showing all reference designators that share those properties.
#
# Example usage from KiCad's BOM generator dialog:
#   python "bom_csv_grouped_extra_avr.py" "%I" "%O.csv"
#

"""
    @package
    Output: CSV (comma-separated)
    Grouped By: Value, Footprint, DNP, specified metadata fields
    Sorted By: Reference
    Fields: #, Reference, Qty, Value, Footprint, DNP, AVR metadata

    Command line usage:
        python "pathToFile/bom_csv_grouped_extra_avr.py" "%I" "%O.csv"

    - %I is replaced by KiCad with the input netlist filename
    - %O is replaced by KiCad with the chosen output filename
"""

# --------------------------------------------------------------------------
# Import required modules
# --------------------------------------------------------------------------

import kicad_netlist_reader   # KiCad’s Python helper module for reading netlists
import kicad_utils            # Utility functions for file handling and formatting
import csv                    # Python standard library for writing CSV files
import sys                    # For accessing command line arguments

# --------------------------------------------------------------------------
# AVR-KiCAD-Method Metadata Fields
# --------------------------------------------------------------------------
# These correspond to the "property" fields defined inside symbols in the
# AVR-KiCAD-Method library. They include pricing at various quantities,
# manufacturer info, vendor info, environmental compliance, etc.
# If you add new properties to your library, you can extend this list.
# --------------------------------------------------------------------------

avr_fields = [
    "Datasheet",
    "Description",
    "Cost QTY: 1",
    "Cost QTY: 1000",
    "Cost QTY: 2500",
    "Cost QTY: 5000",
    "Cost QTY: 10000",
    "MFR",
    "MFR#",
    "Vendor",
    "Vendor #",
    "Designer",
    "Height",
    "Date Created",
    "Date Modified",
    "Lead-Free ?",
    "RoHS Levels",
    "Mounting",
    "Pin Count #",
    "Status",
    "Tolerance",
    "Type",
    "Voltage",
    "Package",
    "Description_1",
    "_Value_",
    "Management_ID"
]

# --------------------------------------------------------------------------
# Base fields used for grouping and output
# --------------------------------------------------------------------------
# These are always included: the electrical "Value" (e.g., 10k),
# the PCB "Footprint" (e.g., Resistor_SMD:R_0603),
# and the "DNP" (Do Not Populate) flag.
# Together with the AVR metadata, they form the complete field set.
# --------------------------------------------------------------------------

comp_fields = ['Value', 'Footprint', 'DNP'] + avr_fields

# Column headers for the CSV file. These appear in the first row.
# '#' is just an index counter for convenience.
header_names = ['#', 'Reference', 'Qty'] + comp_fields

# --------------------------------------------------------------------------
# Helper function: Retrieve the value of a given field from a component
# --------------------------------------------------------------------------
# This abstracts away the difference between special fields (Value, Footprint,
# DNP, Datasheet) which have dedicated accessors, and user-defined fields
# which are accessed through comp.getField().
# --------------------------------------------------------------------------

def getComponentString(comp, field_name):
    """Return the string value of the requested field from a component object."""

    if field_name == "Value":
        return comp.getValue()           # e.g., "10k"
    elif field_name == "Footprint":
        return comp.getFootprint()       # e.g., "Resistor_SMD:R_0603"
    elif field_name == "DNP":
        return comp.getDNPString()       # e.g., "DNP" or ""
    elif field_name == "Datasheet":
        return comp.getDatasheet()       # e.g., "http://datasheet.url"
    else:
        # All other AVR metadata fields are handled as generic fields
        return comp.getField(field_name)

# --------------------------------------------------------------------------
# Custom component equivalence function
# --------------------------------------------------------------------------
# By default, KiCad groups components only by Value and Footprint.
# Here we override the equality operator so that grouping also takes into
# account the DNP flag and all metadata fields (e.g., MFR, Vendor, etc.).
#
# This ensures that, for example, two resistors of the same value and footprint
# but from different manufacturers (different MFR#) will appear as separate
# rows in the BOM, preventing incorrect consolidation.
# --------------------------------------------------------------------------

def myEqu(self, other):
    """Equivalence function for component grouping with metadata awareness."""

    result = True
    for field_name in comp_fields:
        if getComponentString(self, field_name) != getComponentString(other, field_name):
            result = False
    return result

# Override the __eq__ operator for KiCad component objects
# IMPORTANT: Must be done BEFORE loading the netlist, otherwise the grouping
# will be done with the original (simpler) equivalence function.
kicad_netlist_reader.comp.__eq__ = myEqu

# --------------------------------------------------------------------------
# Load the netlist file provided by KiCad
# --------------------------------------------------------------------------
# sys.argv[1] is the input netlist filename (passed automatically by KiCad).
# If the file cannot be found or parsed, the script will terminate.
# --------------------------------------------------------------------------

net = kicad_netlist_reader.netlist(sys.argv[1])

# --------------------------------------------------------------------------
# Open the output file for writing
# --------------------------------------------------------------------------
# sys.argv[2] is the output CSV filename (passed automatically by KiCad).
# If the file cannot be opened (e.g., permission denied), fallback to stdout.
# --------------------------------------------------------------------------

canOpenFile = True
try:
    f = kicad_utils.open_file_writeUTF8(sys.argv[2], 'w')
except IOError:
    e = "Can't open output file for writing: " + sys.argv[2]
    print(__file__, ":", e, sys.stderr)
    f = sys.stdout
    canOpenFile = False

# --------------------------------------------------------------------------
# Initialize the CSV writer
# --------------------------------------------------------------------------
# We use Python’s csv.writer with:
# - newline terminator = '\n'
# - delimiter = ',' (standard CSV)
# - quotechar = '"' to properly escape values
# - quoting = csv.QUOTE_ALL to ensure all fields are quoted
# --------------------------------------------------------------------------

out = csv.writer(
    f,
    lineterminator='\n',
    delimiter=',',
    quotechar='\"',
    quoting=csv.QUOTE_ALL
)

# Write the header row (field names)
out.writerow(header_names)

# --------------------------------------------------------------------------
# Retrieve all components that should appear in the BOM
# --------------------------------------------------------------------------
# excludeBOM=True ensures that any components explicitly marked as
# "Exclude from BOM" in KiCad will be filtered out here.
# --------------------------------------------------------------------------

components = net.getInterestingComponents(excludeBOM=True)

# Group components according to our custom equivalence operator
grouped = net.groupComponents(components)

# --------------------------------------------------------------------------
# Generate BOM rows
# --------------------------------------------------------------------------
# Each group of equivalent components becomes a row in the CSV.
# - index: a simple row counter
# - refs: comma-separated list of component reference designators (e.g., R1, R2, R3)
# - qty: number of components in the group
# - followed by all field values (Value, Footprint, DNP, metadata, etc.)
# --------------------------------------------------------------------------

index = 1
for group in grouped:
    # Build a list of references in this group
    refs_l = [c.getRef() for c in group]
    refs = ", ".join(refs_l)

    # Pick the first component in the group as representative for field values
    c = group[0]

    # Assemble the row
    row = [index, refs, len(group)]

    # Append all field values in the order defined by comp_fields
    for field_name in comp_fields:
        row.append(getComponentString(c, field_name))

    # Write the row to the CSV
    out.writerow(row)

    # Increment the index counter
    index += 1

# --------------------------------------------------------------------------
# Clean exit if file write failed
# --------------------------------------------------------------------------
if not canOpenFile:
    sys.exit(1)
