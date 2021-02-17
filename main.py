from flask import Flask,jsonify
import requests
import bs4
from bs4 import BeautifulSoup as bs
import lxml
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.config['JSON_SORT_KEYS'] = False

def WeatherScraping(url,headers):
    response = requests.get(url, headers=headers).text
    soup = bs(response, 'lxml')
    data = []
    table = soup.find('table', id="wt-hbh")
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip().replace(u'\xa0', u' ') for ele in cols]
        data.append([ele for ele in cols if ele])

    resetdata = []

    for i in data:
        resetdata.append(
            {'temperature': i[0], "weather": i[1], "feelsLike": i[2][:3], 'windSpeed': i[3], "humidity": i[5],
             "precipitationChance": i[6], "precipitationAmount": i[7]})

    return resetdata


def citytime(url,headers):
    response = requests.get(url, headers=headers).text
    soup = bs(response, 'lxml')
    alltime = []
    for i in soup.find_all('tr'):
        try:
            x = (i.find('th').text).replace(u'\xa0', '')
            if x != 'Time':
                alltime.append(x[:5])  # time
            else:
                pass
        except:
            pass

    time = []
    for i in alltime[1:]:
        if float(i) >= 12:
            time.append(i + 'PM')
        else:
            time.append(i + 'AM')

    return time





@app.route('/api/<string:city>')
def data(city):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    url = 'https://www.timeanddate.com/weather/india/{}/hourly'.format(city)

    data = WeatherScraping(url,headers)

    time = citytime(url,headers)

    final = []
    for i, j in zip(time, data):
        final.append([{'time':i},{'weatherupdate':j}])

    result = {
        'city': city,
        'hourlyUpdates':final
    }

    return jsonify(result)





if __name__=="__main__":
    app.run(debug=True)