def proccess(hist_band_power):
    data = hist_band_power["delta_theta_"]
    data = data[-1]
    data = sum(data.values())/2000
    lambda_sum = sum(hist_band_power["lambda_"])/10
    print(lambda_sum, data)
    answer=0
    if data<2.2 and lambda_sum>19.8:
        answer=-1
    if data<0.8:
        data=0
    if 0.8<=data<=2.7:
        data=-1
        if answer!=-1:
            answer=1
    if 2.7<data<20:
        data=1
        if answer!=-1:
            answer=1
    if data>=20:
        data=0
    return answer
