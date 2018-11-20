# AVR-method
My Personal KiCAD Library Management Workflow and practices.

## Schematic Symbol Library Specifications
Components should be separated by types into the following categories:
Resistors, Capacitors, Connectors, ICs, and Special.  
#### Symbol Metadata
Schematic symbols contain several kinds of metadata. This metadata is for
making the BOM more informative to the PCB assembler. It also is for keeping
track of part lifecycle, cost, function, and information all in one place, the
part symbol itself. All components have the same metadata fields. This keeps the BOM generation simple and consistent. If  given component does not have entry for one of the metadata fields, simply leave the default value of * in place. In the future I'm going to develop a library management tool for that utilizes this metadata system I've developed over the years.

* Reference
* Value
* Footprint
* Datasheet
* Cost QTY:1
* Cost QTY:1000
* Cost QTY:3000
* Cost QTY:5000
* Cost QTY:10000
* MFR
* MFR#
* Vendor
* Vendor #
* Designer
* Height
* Date Created
* Date Modified
* Lead-Free?
* RoHS Levels
* Mounting
* Pin Count #
* Status
* Tolerance
* Type
* Voltage
* Package
* Component
* \_Value\_
* Management_ID

#### Capacitors
Capacitors are contained within their own sub-library, I keep all types of
capctitors in one library, if you have many capacitors of various types it might
be more helpful to have additional sub libraries but find this makes Schematic
capture even longer.

#### Resistors
Resistors are contained within their own sub-library, all types in one, I only
use SMT resistors so there isn't much variation aside from size.

#### Connectors
All Connectors in one library,

#### ICs (Integrated Circuits)
All ICs in one library, if you have a diverse collection perhaps sublibraries for types, but remember cycling through folders is a waste of time that could be better spent drawring the schematic.

#### Mounting Holes & Fasteners
All mounting holes of all types, holes for screws of various size, standoffs,PEMS, etc.

#### Special
The Special category is for PCB mounted components that are out of the ordinary. These parts don't always have to be electrical. A good example is the lens mount for a camera image sensor that has to be board mounted. Another common example would be fiducials for pick and place assembly alignment.

#### Management ID
The Management ID is a unique alpha numeric string used as an identifier for each component relative to the library as a whole. The number contains the type of component, date created, and a unique 8 digit alpha numeric identifier string.

Example:

CAP-09092018-F8T4YU35

RES-08082018-G94EY76U

ICS-11162018-H8UI9R56

CON-12092018-J8R77GQ9

SPE-07122018-H8U99G03

#### Example of Fields:
![alt text](imgs\ICs-Template.png "ICs Example")
