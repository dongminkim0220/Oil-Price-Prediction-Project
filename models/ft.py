import numpy as np
from scipy.stats import chi2
import csv

def readData(inputfile, startdate, enddate):
    print("Reading dataset: [", startdate, ' ~ ' , enddate , "]")

    data = []
    dates = []
    f = inputfile
    csvReader = csv.reader(f, delimiter = ",")
    start = 0
    for i in csvReader:
        # check start date
        if(start == 0):
            if(i[0] != startdate):
                continue
            else:
                print("start date checked: ", i[0])
                start = 1

        # get inputs
        if(i[1] == ''):
            continue
        else:
            data.append(float(i[1]))
            dates.append(i[0])

        # check end date
        if(i[0] == enddate):
            print("end date checked: ", i[0])
            break
    f.close()
    return dates, data

def smoothnessMeasure(data, dates, mode) :
    # Smoothness Measure
    #P = 1 # normal
    P = 1 # for weekly -> monthly
    SM_list = []
    f = open('sm.txt', 'w')
    #if (mode =="daily"):
    if False:
        for tau in range(1, 10):
            for E in range(2, 13):
                temp = []
                a1, a2, _, _ = extracting(tau, E, P, data, dates, mode)
                sm = SM(a1, a2, E)
                temp.append(tau)
                temp.append(E)
                temp.append(sm)
                print(format("E: %f, tau: %f sm: %f") % (E, tau, sm))
                f.write(format("E: %f, tau: %f sm: %f") % (E, tau, sm) + '\n')
                SM_list.append(temp)
    else:
        for E in range(2, 11):
            temp=[]
            a1, a2, _, _ = extracting(1, E, P, data, dates, mode)
            sm = SM(a1, a2, E)
            temp.append(1)
            temp.append(E)
            temp.append(sm)
            print(format("E: %f, tau: 1 sm: %f")%(E, sm))
            f.write(format("E: %f, tau: 1 sm: %f") % (E, sm) + '\n')
            SM_list.append(temp)
    f.close()


def extracting(tau, E, P, obj, dates, mode):
    '''if the mode is weekly_data+ or monthly_data+, we use the daily data, extracting by 5 days or 20 days in sequence'''

    input = []
    output = []
    output_dates = []
    index = []

    if mode == "weekly_data+":
        a = tau * (E-1)*5
        for i in range(a, len(obj)-5*P):
            b=[]
            for j in range(i-a, i+5*tau, 5*tau):
                b.append(obj[j])
            input.append(b)
            output.append(obj[i+5*P])
            index.append(i+5*P)
            output_dates.append(dates[i+5*P])
    elif mode == "monthly_data+":
        a = tau * (E-1)*20
        for i in range(a, len(obj)-20*P):
            b=[]
            for j in range(i-a, i+20*tau, 20*tau):
                b.append(obj[j])
            input.append(b)
            output.append(obj[i+20*P])
            index.append(i+20*P)
            output_dates.append(dates[i+20*P])
    else:
        a = tau * (E-1)
        for i in range(a, len(obj)-P):
            b=[]
            for j in range(i-a, i+tau, tau):
                b.append(obj[j])
            input.append(b)
            output.append(obj[i+P])
            index.append(i+P)
            output_dates.append(dates[i+P])

    return np.array(input), np.array(output), np.array(index), np.array(output_dates)

def extracting_on_index(tau, E, P, obj, index, mode):
    input = []
    idx = index
    for j in range(E):
        input.insert(0, obj[idx]) # FIFO push
        if mode == "weekly_data+":
            idx -= tau*5
            P_ = 5*P
        elif mode== "monthly_data+":
            idx -= tau*20
            P_ = 20*P
        else:
            idx -= tau
            P_ = P

    return input, index+P_

def GaussianKernel(x, mu, sig):
    diff = x - mu
    dnorm = np.sum(np.square(diff))
    d =  dnorm / (2 * (sig**2))
    res = np.exp(-1 * d)

    return res

