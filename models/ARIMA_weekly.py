import ft
from statsmodels.tsa.arima_model import ARIMA, ARIMAResults
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
import pandas as pd
import ft


# ignore warnings
warnings.filterwarnings("ignore")

#  mode = "daily"
#mode = "weekly"
#mode = "monthly_data+"

dailyfile = open('./daily/wti.csv', 'r')
weeklyfile = open('./weekly/wti_week.csv', 'r')
#monthlyfile = open('./monthly/wti_month.csv', 'r')

if(mode == "daily"): # Daily
    print("===DAILY DATASET===")
    data = ft.readData(dailyfile, '2000-01-03', '2020-08-30')
elif(mode == "weekly"): # Weekly_original
    print("===WEEKLY DATASET===")
    data = ft.readData(weeklyfile, '1986-01-03', '2020-08-28')
elif(mode == "monthly"): # Monthly
    print("===MONTHLY DATASET===")
    #data = ft.readData(monthlyfile, '1960-01-01', '2020-06-01')

# hyperparmeters
test_ratio = 0.2
ARIMA_order = (3, 1, 3)

# train / test split
test_size = int(len(data) * test_ratio)
print("size of dataset:", len(data))
print("size of test dataset:", test_size)

#train, extra, test = data[:-test_size-4], data[-test_size-4:-4], data[-test_size:]
train, test = data[:-test_size], data[-test_size:]


# evaluate models
history = [x for x in train]

predictions = list()


print("=== TESTING ARIMA ==")
for t in range(len(test)):
    model = ARIMA(history, order = ARIMA_order)
    model_fit = model.fit(disp = 0, trend='nc')
    output = model_fit.forecast()
    yhat = output[0][0] #output[0][4]
    predictions.append(yhat)
    obs = test[t] #extra[t]
    history.append(obs)

    # Track the testing process
    print(".", end = "")
    cnt = t + 1
    if(cnt % 100 == 0):
        print("({} / {})".format(t+1, len(test)))
    elif(cnt == len(test)):
        print("({} / {})".format(t+1, len(test)))


print("=== EVALUATE ===")
params = model_fit.params
pvalues = model_fit.pvalues
rmse = ft.rMSE(test, predictions)
rsq = ft.R2(test, predictions)
mae = ft.MAE(test, predictions)

print(format('rmse: %f, R2: %f, MAE: %f') % (rmse, rsq, mae))

# Save
df = pd.DataFrame()
df["Estimate"] = pd.Series(predictions)
df["Value"] = pd.Series(test)

print(df.head())

filename = "ARIMA" + "_" + "weekly" + "_" + str(ARIMA_order)
text = "rmse" + ":" + str(rmse) +  "\n" +\
            "rsq" + ":" + str(rsq) +  "\n" +\
            "mae" + ":" + str(mae) + "\n" +\
            "parameters :" + "\n"

const = False #constant 유무
if const:
    st=1
    text = text + "constant:" + str(params[st]) + \
           " (" + str(pvalues[st]) + ")" + "\n"
else: st =0
for ar in range(1, ARIMA_order[0]+1):
    text = text + "AR_" + str(ar) + ":" + str(params[st+ar-1]) +\
           " (" + str(pvalues[st+ar-1])+ ")" + "\n"

for ma in range(1, ARIMA_order[2]+1):
    text = text + "MA_" + str(ma) + ":" + str(params[st+ARIMA_order[0]+ma-1]) +\
           " (" + str(pvalues[st + ARIMA_order[0]+ma-1])+ ")" + "\n"

df.to_csv(filename + ".csv", index=False)

plt.figure(figsize=(12,5), dpi=100)
plt.plot(test, 'r')
plt.plot(predictions, 'b')
plt.legend(["Test Data", "Prediction"])
plt.savefig(filename + ".png")
plt.clf()


test = pd.Series(test, index=range(len(data)-test_size, len(data)))
predictions = pd.Series(predictions, index=range(len(data)-test_size, len(data)))

plt.plot(train, label='training')
plt.plot(test, label='actual', color='r')
plt.plot(predictions, label='prediction', color = 'b')
plt.legend(["Test Data", "Prediction"])
plt.savefig(filename + "_all" + ".png")
plt.show()

log = open(filename + "_result" + '.txt', 'w')
log.write(text)
log.close()