# SCGraph Benchmarking

This repo is not intended to be used by end users and is purely for internal and development purposes related to the SCGraph package and associated packages.
- It is not designed to be used as a library
- It is designed to be used as a collection of scripts to benchmark the performance of the SCGraph library against other libraries like NetworkX and OSMNX. 

This directory contains scripts and configurations for benchmarking the SCGraph library. 
- The benchmarks are designed to evaluate the performance of various graph algorithms implemented in SCGraph. 
- It also includes benchmarking against other libraries like NetworkX and OSMNX.

## Environment Setup
Setup a virtual environment and install the required dependencies:

```bash
python3.13 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Running Benchmarks

### Notes for Google Routes API
If you want to evaluate the performance of Google Routes API, you will have to enable the Routes API in the google dashboard and set the API key in `utils/keys.json` file. The file should look like this:

```json
{
    "google_api_key": "YOUR_API_KEY"
}
```

You should also modify the `geo_time_comparisons_test.py` script to actually fetch the data from Google Routes API live rather than reloading the data from the same test when previously run.

### Benchmark Scripts

To run the benchmarks, execute the desired benchmark script. For example, to run the distance matrix benchmark:

```bash
python geo_time_comparisons_test.py
```

### Output
The output of the benchmarks will be saved in the `outputs` directory. Each benchmark script will generate a file containing the results of the benchmark, including execution times and any relevant metrics.
