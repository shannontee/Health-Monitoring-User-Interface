from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
import pyrebase
from django.contrib import auth
from datetime import datetime
from datetime import timedelta
import time
import pandas as pd
from django.http import HttpResponse
import pytz

# Connection to Firebase Database
config={
    "apiKey": "AIzaSyAwHaQ7P6QFCBMjGN3NdBkBIYEJb6g5N1o",
    "authDomain": "inf551-3a4c2.firebaseapp.com",
    "databaseURL": "https://inf551-3a4c2.firebaseio.com",
    "projectId": "inf551-3a4c2",
    "storageBucket": "inf551-3a4c2.appspot.com",
    "messagingSenderId": "2890826953"
  }

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
database=firebase.database()

# Dataframes to store data from Firebase
scale_df = pd.DataFrame(columns = ['Date', 'Weight', 'BMI', 'BodyFat'])
sleep_df = pd.DataFrame(columns = ['Date', 'Hours', 'Breathing', 'Temp'])
watch_df = pd.DataFrame(columns = ['Date', 'Steps', 'Highest HR', 'Calories'])
summary_df = pd.DataFrame(columns = ['Date', 'Steps', 'Calories', 'Hours', 'Weight', 'BMI'])


# CODE FOR SCALE USER INTERFACE
class HomeViewScale(View):

    scale_status = list((database.child('status').get().val())['scale'].items())[-1][1]

    def get(self, request, *args, **kwargs):

        # Get data from database
        data = database.child('scale').get().val()
        status = database.child('status').get().val()

        scale_status = list(status['scale'].items())[-1][1]

        # If user selects specific start/end dates
        if ('dates' in request.GET) and (request.GET['start_date'] != '') and (request.GET['end_date'] != ''):
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']

        else:
            start_date = '12-01-2018'
            end_date = '04-22-2019'

        # Clear previously saved dataframe
        global scale_df 
        scale_df = scale_df.iloc[0:0]

        # Go through data from database and save in dataframe for those between start and end date
        i = 0
        for item in data:
            day = list(item.keys())[0]

            day_temp = day.replace('-', '/')
            day_temp = datetime.strptime(day_temp, '%m/%d/%Y')
            start_date_c = start_date.replace('-', '/')
            start_date_c= datetime.strptime(start_date_c, '%m/%d/%Y')

            end_date_c = end_date.replace('-', '/')
            end_date_c = datetime.strptime(end_date_c, '%m/%d/%Y')

            if (day_temp <= end_date_c) and (day_temp >= start_date_c):
                weight = item[day]['weight']
                bmi = item[day]['bmi']
                body = item[day]['body fat']

                day = day.replace('-', '/')
                day = datetime.strptime(day, '%m/%d/%Y')
                day = day.strftime('%B %d, %Y')

                scale_df.loc[i] = [day, weight, bmi, body]
                i += 1

        # Find averages based on dataframe
        avg_weight = round(scale_df['Weight'].mean(),2)
        avg_bmi = round(scale_df['BMI'].mean(),2)
        avg_body = round(scale_df['BodyFat'].mean(),2)
        last_sync = list(data[-1].keys())[0]

        # If user presses ON/OFF button
        if 'device' in request.GET:
            last_status = list(status['scale'].items())[-1][1] # Find current status
            today_date = str(datetime.now(pytz.timezone('US/Pacific')))[0:19] #  Current timestamp
            data = status['scale'] 

            if last_status == 0:
                data[today_date] = 1
            else:
                data[today_date] = 0

            # Input new device status into database
            database.child("status").child("scale").set(data)

        # Get new device status
        status = database.child('status').get().val()
        scale_status = list(status['scale'].items())[-1][1]

        if scale_status == 1:
            self.scale_status = 'ON'
        else:
            self.scale_status = 'OFF'

        return render(request, 'scale.html', {'last_sync': last_sync, 'avg_weight': avg_weight,\
                                        'avg_bmi': avg_bmi, 'avg_body': avg_body, 'scale_status': self.scale_status,\
                                        'start_date': start_date, 'end_date': end_date})


def get_data_scale(request, *args, **kwargs):
    return JsonResponse(data)

