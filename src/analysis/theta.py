def proccess(hist_band_power):
    data = hist_band_power["delta_theta_"]
    data = data[-1]
    data = sum(data.values()) / 100
    data *= 2.5
    if data > 2:
        data = (data - 3) / 4 + 3
    print(data)
    return result
