# Roselap V6
Welcome to RoseLap, a moderately powerful laptime simulation tool used by Rose-Hulman Institue of Technology's FSAE team, Rose Grand Prix Engineering (GPE). We use this software to turn vehicle parameters into theoretical lap times, as well as perform studies to examine the effects of variations in parameters on track performance. From that data we can then make better-informed design decisions.

RoseLap is accessed via a web interface, which includes various plotting and analysis tools.

## Getting Acquainted as a User

- Check out the model documentation in [model_docs.pdf](./sim/docs/model_docs.pdf)
- If you are dealing with tires, familiarize yourself with [the tire utility](./tire_utility)

While the web interface is in progress...

- Check out [the example vehicle definition](./example/VEHICLE_START_HERE.yaml)
- Check out [the currently available tracks](./example/tracks)
- Read through [an introductory study definition file](./example/STUDY_START_HERE.yaml)

## Getting Acquainted as a Model Developer

- [Check out the model documentation in model_docs.pdf](./sim/docs/model_docs.pdf)
- [Check out the vehicle example in params/vehicles/START_HERE.yaml](./py/RoseLapCore/params/vehicles/START_HERE.yaml)
- [Check out the track segmenter / generator](./py/RoseLapCore/input_processing/track_segementation.py)
- [Check out the sims in sims](./sims) althought some of the logic is also in [vehicle.py](./py/RoseLapCore/input_processing/vehicle.py)
- [Visit the playground for some example usage](./sim/example)
- [Note the antiquiated-ish plotting library useful for model development without the web](./py/RoseLapCore/plottools.py)

## Getting Acquainted as a UX Developer
- [This is the current state of affairs](http://rosegpe.ddns.net/RoseLap/)
- We are using bootstrap 4 + jquery
- Not sure about plotting... either Thad's splot, or d3... we'll see