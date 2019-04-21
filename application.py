# Import libraries
import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import requests
import json
app = Flask(__name__)
# Load the model
model = pickle.load(open('model.pkl','rb'))
test=[[0 for i in range(4)]for j in range(5)]
location='mumbai'


@app.route('/')
def jsonpage():
    return render_template('forest.html')


@app.route('/m', methods=['POST'])
def my_form_post():
    location = request.form['word']
    processed_text = location.upper()
    print (processed_text)
    response = requests.get("http://api.worldweatheronline.com/premium/v1/weather.ashx?key=811c892f33bb4688802102448191903&q=mumbai&format=json&num_of_days=5&tp=24")
    json_value=response.json()
    for i in range(5):
        for j in range(1):
            humidity=json_value['data']['weather'][i]['hourly'][j]['humidity'];
            precipMM=json_value['data']['weather'][i]['hourly'][j]['precipMM'];
            pressure=json_value['data']['weather'][i]['hourly'][j]['pressure'];
            tempC=json_value['data']['weather'][i]['hourly'][j]['tempC'];
            #windspeedKmph=json.data.weather[i].hourly[j].windspeedKmph;
            test[i][j]=float(humidity);
            test[i][j+1]=float(precipMM);
            test[i][j+2]=float(pressure);
            test[i][j+3]=float(tempC);
    print(test)
    return  json.dumps(json_value)


@app.route('/predict')
def predict():
    # Make prediction using model loaded from disk as per the data.
    
    prediction = model.predict(test)
    print(prediction)
    return jsonify(prediction.tolist())


@app.route('/userpredictfunction', methods=['POST'])
def userpredict():
    # Make prediction using model loaded from disk as per the data.
    location=request.form['loc']
    humidity=request.form['humidity']
    precipMM=request.form['precipMM']
    pressure=request.form['pressure']
    Temperature=request.form['Temperature']
    print(location,humidity,precipMM,pressure,Temperature)
    prediction = model.predict([[humidity,precipMM,pressure,Temperature]])
    if (prediction>0.6):
        prediction=1
    else:
        prediction=0
    print(prediction)
    return jsonify(prediction)

@app.route('/notify',methods=['POST'])
def notify():
    
    import smtplib
    import pandas as pd
    import numpy as np
    location = request.form['word']
    gmailaddress ='flood.prediction.user@gmail.com'
    pwd = 'Floods2019'
    names=['name','email']
    users=pd.read_csv(location+"Users.csv",names=names)
    array=users.values
    mailto =array[:,1]
    message = """Subject: Flood Warning

    Attention User,
    Flood Warning in your area """ + location
  
    try:
        mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
        mailServer.starttls()
        mailServer.login(gmailaddress , pwd)
        mailServer.sendmail(gmailaddress, mailto , message  )
        sendvalue="Successfully sent warning email to users in "+location+" area"
    except Exception:
        sendvalue="Error: unable to send email"
    mailServer.quit()
    return sendvalue
        

   
if __name__ == '__main__':
    app.run(port=5000, debug=True)
