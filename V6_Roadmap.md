# "V6" RoseLap
## _the future is now_

# Changes

Backend
- Pure python; rewrite everything in web.py
- Pure data; no precompiled plots
-- Should we use databases still? Same DB backend?
- Batcher needs some serious revamping
- Working with any version of python would be good
- One-time import of old data OK? 
- 1D sweeps are just 2D sweeps?
- Do we want a real database? Is a filesystem not sufficient? I don't see a compelling reason to use a DB over a FS here...
-- Other than listing properties of the folder... but then again, a DB + FS hybrid (a la owncloud) could be the right path

Frontend
- Pure data; no precompiled plots
-- Could use d3, or could use Thad's splot
- Detail views on the same area as heat maps
-- Better yet, two detail views side-by-side beneath heatmap
- Bonus: User-friendly study definition

Model Changes
- Rolling resistance
- Proper integration of electric motor options

Overall
- Be better; document what's going on for future use
- Don't be afraid to blow things up and refactor

# Component Definition
*Vehicles*
- are sets of base parameters (complex objects in YAML format)

*Tracks*
- are sets of distance-curvature data (in some format)

*Studies*
- are based on vehicles and tracks (complex objects in YAML format)
- Study database entries have three states: drafting, submitted, running, and finished
- Once a study is submitted, the link to the track and vehicle is broken; the track and vehicle data is imported/stored into the database entry
- Studies can be 'rebased'; the previous study serves as a draft upon which further improvements can be written. In this rebasing, the previous tracks and vehicles can be imported, or left behind in favor of the new dynamically linked ones
*Runs*
- are individual maneuvers around a track 
- Run database entries contain a MD5 hash of the vehicle (as configured) and track
- Collisions are a feature to reduce computational load, not a bug?
*Users* are individual members which have access to particular runs
*Groups* are teams which users can belong to (maybe)

# Primary Database Spec
*Vehicles*
- Name
- Version
- YAML data to provide vehicle parameters
- Date of last edit

*Tracks*
- Name
- Data
- Date of last edit
- Distance (computed from data upon upload) (set to invalid/null if parsing issues)

*Studies*
- Name
- YAML data for study
- sequential id (corresponds to a filesystem folder)
- Date of last edit
- Date of submission (null if unsubmitted)
- Date of completion (null if uncompleted)
- Number of total runs
- Number of completed runs
- Error log

# Study Database Spec
Format: sqlite3? JSON? (if it were JSON, it could be sent directly to the client...)

*Vehicle*
- Clone from above

*Track*
- Clone from above

*Study*
- Clone from above

*Runs*
- Run matrix (or reference to the run as its own file)
- Track
- Unique run id (Underscore (or other delimiter) Separated Value of sweep #, sweep x, sweep y)
- Total Time
- Energy Consumption
- (Any other parameters worth tossing in here?)

# UX Spec
*Homepage* displays an overview of what's going on
- Vehicles are tabulated, with the last edit date, and option to edit. Versions are their own rows in the table.
- Tracks are tabulated, with the last edit date, track type, length (or parsing errors), and option to upload a new track
- Studies are tabulated, with the last edit (or submission) date, status, option to view error/progress log, link to view the results, option to derive a study, and option to edit

*Vehicle Edit* brings up a plaintext editor with the only option being 'save new version'

*Track Edit* is an option to upload new track data

*Study Edit* brings up a plaintext editor with the options to 'save' and 'save + run'

*Study Log View* brings up a plaintext viewer with no options

# Enterprising
Can this be monetized? It certainly would be interesting to run
- SAAS like (the millenial way)
- Distributed & owned software (the chad way)

# Dependencies

*Python 3*
- web.py
- ruamel.yaml
- sqlite3 (builtin to python3)