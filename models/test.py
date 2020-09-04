import GKFN
import ft

#mode = "daily"
#mode = "weekly_origin"
#mode = "weekly_tau1"
#mode = "weekly_tau1_for_monthly"
#mode = "monthly"
#mode = "weekly_data+"
#mode = "monthly_data+"

dailyfile = open('./daily/wti.csv', 'r')
weeklyfile = open('./weekly/wti_week.csv', 'r')
monthlyfile = open('./monthly/wti_month.csv', 'r')

if(mode == "daily"): # Daily
    print("===DAILY DATASET===")
    data = ft.readData(dailyfile, '2000-01-03', '2020-03-13')
    E = 5
    tau = 3
elif(mode == "weekly_origin"): # Weekly_original
    print("===WEEKLY DATASET===")
    data = ft.readData(weeklyfile, '1986-01-03', '2020-06-26')
    E = 4
    tau = 18
elif(mode == "weekly_tau1"): # Weekly_tau1
    print("===WEEKLY DATASET===")
    data = ft.readData(weeklyfile, '1986-01-03', '2020-06-26')
    E = 6
    tau = 1
elif(mode == "weekly_tau1_for_monthly"): # Weekly_tau1
    print("===WEEKLY DATASET===")
    data = ft.readData(weeklyfile, '1986-01-03', '2020-06-26')
    E = 10
    tau = 1
elif(mode == "monthly"): # Monthly
    print("===MONTHLY DATASET===")
    data = ft.readData(monthlyfile, '1960-01-01', '2020-06-01')
    E = 4
    tau = 2
elif(mode == "weekly_data+"): # weekly_data+
    print("===WEEKLY DATASET===")
    data = ft.readData(dailyfile, '2000-01-03', '2020-03-13')
    E = 6
    tau = 1
elif(mode == "monthly_data+"): # weekly_data+
    print("===MONTHLY DATASET===")
    data = ft.readData(dailyfile, '2000-01-03', '2020-03-13')
    E = 10
    tau = 1

P = 1 # P days/weeks/months after
dataX, dataY = ft.extracting(tau, E, P, data,mode)
test_ratio = 0.3
test_size = int(len(data) * test_ratio)
print("size of dataset:", len(data))
print("size of test dataset:", test_size)

# Train
trX = dataX[:-test_size]
trY = dataY[:-test_size]

# Test
teX = dataX[-test_size:]
teY = dataY[-test_size:]

print(teX)
print(teY)

# parameter
alpha = 0.5
loop = 5
Kernel_Num = 100

GKFN.GKFN(trX, trY, teX, teY, alpha, loop, Kernel_Num)
