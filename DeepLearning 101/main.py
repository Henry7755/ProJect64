from nueral_network import NaiveSequential, NaiveDense
import batch_gen
import tensorflow as tf



#assert len(model.weights) == 4

from tensorflow.keras.datasets import mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images = train_images.reshape((60000, 28 * 28))
train_images = train_images.astype("float32") / 255  
test_images = test_images.reshape((10000, 28 * 28))
test_images = test_images.astype("float32") / 255 

model = NaiveSequential([
    NaiveDense(input_size = 28*28, output_size = 512, activation = tf.nn.relu),
    NaiveDense(input_size = 512, output_size = 10, activation = tf.nn.softmax)
]
)
model_1 = model
model.fit(model_1,train_images, train_labels, epochs=10, batch_size=128) 


predictions = model(test_images)
predictions = predictions.numpy()      
predicted_labels = np.argmax(predictions, axis=1)
matches = predicted_labels == test_labels
print(f"accuracy: {matches.mean():.2f}")