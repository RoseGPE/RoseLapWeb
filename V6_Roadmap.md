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
*Vehicles* are sets of base parameters (complex objects in YAML format)
*Tracks* are sets of distance-curvature data (in some format)
*Studies* are based on vehicles and tracks (complex objects in YAML format)
- Study database entries have three states: drafting, submitted, running, and finished
- Once a study is submitted, the link to the track and vehicle is broken; the track and vehicle data is imported/stored into the database entry
- Studies can be 'rebased'; the previous study serves as a draft upon which further improvements can be written. In this rebasing, the previous tracks and vehicles can be imported, or left behind in favor of the new dynamically linked ones
*Runs* are individual maneuvers around a track 
- Run database entries contain a MD5 hash of the vehicle (as configured) and track
- Collisions are a feature to reduce computational load, not a bug?
*Users* are individual members which have access to particular runs
*Groups* are teams which users can belong to (maybe)

# Enterprising
Can this be monetized? It certainly owuld be interesting to run
- SAAS like (the millenial way)
- Distributed & owned software (the chad way)
