def proccess(hist_band_power):
    lambda_s = sum([sum(elem.values()) for elem in hist_band_power["lambda"]]) / len(hist_band_power["lambda"])
    kappa_s = sum([sum(elem.values()) for elem in hist_band_power["kappa"]]) / len(hist_band_power["kappa"])
    print(kappa_s, lambda_s)
    answer = 0
    return answer