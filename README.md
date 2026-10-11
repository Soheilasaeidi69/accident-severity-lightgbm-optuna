# Data

The data are not included in this repository.

The paper uses **US-Accidents** (Moosavi et al., 2019), a countrywide data set of traffic accidents in 49 US states.

- Download: <https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents> (free Kaggle account needed)
- Project page: <https://smoosavi.org/datasets/us_accidents>
- Licence: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)

The paper used the **December 2020 release** (`US_Accidents_Dec20.csv`, about 4.2 million records, February 2016 to December 2020). Kaggle now offers the **March 2023 release** (`US_Accidents_March23.csv`, about 7.7 million records, 2016 to 2023) and a 500,000-record sample of it (`US_Accidents_March23_sampled_500k.csv`). The code accepts any of them; `src/preprocess.py` keeps the records from February 2016 to December 2020.

Put the CSV file in this folder and run, for example:

```
python src/preprocess.py --input data/US_Accidents_March23_sampled_500k.csv --output data/model_table.csv.gz
```

If you use the data, please cite:

- Moosavi, S., Samavatian, M. H., Parthasarathy, S., and Ramnath, R. (2019). A countrywide traffic accident dataset. arXiv:1906.05409.
- Moosavi, S., Samavatian, M. H., Parthasarathy, S., Teodorescu, R., and Ramnath, R. (2019). Accident risk prediction based on heterogeneous sparse data: new dataset and insights. In *Proceedings of the 27th ACM SIGSPATIAL International Conference on Advances in Geographic Information Systems*.