# Get data for graphs
class ChartDataScale(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = scale_df.iloc[:,0]
        weight_items = scale_df.iloc[:,1]
        bmi_items = scale_df.iloc[:,2]
        body_items = scale_df.iloc[:,3]
        data = { "labels": labels, "weight" : weight_items, "bmi": bmi_items, "body": body_items}

        return Response(data)

# CODE FOR SLEEP USER INTERFACE
class HomeViewSleep(View):
    sleep_status = list((database.child('status').get().val())['sleep'].items())[-1][1]

    def get(self, request, *args, **kwargs):

        # Get data from database
        data = database.child('sleep').get().val()
        status = database.child('status').get().val()

        sleep_status = list(status['sleep'].items())[-1][1]

        # If user selects specific start/end dates
        if ('dates' in request.GET) and (request.GET['start_date'] != '') and (request.GET['end_date'] != ''):
                start_date = request.GET['start_date']
                end_date = request.GET['end_date']
        else:
            start_date = '12-01-2018'
            end_date = '04-22-2019'

        # Clear previously saved dataframe
        global sleep_df 
        sleep_df = sleep_df.iloc[0:0]

        # Go through data from database and save in dataframe for those between start and end date
        i = 0
        for item in data:
            day = list(item.keys())[0]

            day_temp = day.replace('-', '/')
            day_temp = datetime.strptime(day_temp, '%m/%d/%Y')
            start_date_c = start_date.replace('-', '/')
            start_date_c= datetime.strptime(start_date_c, '%m/%d/%Y')

            end_date_c = end_date.replace('-', '/')
            end_date_c = datetime.strptime(end_date_c, '%m/%d/%Y')

            if (day_temp <= end_date_c) and (day_temp >= start_date_c):
                hours = item[day]['hours']
                breathing = item[day]['breathing']
                temp = item[day]['temp']

                day = day.replace('-', '/')
                day = datetime.strptime(day, '%m/%d/%Y')
                day = day.strftime('%B %d, %Y')

                sleep_df.loc[i] = [day, hours, breathing, temp]
                i += 1

         # Find averages based on dataframe
        avg_hours = round(sleep_df['Hours'].mean(),2)
        avg_breathing = round(sleep_df['Breathing'].mean(),2)
        avg_temp = round(sleep_df['Temp'].mean(),2)
        last_sync = list(data[-1].keys())[0]

        # If user presses ON/OFF button
        if 'device' in request.GET:    
            last_status = list(status['sleep'].items())[-1][1]
            today_date = str(datetime.now(pytz.timezone('US/Pacific')))[0:19]
            data = status['sleep']

            if last_status == 0:
                data[today_date] = 1
            else:
                data[today_date] = 0

            database.child("status").child("sleep").set(data)  # Input new device status into database

        # Get new device status
        status = database.child('status').get().val()
        sleep_status = list(status['sleep'].items())[-1][1]

        if sleep_status == 1:
            self.sleep_status = 'ON'
        else:
            self.sleep_status = 'OFF'

        return render(request, 'sleep.html', {'last_sync': last_sync, 'avg_hours': avg_hours,\
                                        'avg_breathing': avg_breathing, 'avg_temp': avg_temp, 'sleep_status': self.sleep_status,\
                                        'start_date': start_date, 'end_date': end_date})

def get_data_sleep(request, *args, **kwargs):
    return JsonResponse(data)

# Get data for graphs
class ChartDataSleep(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = sleep_df.iloc[:,0]
        hours_items = sleep_df.iloc[:,1]
        breathing_items = sleep_df.iloc[:,2]
        temp_items = sleep_df.iloc[:,3]
        data = { "labels": labels, "hours" : hours_items, "breathing": breathing_items, "temp": temp_items}
        return Response(data)

# CODE FOR WATCH USER INTERFACE
class HomeViewWatch(View):
    watch_status = list((database.child('status').get().val())['watch'].items())[-1][1]

    def get(self, request, *args, **kwargs):

        # Get data from database
        data = database.child('watch').get().val()
        status = database.child('status').get().val()

        sleep_status = list(status['watch'].items())[-1][1]

        # If user selects specific start/end dates
        if ('dates' in request.GET) and (request.GET['start_date'] != '') and (request.GET['end_date'] != ''):
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']

        else:
            start_date = '12-01-2018'
            end_date = '04-22-2019'

        # Clear previously saved dataframe
        global watch_df 
        watch_df = watch_df.iloc[0:0]

        # Go through data from database and save in dataframe for those between start and end date
        i = 0
        for item in data:
            day = list(item.keys())[0]

            day_temp = day.replace('-', '/')
            day_temp = datetime.strptime(day_temp, '%m/%d/%Y')
            start_date_c = start_date.replace('-', '/')
            start_date_c= datetime.strptime(start_date_c, '%m/%d/%Y')

            end_date_c = end_date.replace('-', '/')
            end_date_c = datetime.strptime(end_date_c, '%m/%d/%Y')

            if (day_temp <= end_date_c) and (day_temp >= start_date_c):
                steps = item[day]['steps']
                highest_HR = item[day]['highest_hr']
                calories = item[day]['calories']

                day = day.replace('-', '/')
                day = datetime.strptime(day, '%m/%d/%Y')
                day = day.strftime('%B %d, %Y')

                watch_df.loc[i] = [day, steps, highest_HR, calories]
                i += 1

         # Find averages based on dataframe
        avg_steps = int(watch_df['Steps'].mean())
        avg_hHR = round(watch_df['Highest HR'].mean(),2)
        avg_calories = round(watch_df['Calories'].mean(),2)
        last_sync = list(data[-1].keys())[0]

        # If user presses ON/OFF button
        if 'device' in request.GET:   
            last_status = list(status['watch'].items())[-1][1]
            today_date = str(datetime.now(pytz.timezone('US/Pacific')))[0:19]
            data = status['watch']

            if last_status == 0:
                data[today_date] = 1
            else:
                data[today_date] = 0

            database.child("status").child("watch").set(data) # Input new device status into database

        # Get new device status
        status = database.child('status').get().val()
        watch_status = list(status['watch'].items())[-1][1]

        if watch_status == 1:
            self.watch_status = 'ON'
        else:
            self.watch_status = 'OFF'

        return render(request, 'watch.html', {'last_sync': last_sync, 'avg_steps': avg_steps,\
                                        'avg_hHR': avg_hHR, 'avg_calories': avg_calories, 'watch_status': self.watch_status,\
                                        'start_date': start_date, 'end_date': end_date})

def get_data_watch(request, *args, **kwargs):
    return JsonResponse(data)

# Get data for graphs
class ChartDataWatch(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = watch_df.iloc[:,0]
        steps_items = watch_df.iloc[:,1]
        hHR_items = watch_df.iloc[:,2]
        calories_items = watch_df.iloc[:,3]
        data = { "labels": labels, "steps" : steps_items, "hHR": hHR_items, "calories": calories_items}
        return Response(data)


# CODE FOR SUMMARY HTML
class HomeViewSummary(View):
    def get(self, request, *args, **kwargs):

        # Clear previously saved dataframe
        global summary_df 
        summary_df = summary_df.iloc[0:0]

        # Select last 7 days of data
        start_date = '04-15-2019'
        end_date = '04-22-2019'

        # Get data from database
        watch_data = database.child('watch').get().val()
        scale_data = database.child('scale').get().val()
        sleep_data = database.child('sleep').get().val()


        i = 0
        days = []
        steps = []
        calories = []
        hours = []
        weight = []
        bmi = []
        hours = []


        # Pull data from each device for last 7 days and store in dataframe
        for item in watch_data:
            day = list(item.keys())[0]

            day_temp = day.replace('-', '/')
            day_temp = datetime.strptime(day_temp, '%m/%d/%Y')
            start_date_c = start_date.replace('-', '/')
            start_date_c = datetime.strptime(start_date_c, '%m/%d/%Y')

            end_date_c = end_date.replace('-', '/')
            end_date_c = datetime.strptime(end_date_c, '%m/%d/%Y')
            today_date = str(datetime.now(pytz.timezone('US/Pacific')))[0:19]

            if (day_temp <= end_date_c) and (day_temp >= start_date_c):
                
                steps.append(item[day]['steps'])
                calories.append(item[day]['calories'])

                day = day.replace('-', '/')
                day = datetime.strptime(day, '%m/%d/%Y')
                day = day.strftime('%B %d, %Y')

                days.append(day)

        for item in scale_data:
            day = list(item.keys())[0]

            day_temp = day.replace('-', '/')
            day_temp = datetime.strptime(day_temp, '%m/%d/%Y')
            start_date_c = start_date.replace('-', '/')
            start_date_c = datetime.strptime(start_date_c, '%m/%d/%Y')

            end_date_c = end_date.replace('-', '/')
            end_date_c = datetime.strptime(end_date_c, '%m/%d/%Y')

            if (day_temp <= end_date_c) and (day_temp >= start_date_c):
                
                weight.append(item[day]['weight'])
                bmi.append(item[day]['bmi'])

        for item in sleep_data:
            day = list(item.keys())[0]

            day_temp = day.replace('-', '/')
            day_temp = datetime.strptime(day_temp, '%m/%d/%Y')
            start_date_c = start_date.replace('-', '/')
            start_date_c = datetime.strptime(start_date_c, '%m/%d/%Y')

            end_date_c = end_date.replace('-', '/')
            end_date_c = datetime.strptime(end_date_c, '%m/%d/%Y')

            if (day_temp <= end_date_c) and (day_temp >= start_date_c):
                
                hours.append(item[day]['hours'])

        summary_df['Date'] = days
        summary_df['Steps'] = steps
        summary_df['Calories'] = calories
        summary_df['Weight'] = weight
        summary_df['BMI'] = bmi
        summary_df['Hours'] = hours

        # Find sum and averages for different metrics
        sum_calories = round(sum(summary_df['Calories']),1)
        avg_weight = round(summary_df['Weight'].mean(),2)
        avg_bmi = round(summary_df['BMI'].mean(),2)
        sum_hours = round(sum(summary_df['Hours']),1)

        # Find percentages towards weekly goals
        hours_goal = int(sum_hours / 62 * 100)
        calories_goal = int(sum_calories / 5600 * 100)

        return render(request, 'summary.html', {'sum_calories': sum_calories, 'avg_weight': avg_weight, 'avg_bmi': avg_bmi, 'sum_hours': sum_hours, 'hours_goal':hours_goal, 'calories_goal': calories_goal})

def get_data_summary(request, *args, **kwargs):
    return JsonResponse(data)

# Get data for graphs
class ChartDataSummary(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = summary_df.iloc[:,0]
        steps_items = summary_df.iloc[:,1]
        data = { "labels": labels, "steps" : steps_items}
        return Response(data)


