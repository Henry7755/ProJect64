from sklearn.pipeline import Pipeline

# Create a pipeline with the ECGNoiseHandler class
pipeline = Pipeline([
    ('noise_handler', ECGfilter(lowcut=0.5, highcut=50.0, notch_freq=50.0, fs=1000)),
    # Add other transformations or models here as needed
])

# Tackle the ECG signal data but will call it in a different file
X_filtered = pipeline.fit_transform(X_ecg)