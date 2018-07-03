# Roselap v4 Core
Welcome to RoseLap, a moderately powerful laptime simulation tool used by Rose-Hulman Institue of Technology's FSAE team, Rose Grand Prix Engineering (GPE). We use this software to turn vehicle parameters into theoretical lap times, as well as perform studies to examine the effects of variations in parameters on track performance. From that data we can then make better-informed design decisions.

RoseLap will soon be acessible via a web interface, which includes various plotting and analysis tools.

## Getting Acquainted as a User

- Check out the model documentation in [model_docs.pdf](model_docs.pdf)
- If you are dealing with tires, familiarize yourself with [the tire utility](./tire_utility)

While the web interface is in progress...

- Check out [the example vehicle definition]](./params/vehicles/VEHICLE_START_HERE.yaml)
- Check out [the currently available tracks](./params/tracks)
- Read through [an introductory study definition file](./params/STUDY_START_HERE.yaml)


## Getting Acquainted as a Model Developer

- [Check out the model documentation in model_docs.pdf](model_docs.pdf)
- [Check out the vehicle example in params/vehicles/START_HERE.yaml](./params/vehicles/START_HERE.yaml)
- [Check out the track segmenter / generator](./input_processing/track_segementation.py)
- [Check out the sims in sims](./sims) althought some of the logic is also in [vehicle.py](./input_processing/vehicle.py)
- [Visit the playground for some example usage](./playground.py)
- [Note the antiquiated-ish plotting library useful for model development without the web](./plottools.py)
