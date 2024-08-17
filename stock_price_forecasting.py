# -*- coding: utf-8 -*-
"""Stock Price Forecasting

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1248pJXGh1QltyuQ3YDAYSPAghlAOj6ye
"""

# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.metrics import mean_squared_error, r2_score
import math
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# Fetch the data from Yahoo Finance
stock_data = yf.download('GRASIM.NS', start='2010-01-01', end='2023-01-01')

# Ensure the date index has a frequency
stock_data = stock_data.asfreq('B')  # 'B' stands for business day frequency

# Prepare the data
stock_data['Code'] = 'GRASIM'
stock_data = stock_data.reset_index()
stock_data['Date'] = stock_data['Date'].dt.strftime('%Y-%m-%d')

# LSTM Model
# Select the 'Close' column for LSTM model
data = stock_data[['Date', 'Close']]
data = data.set_index('Date')

# Ensure there are no NaN values in the data
data = data.fillna(method='ffill')

# Scale the data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# Split the data into training and testing sets
train_size = int(len(scaled_data) * 0.80)
train_data, test_data = scaled_data[:train_size], scaled_data[train_size:]

# Create the dataset for LSTM
def create_dataset(dataset, time_step=1):
    X, Y = [], []
    for i in range(len(dataset) - time_step - 1):
        a = dataset[i:(i + time_step), 0]
        X.append(a)
        Y.append(dataset[i + time_step, 0])
    return np.array(X), np.array(Y)

time_step = 100
X_train, y_train = create_dataset(train_data, time_step)
X_test, y_test = create_dataset(test_data, time_step)

# Reshape input to be [samples, time steps, features] which is required for LSTM
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# Create the LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train, y_train, batch_size=64, epochs=100)

# Predict the stock prices
train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

# Transform back to original form
train_predict = scaler.inverse_transform(train_predict)
test_predict = scaler.inverse_transform(test_predict)

# Adjust the lengths of the predictions to match the original data
train_predict_plot = np.empty_like(scaled_data)
train_predict_plot[:, :] = np.nan
train_predict_plot[time_step:len(train_predict) + time_step, :] = train_predict

test_predict_plot = np.empty_like(scaled_data)
test_predict_plot[:, :] = np.nan
test_predict_plot[len(train_predict) + (time_step * 2) + 1:len(scaled_data) - 1, :] = test_predict

# Calculate RMSE and R²
train_rmse = math.sqrt(mean_squared_error(scaler.inverse_transform(y_train.reshape(-1, 1)), train_predict))
test_rmse = math.sqrt(mean_squared_error(scaler.inverse_transform(y_test.reshape(-1, 1)), test_predict))
train_r2 = r2_score(scaler.inverse_transform(y_train.reshape(-1, 1)), train_predict)
test_r2 = r2_score(scaler.inverse_transform(y_test.reshape(-1, 1)), test_predict)

print("Train RMSE:", train_rmse)
print("Test RMSE:", test_rmse)
print("Train R²:", train_r2)
print("Test R²:", test_r2)

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(data.index, scaler.inverse_transform(scaled_data), label='Actual Price')
plt.plot(data.index, train_predict_plot, label='Train Predict')
plt.plot(data.index, test_predict_plot, label='Test Predict')
plt.legend()
plt.title('LSTM Model Predictions')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

def ARIMA_ALGO(df):
    uniqueVals = df["Code"].unique()
    df = df.set_index("Code")

    def parser(x):
        return datetime.strptime(x, '%Y-%m-%d')

    def arima_model(train, test):
        history = [x for x in train]
        predictions = list()
        for t in range(len(test)):
            model = ARIMA(history, order=(6, 1, 0))
            model_fit = model.fit()
            output = model_fit.forecast()
            yhat = output[0]
            predictions.append(yhat)
            obs = test[t]
            history.append(obs)
        return predictions

    for company in uniqueVals[:1]:  # Only process GRASIM
        data = (df.loc[company, :]).reset_index()
        data['Price'] = data['Close']
        Quantity_date = data[['Price', 'Date']]
        Quantity_date.index = Quantity_date['Date'].map(lambda x: parser(x))
        Quantity_date['Price'] = Quantity_date['Price'].map(lambda x: float(x))
        Quantity_date = Quantity_date.fillna(Quantity_date.bfill())
        Quantity_date = Quantity_date.drop(['Date'], axis=1)

        plt.figure(figsize=(10, 6))
        plt.plot(Quantity_date)
        plt.title('GRASIM Stock Price Over Time')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.show()

        quantity = Quantity_date.values
        size = int(len(quantity) * 0.80)
        train, test = quantity[0:size], quantity[size:len(quantity)]

        # Fit the model
        predictions = arima_model(train, test)

        # Plot the graph
        plt.figure(figsize=(10, 6))
        plt.plot(test, label='Actual Price')
        plt.plot(predictions, label='Predicted Price')
        plt.legend(loc=4)
        plt.title('ARIMA Model Predictions')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.show()

        print("##############################################################################")
        arima_pred = predictions[-2]
        print("Tomorrow's GRASIM Closing Price Prediction by ARIMA:", arima_pred)

        # RMSE calculation
        error_arima = math.sqrt(mean_squared_error(test, predictions))
        arima_r2 = r2_score(test, predictions)
        print("ARIMA RMSE:", error_arima)
        print("ARIMA R²:", arima_r2)
        print("##############################################################################")

        return arima_pred, error_arima, arima_r2

# Run the ARIMA algorithm
arima_pred, error_arima, arima_r2 = ARIMA_ALGO(stock_data)