def output(x, kernelMeans, kernelSigma, kernelWeights):
    res = 0
    for i in range(len(kernelMeans)):
        val = GaussianKernel(x, kernelMeans[i], kernelSigma[i])
        res += val * kernelWeights[i]
        
    return res

def rMSE(y, yhat):
    a = 0
    for i in range(len(y)):
        a = a + np.square(y[i]-yhat[i])
        
    return np.sqrt(a/len(y))

def MAE(y, yhat):
    a = 0
    for i in range(len(y)):
        a = a + np.abs(y[i]-yhat[i])

    return a / len(y)

def R2(y, yhat):
    ymean = np.mean(y)
    a = 0
    b = 0
    for i in range(len(y)):
        a = a + np.square(y[i]-yhat[i])
        b = b + np.square(y[i]-ymean)
    
    c = 1 - (a/b)
    
    return c

def MAPE(y,yhat):
    a = 0
    for i in range(len(y)):
        a = a + (np.absolute(yhat[i]-y[i]) / y[i])
    
    return a / (len(y))

def loss(X, Y, kernelMeans, kernelSigma, kernelWeights):
    n = len(X)
    Yest = []
    for i in range(n):
        Yest.append(output(X[i], kernelMeans, kernelSigma, kernelWeights))
        
    Yest = np.array(Yest)
    err = Y - Yest
    rmse = rMSE(Y, Yest)
    rsq = R2(Y, Yest)
    mae = MAE(Y, Yest)

    return err, rmse, rsq, mae

def loss_with_prediction_array(Y, Y_hat):
    err = Y - Y_hat
    rmse = rMSE(Y, Y_hat)
    rsq = R2(Y, Y_hat)
    mae = MAE(Y, Y_hat)
    
    return err, rmse, rsq, mae
    
def EstimatedNoiseVariance(X):
    n = len(X)
    alpha = 0.05
    estSig = 0

    for i in range(n-1):
        if X[i] < 0 or X[i+1] < 0:
            n-=1
            continue
        dx = X[i] - X[i+1]
        estSig += dx ** 2

    estSig /= 2
    chisqCoeff_max = chi2.isf(1 - alpha/2, n-1)
    chisqCoeff_min = chi2.isf(alpha/2,n-1)

    res_max = estSig / chisqCoeff_max
    res_min = estSig / chisqCoeff_min

    return res_max, res_min

def Phase1(x, y, e, m, alpha, kernelMeans, kernelSigma, kernelWeights, invPSI):
    m += 1
    mdist = []

    for i in range(m - 1):
        val = np.sum(np.square(kernelMeans[i] - x))
        mdist.append(np.sqrt(val))
    
    idx = np.argmin(np.array(mdist))
    sig = mdist[idx] * alpha
    
    
    kernelMeans = np.concatenate((kernelMeans, np.array([x])), axis=0)
    kernelSigma = np.concatenate((kernelSigma, np.array([sig])), axis=0)

    u = np.ndarray(shape=(m - 1, 1))
    v = np.ndarray(shape=(m - 1, 1))

    for i in range(m - 1):
        u[i] = GaussianKernel(kernelMeans[i], x, sig)
        v[i] = GaussianKernel(x, kernelMeans[i], kernelSigma[i])
        
    vtP = np.matmul(v.transpose(), invPSI)
    Pu = np.matmul(invPSI, u)
    denom = 1 - np.matmul(vtP, u)
    
    A = invPSI + (np.matmul(Pu, vtP) / denom)
    b = -1 * Pu / denom
    c = 1 / denom
    d = -1 * vtP / denom

    invPSI = A

    invPSI = np.concatenate((invPSI, b), axis=1)
    d = np.concatenate((d, c), axis=1)
    invPSI = np.concatenate((invPSI, d), axis=0)

    kernelWeights += np.transpose(e * b)[0]
    kernelWeights = np.concatenate((kernelWeights, (c*e)[0]),axis=0)
    
    return m, kernelMeans, kernelSigma, kernelWeights, invPSI


