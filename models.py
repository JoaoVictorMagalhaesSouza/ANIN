
from xgboost import XGBRegressor
#Import tensorflow sequential
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import EarlyStopping

class ModelXGboost():
    def __init__(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train
        
        
    def fit(self):
        self.model = XGBRegressor(n_estimators=1500, learning_rate=0.05, max_depth=12, random_state=42,
        eval_metric='mae', subsample=0.8)
        self.model.fit(self.X_train, self.y_train)
        
    def predict(self, X_test_xgb):
        self.y_pred = self.model.predict(X_test_xgb)
        return self.y_pred
    
    def get_booster(self):
        return self.model.get_booster()

class ModelLSTM():
    def __init__(self, X_train, x_test, y_train, y_test):
        self.X_train = X_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.model = Sequential()
        self.model.add(LSTM(32,return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))    
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(256,return_sequences=True))
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(512,return_sequences=True))
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(1024))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(1))
        #self.model.compile(optimizer='Adam', loss='mse', metrics=['accuracy','mae'])
        #EarlyStopping
        self.es = EarlyStopping(monitor='mae', mode='min', verbose=1, patience=20)
    def compile(self, optimizer='Adam', loss='mse'):
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy','mae'])
    
    def fit(self, epochs=500, batch_size=64):
        print("X_train shape: ", self.X_train.shape)
        self.model.fit(self.X_train, self.y_train, epochs=epochs, batch_size=batch_size, callbacks=[self.es])
    
    def predict(self):
        self.y_pred = self.model.predict(self.x_test)
        return self.y_pred
    
    def evaluate(self):
        return self.model.evaluate(self.X_train, self.y_train)
    
    def get_weights(self):
        return self.model.get_weights()

    def save_model(self):
        self.model.save('model.h5')
        self.model.save_weights('weights.h5')
    
    #Load model and weights
    def carrega_modelo(self):
        self.model = load_model('model.h5')
        self.model.load_weights('weights.h5')
    
   