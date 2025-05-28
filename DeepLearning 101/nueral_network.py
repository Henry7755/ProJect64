import tensorflow as tf
from tensorflow.keras import optimizers
from batch_gen import BatchGenerator


class NaiveSequential(BatchGenerator):
    def __init__(self,layers):
        self.layers = layers
        
    def __call__(self,x):
        x = inputs
        for layer in self.layers:
            x = layer(x)
        return x
    
    @property
    def weights(self):
        weights = []
        for layer in self.layers:
            weights += layer.weights
        return weights
    
    def update_weight( gradient, weights):
        optimizer.apply_gradients(zip(gradients, weights))
        
    def one_training_step(model, images_batch, labels_batch):
        with tf.GradientTape() as tape:            
            predictions = model(images_batch)             
            per_sample_losses = tf.keras.losses.sparse_categorical_crossentropy(labels_batch,predictions)              

            average_loss = tf.reduce_mean(per_sample_losses)            
        gradients = tape.gradient(average_loss, model.weights)  
        update_weights(gradients, model.weights)  
        return average_loss
        
    def fit (model, images, labels, epochs, batch_size = 128):
        for epoch_counter in range(epochs):
            print(f"Epoch {epoch_counter}")
    
        
        batch_generator = BatchGenerator (images, labels)
        for batch_counter in range (batch_generator.num_batches):
            images_batch, label_batch = batch_generator.next()
            loss = one_training_step(model,images_batch, labels_batch)
            if batch_counter %100 == 0:
                print(f"loss at batch {batch_counter}: {loss: .2f}")

class NaiveDense(NaiveSequential):
    def __init__ (self, input_size, output_size, activation):
        self.activation = activation
        
        w_shape = (input_size, output_size)
        w_initial_value = tf.random.uniform(shape=w_shape, minval= 0 , maxval=1e-1)
        self.W = tf.Variable(w_initial_value)
        
        b_shape = (output_size,)
        b_initial_value = tf.zeros(b_shape)
        self.b = tf.Variable(b_initial_value)
        
        def __call__(self, x):
            return self.activation(tf.matmul(x,self.W) + self.b)
        
        @property
        def weights(self):
            return [self.W, self.b]
        
        

    
