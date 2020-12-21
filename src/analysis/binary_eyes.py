def proccess(hist_band_power):
    data = hist_band_power["delta_theta_"]
    data = data[-1]
    data = sum(data.values())/5
    print(data, end=' ')
    return data
