# StrainFish

`strainfish` is a weighted ensemble machine learning algorithm with multiple DNA sequence encoders and logic, specifically designed for classification of marker sequences.

## Conceived and built by Kranti Konganti, HFP

### v0.2.0

- Multiple DNA sequence encoders for **GPU-accelerated** training.
- A weighted Ensemble machine-learning model generation with sensible defaults.
- **GPU-accelerated Learning and Prediction only!**
- **Important Note**: This software is under active development and as such some features are **experimental**. Results should be thoroughly validated and independently verified before use in critical applications or publications.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Training Models](#training-models)
   - [Basic Training Command](#basic-training-command)
   - [Advanced Configuration](#advanced-configuration)
   - [Encoding Methods](#encoding-methods)
4. [Making Predictions](#making-predictions)
   - [Basic Prediction Command](#basic-prediction-command)
   - [Model Management](#model-management)
5. [Configuration Options](#configuration-options)
   - [**XGBoost** Parameters](#xgboost-parameters)
   - [**RandomForest** Parameters](#randomforest-parameters)
   - [**SentencePiece** Parameters](#sentencepiece-parameters)
   - [Imbalance Handling Parameters](#imbalance-handling-parameters)
6. [Test Data and Examples](#test-data-and-examples)
7. [Dependencies](#dependencies)
8. [License](#license)

## Installation

**StrainFish** requires Python 3.11+ and can be installed via `pip`:

```bash
pip install strainfish
```

For development installation:

```bash
git clone https://github.com/your-repo/strainfish.git
cd strainfish
pip install -e .
```

## Quick Start

### Training a Model

To train a model on your DNA sequences:

```bash
strainfish train run \
  -f path/to/sequences.fasta \
  -l path/to/labels.csv \
  -o /path/to/models_output_dir/model_prefix
```

### Predicting using a Model

To predict bacterial strains using a trained model:

```bash
strainfish predict run \
  -f path/to/predict_sequences.fasta \
  -m /path/to/models_output_dir/model_prefix \
  -o path/to/results_directory
```

## Training Models

**StrainFish** uses an ensemble approach for both training and prediction (**XGBoost**, **RandomForest** and **NaiveBayes**), with custom DNA sequence encodings optimized for GPU acceleration.

### Basic Training Command

```bash
strainfish train run \
  -f training_sequences.fasta \                             # Input FASTA file
  -l labels.csv \                                           # Labels CSV (id,label)
  -o /path/to/models_output_dir/model_prefix                # Output directory for models
```

### Advanced Configuration

**StrainFish** configuration options during training:

```bash
strainfish train run \
  -f training_sequences.fasta \
  -l labels.csv \
  -o model_output_dir \
  --encode-method tf \              # Encoding method: sm, sp, or tf
  --kmer 7 \                        # K-mer size for hashing
  --num-hashes 100 \                # Number of hashes per sequence
  --factor 21 \                     # Sequence overlap factor
  --chunk-size 200 \                # Size of DNA chunks
  --pseknc-weight 0.1 \             # Weight for PseKNC encoding
  --xgb-n-estimators 300 \          # XGBoost parameters
  --rf-n-estimators 100 \           # RandomForest parameters
```

### Encoding Methods

**StrainFish** supports three DNA sequence encoding methods:

- **`tf` (TF-IDF)**: Traditional TF-IDF vectorization
- **`sp` (SentencePiece)**: Subword tokenization using SentencePiece models (**Experimental**)
- **`sm` (SOMH)**: MinHash based approach with PseKNC and sequencing composition weights (AT/GC ratio) (**Experimental**)

## Making Predictions

### Basic Prediction Command

```bash
strainfish predict run \
  -f prediction_sequences.fasta \                        # Input FASTA file(s)
  -m /path/to/models_output_dir/model_prefix \           # Path to trained model
  -o results_dir                                         # Output directory for predictions
```

### Model Management

List available models:

```bash
strainfish predict list-models
# Or list models stored at a particular models directory:
strainfish predict list-models -md /path/to/models_dir
```

## Configuration Options

**StrainFish** provides configuration options for training.

### **XGBoost** Parameters

View all configurable **XGBoost** parameters:

```bash
strainfish train show-xgb-params
```

Key parameters:

- `--xgb-n-estimators`: Number of boosting rounds
- `--xgb-max-depth`: Maximum tree depth
- `--xgb-learning-rate`: Learning rate for boosting
- `--xgb-subsample`: Subsample ratio of the training instance

### **RandomForest** Parameters

View all configurable **RandomForest** parameters:

```bash
strainfish train show-rf-params
```

Key parameters:

- `--rf-n-estimators`: Number of trees in the forest
- `--rf-max-depth`: Maximum depth of the tree
- `--rf-random-state`: Random seed for reproducibility
- `--rf-min-samples-leaf`: Minimum samples required at a leaf node

### **SentencePiece** Parameters

View all configurable **SentencePiece** parameters:

```bash
strainfish train show-sp-params
```

Key parameters:

- `--sp-vocab-size`: Vocabulary size for tokenization
- `--sp-max-sentence-length`: Maximum sentence length
- `--sp-char-cov`: Character coverage ratio

### Imbalance Handling Parameters

View all imbalance handling parameters:

```bash
strainfish train show-imb-params
```

Key parameters:

- `--imb-smote-k-neighbors`: Number of neighbors for SMOTE
- `--imb-enn-n-neighbors`: Number of neighbors for ENN cleaning

## Test Data and Examples

The repository includes test data in the `tests/test_input/` directory:

- `test.train.fasta`: Training sequences in FASTA format
- `test.train.csv`: Labels file with `id,label` columns
- `predict.fasta`: Sequences for prediction using trained models

You can use these to test **StrainFish** functionality:

```bash
# Train a model using test data
strainfish train run \
  -f tests/test_input/test.train.fasta \
  -l tests/test_input/test.train.csv \
  -o test_output/test_model

# Make predictions on the trained model
strainfish predict run \
  -f tests/test_input/predict.fasta \
  -m test_output/test_model \
  -o prediction_results
```

## Dependencies

**StrainFish** has the following key dependencies:

- **Core ML Libraries**: numpy, pandas, scikit-learn, xgboost, cuml (GPU-accelerated)
- **Sequence Processing**: biopython, sourmash, sentencepiece
- **CLI Interface**: rich, rich-click
- **Utilities**: joblib, psutil, humanize, pynvml
- **Testing**: pytest, pytest-cov

For a complete list of dependencies, see `pyproject.toml`.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
