def proccess(hist_band_power):
    data = hist_band_power["delta_theta_"]
    data = data[-1]
    data = sum(data.values())/2000
    print(data, end=' ')
    result=0
    if data>0.7:
        result = 1
    #if data>0.9:
    #    result=-1
    #if data>2.5:
    #    result=1
    print(result)
    return result