def geta(h, B):
    htB = np.matmul(h.transpose(), B)
    Bh = np.matmul(B, h)
    hBh = np.matmul(htB, h)
    denom = 1 + hBh
    
    B -= np.matmul(Bh, htB) / denom
    
    return np.matmul(B, h), B
    
def Phase2(x, y, e, m, B, kernelMeans, kernelSigma, kernelWeights) :
    h = np.zeros(shape=(m, 1))
    
    for i in range(m):
        dist = np.sum(np.square(x-kernelMeans[i]))
        ko = GaussianKernel(x, kernelMeans[i], kernelSigma[i])
        h[i] = kernelWeights[i] * ko * dist / (kernelSigma[i]**3)
        
    a, B = geta(h, B)
    
    kernelSigma += np.transpose(e*a)[0]
    kernelSigma = np.abs(kernelSigma)
    
    return B, kernelSigma
    
def Phase3(x, y, e, m, B, kernelMeans, kernelSigma, kernelWeights):
    h = np.zeros(shape = (m, 1))
    
    for i in range(m):
        ko = GaussianKernel(x, kernelMeans[i], kernelSigma[i])
        h[i] = ko
        
    a, B = geta(h, B)
    kernelWeights += np.transpose(e*a)[0]
    
    return B, kernelWeights

# Smootheness Measure
def Dist(x1, x2, E):
    dist = 0
    for i in range(0, E):
        dist += np.square(x1[i] - x2[i])
    
    return np.sqrt(dist)

def SM(input_data, output_data, E):
    sm = 0
    for i in range(len(input_data)):
        temp = []
        for j in range(len(input_data)):
            temp.append(Dist(input_data[i], input_data[j],E))

        temp = np.array(temp)
        
        nonzerotemp = temp[np.nonzero(temp)]
        nonzerotemp.sort()
        
        for j in range(len(temp)):
            if nonzerotemp[0] == temp[j]:
                idx = j
                
               
        minDist = temp[idx]
        
        sm += np.abs(output_data[i]-output_data[idx]) / minDist
#        print(format("%f th step minDist: %f, minIndex: %f, sm: %f") % (i, minDist, idx, sm))

    try:
        sm = 1 - sm / len(input_data)
    except ZeroDivisionError:
        print("!", end ='')

    return sm    

#Kernel Alignment
    
def MaxGaussian(x, Means_array, Sigmas_array):
    G_value = []
    for i in range(len(Means_array)):
        G_value.append(GaussianKernel(x, Means_array[i], Sigmas_array[i]))
    G_value = np.array(G_value)
    return np.max(G_value)
#    return G_value
    
def KernelAlignment(x, MeanMatrix, SigmaMatrix):
    temp = []
    for i in range(len(MeanMatrix)):
        temp.append(MaxGaussian(x, MeanMatrix[i], SigmaMatrix[i]))
        
    temp = np.array(temp)
    
    return np.argmax(temp)

def MaxKernelPredict(teX, MeanMatrix, SigmaMatrix, WeightMatrix):
    temp = []
    for i in range(len(teX)):
        idx = KernelAlignment(teX[i], MeanMatrix, SigmaMatrix)
        temp.append(output(teX[i], MeanMatrix[idx], SigmaMatrix[idx], WeightMatrix[idx]))
    
    temp = np.array(temp)
    
    return temp

def minDist(x, Means_array):
    dist = []
    for i in range(len(Means_array)):
        dist.append(Dist(x, Means_array[i], len(x)))
    dist = np.array(dist)
    return np.min(dist)
        
def KernelAlignment_Dist(x, MeanMatrix):
    temp = []
    for i in range(len(MeanMatrix)):
        temp.append(minDist(x, MeanMatrix[i]))
    temp = np.array(temp)
    
    return np.argmin(temp)
#    return temp

def minDistPredict(teX, MeanMatrix, SigmaMatrix, WeightMatrix):
    temp = []
    for i in range(len(teX)):
        idx = KernelAlignment_Dist(teX[i], MeanMatrix)
        temp.append(output(teX[i], MeanMatrix[idx], SigmaMatrix[idx], WeightMatrix[idx]))
    
    temp = np.array(temp)
    
    return temp