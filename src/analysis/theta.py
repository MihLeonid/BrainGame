def proccess(hist_band_power):
    data = hist_band_power["delta_theta_"]
    data = (sum([sum(elem.values()) for elem in data]) / 100) / len(data)
    data *= 3
    if data > 2:
        data = (data - 3) / 4 + 3
    #data -= 2.2
    data *= 1.5
    print(data)
   # if data < 2.5:
   # 	data = 2.5
   # elif data > 3.5:
   # 	data = 3.5
    return data
