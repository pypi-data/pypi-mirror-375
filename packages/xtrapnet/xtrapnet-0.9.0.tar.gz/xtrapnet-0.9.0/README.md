# XtrapNet - Extrapolation-Aware Neural Networks  
[![PyPI Version](https://img.shields.io/pypi/v/xtrapnet)](https://pypi.org/project/xtrapnet/)  
[![Python Version](https://img.shields.io/pypi/pyversions/xtrapnet)](https://pypi.org/project/xtrapnet/)  
[![License](https://img.shields.io/pypi/l/xtrapnet)](https://opensource.org/licenses/MIT)  

XtrapNet v0.2.0 is a deep learning framework that actually handles out-of-distribution (OOD) extrapolation properly. Most neural networks break when they see data they haven't trained on, but XtrapNet gives you control over what happens in those situations.

**What makes it different:**
- **Modular Pipeline Architecture** - Everything you need in one configurable pipeline
- **Advanced OOD Detection** - Multiple ways to detect when your model is seeing something new (Mahalanobis, KNN, etc.)
- **Conformal Prediction** - Real uncertainty quantification with statistical guarantees
- **Ensemble Wrappers** - Built-in ensemble methods that actually work
- **Extrapolation Control** - Choose how your model behaves when it's uncertain
- **PyTorch Integration** - Works with any PyTorch model without breaking your existing code  

## Installation
Just pip install it:
```bash
pip install xtrapnet
```

## Quick Start

### Basic Usage
Here's how you'd use it for a simple regression problem:

```python
import numpy as np 
from xtrapnet import XtrapNet, XtrapTrainer, XtrapController

# Generate some training data
features = np.random.uniform(-3.14, 3.14, (100, 2)).astype(np.float32)
labels = np.sin(features[:, 0]) * np.cos(features[:, 1]).reshape(-1, 1)

# Train the model
net = XtrapNet(input_dim=2)
trainer = XtrapTrainer(net)
trainer.train(labels, features)

# Set up the controller to handle OOD inputs
controller = XtrapController(
    trained_model=net,
    train_features=features,
    train_labels=labels,
    mode='warn'  # This will warn you when it sees something weird
)

# Test it on an out-of-distribution point
test_input = np.array([[5.0, -3.5]])  # Way outside training range
prediction = controller.predict(test_input)
print("Prediction:", prediction)
```

### The New Pipeline (v0.2.0)
If you want the full experience with uncertainty quantification and OOD detection:

```python
from xtrapnet import XtrapPipeline, PipelineConfig, default_config

# Set up the complete pipeline
config = default_config()
config.model.input_dim = 2
config.ood.detector_type = 'mahalanobis'  # Good default for most cases
config.uncertainty.enable_conformal = True

# Train everything at once
pipeline = XtrapPipeline(config)
pipeline.fit(features, labels)

# Get predictions with uncertainty bounds
predictions, uncertainty = pipeline.predict(test_input, return_uncertainty=True)
print(f"Prediction: {predictions}")
print(f"Uncertainty: {uncertainty}")
```

## What Happens When Your Model Sees Something Weird?

You get to choose how XtrapNet behaves when it encounters data outside its training distribution:

| Mode             | What it does |
|-----------------|-------------|
| clip            | Clamps predictions to the range it's seen before |
| zero            | Returns zero for unknown inputs |
| nearest_data    | Uses the closest training example it knows |
| symmetry        | Makes educated guesses based on symmetry |
| warn           | Prints a warning but makes a prediction anyway |
| error           | Throws an error and stops |
| highest_confidence | Picks the prediction with lowest uncertainty |
| backup          | Falls back to a simpler model |
| deep_ensemble   | Averages predictions from multiple models |
| llm_assist      | Asks an LLM for help (experimental) |


## Visualizing What's Happening

You can easily plot how your model behaves across different regions:

```python
import matplotlib.pyplot as plt 

# Test across a wide range
x_test = np.linspace(-5, 5, 100).reshape(-1, 1) 
mean_pred, var_pred = controller.predict(x_test, return_variance=True)

# Plot the predictions with uncertainty bands
plt.plot(x_test, mean_pred, label='Model Prediction', color='blue') 
plt.fill_between(x_test.flatten(), 
                mean_pred - var_pred, 
                mean_pred + var_pred, 
                color='blue', alpha=0.2, 
                label='Uncertainty') 
plt.legend() 
plt.show()
```

This shows you exactly where your model is confident (narrow bands) vs uncertain (wide bands).

## What's New in v0.2.0

### Major Features Added
- **XtrapPipeline**: Everything you need in one pipeline - no more juggling different components
- **EnsembleWrapper**: Built-in ensemble methods that actually give you meaningful uncertainty estimates
- **OOD Detectors**: Multiple ways to detect when your model is seeing something new (Mahalanobis, KNN, etc.)
- **Conformal Prediction**: Real uncertainty quantification with statistical guarantees (not just hand-waving)
- **Modular Architecture**: Mix and match components however you want

### API Improvements
- Cleaner imports: `from xtrapnet import XtrapPipeline, PipelineConfig`
- Configuration-based setup with `default_config()` - no more guessing what parameters to use
- Better error messages when things go wrong
- Proper type hints so your IDE actually helps you

## What's Coming Next

We're working on some cool stuff:
- **v0.2.0** (current): Modular pipeline, ensemble wrappers, OOD detectors, conformal prediction
- **v0.3.0**: Bayesian Neural Network support - proper Bayesian uncertainty
- **v0.4.0**: Physics-Informed Neural Networks - when you know the physics but not the data
- **v0.5.0**: LLM integration - let language models help with OOD decisions
- **v0.6.0**: Adaptive learning - models that get better at handling OOD data over time
- **v0.7.0**: Real-world anomaly detection - because real data is messy

## Contributing
Found a bug or want to add a feature? Pull requests are welcome.  
**GitHub:** [https://github.com/cykurd/xtrapnet](https://github.com/cykurd/xtrapnet)  

## License
MIT License - use it however you want.

## Support
Questions? Open an issue on GitHub or email **cykurd@gmail.com**.

## Why Use XtrapNet?
Most neural networks break when they see data they haven't trained on. XtrapNet gives you control over what happens in those situations instead of just hoping for the best.  
