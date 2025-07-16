# Known Issues

## PDF Support
- PDF import is currently unreliable ("wonky").
- Excel import works much better, mainly because Excel files in this use case generally have more information in fewer tokens.
- Other file formats have not been tested.

## Exercise Name Mapping
- The Lyfta exercise database may not contain all the different names for a particular exercise.
- As a workaround, an exercise name mapping is defined in `app/constants.py`.
- This mapping currently includes only the exercises encountered during testing.
- To improve accuracy, this mapping will need to be updated as new exercise names are found. 