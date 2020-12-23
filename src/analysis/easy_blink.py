def proccess(hist_band_power):
    lambda_s = sum([sum(elem.values()) for elem in hist_band_power["lambda"]]) / len(hist_band_power["lambda"])
    print(lambda_s, end=' ')
    if lambda_s > 100:
    	print(1)
    	return 1
    if lambda_s > 10:
    	print(-1)
    	return -1
    print(0)
    return 0