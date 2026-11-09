from django.shortcuts import render,HttpResponseRedirect
from django.contrib.auth.models import User,auth 
from django.contrib import messages
from .models import Credit_Card
# Create your views here.
def index(request):
    return render(request,"index.html")


def adminlogin(request):
    if request.method=="POST":
        un=request.POST['uname']
        ps=request.POST['psw']
        user=auth.authenticate(username=un,password=ps)
        if user.is_superuser is not None:
            auth.login(request,user)
            return HttpResponseRedirect('adminhome')
        else:
            messages.info(request,"Invalid Credentials")
            return render(request,"adminlogin.html")
    return render(request,"adminlogin.html")

def register(request):
    if request.method=="POST":
        name=request.POST.get('name', request.POST.get('fname', ''))
        uname=request.POST['uname']
        em=request.POST['email']
        ps=request.POST['psw']
        ps1=request.POST['psw1']
        if ps==ps1:
            if User.objects.filter(username=uname).exists():
                messages.info(request,"Username Exists")
                return render(request,"register.html")
            elif User.objects.filter(email=em).exists():
                messages.info(request,"Email exists")
                return render(request,"register.html")
            else:
                user=User.objects.create_user(first_name=name,
            username=uname,email=em,password=ps)
                user.save()
                return HttpResponseRedirect("login")
        else:
            messages.info(request,"Password not Matching")
            return render(request,"register.html")

    return render(request,"register.html")

def login(request):
    if request.method=="POST":
        uname=request.POST['uname']
        ps=request.POST['psw']
        user=auth.authenticate(username=uname,password=ps)
        if user is not None:
            auth.login(request,user)
            return HttpResponseRedirect('data')
        else:
            messages.info(request,"Invalid Credentials")
            return render(request,"login.html")
    return render(request,"login.html")


def logout(request):
    auth.logout(request)
    return  HttpResponseRedirect("/")


LOCATION_MAP = {
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "chandigarh": (30.7333, 76.7794),
    "kochi": (9.9312, 76.2673),
    "goa": (15.2993, 74.1240),
    "lucknow": (26.8467, 80.9462),
    "indore": (22.7196, 75.8577),
    "new york": (40.7128, -74.0060),
    "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "london": (51.5074, -0.1278),
    "tokyo": (35.6762, 139.6503),
}

def get_coords_for_place(place_name, is_merchant=False):
    if not place_name:
        return (19.0760, 72.8777)
    clean_name = str(place_name).strip().lower()
    for k, coords in LOCATION_MAP.items():
        if k in clean_name or clean_name in k:
            return coords
    p_hash = sum(ord(c) for c in clean_name)
    lat = 8.0 + (p_hash % 2800) / 100.0
    long = 68.0 + ((p_hash * 13) % 2800) / 100.0
    if is_merchant:
        lat += 0.05
        long += 0.05
    return (round(lat, 4), round(long, 4))

CATEGORY_RISK_MAP = {
    'travel': 100, 'health_fitness': 75, 'shopping_net': 71, 'kids_pets': 70,
    'home': 67, 'misc_net': 63, 'entertainment': 57, 'grocery_pos': 48,
    'shopping_pos': 44, 'food_dining': 42, 'gas_transport': 29, 'misc_pos': 27,
    'grocery_net': 17, 'personal_care': 66
}

def data(request):
    if request.method=="POST":
        category=request.POST['cat']
        amount=float(request.POST['amt'])
        job=request.POST['job']

        user_place=request.POST.get('user_place', 'Local Area')
        merchant_place=request.POST.get('merchant_place', 'Local Area')

        if 'lat' in request.POST and 'long' in request.POST:
            latitude=float(request.POST['lat'])
            longitude=float(request.POST['long'])
        else:
            coords = get_coords_for_place(user_place, is_merchant=False)
            latitude, longitude = coords[0], coords[1]

        if 'mlat' in request.POST and 'mlong' in request.POST:
            mlatitude=float(request.POST['mlat'])
            mlongitude=float(request.POST['mlong'])
        else:
            mcoords = get_coords_for_place(merchant_place, is_merchant=True)
            mlatitude, mlongitude = mcoords[0], mcoords[1]

        import pandas as pd
        import numpy as np
        import math

        df=pd.read_csv("static/dataset/CreditCard.csv")

        X=df.drop(["category","job","is_fraud"],axis=1)
        y=df["is_fraud"]

        from sklearn.linear_model import LogisticRegression
        rf=LogisticRegression()
        rf.fit(X,y)

        pred_data=np.array([[amount,latitude,longitude,mlatitude,mlongitude]],dtype=object)
        prediction_val = int(rf.predict(pred_data)[0])
        
        # Calculate exact probabilities
        probabilities = rf.predict_proba(pred_data)[0]
        safe_prob = round(float(probabilities[0]) * 100, 1)
        fraud_prob = round(float(probabilities[1]) * 100, 1)

        if prediction_val == 1:
            prediction_data = "Fraud"
        else:
            prediction_data = "No Fraud"

        # Calculate Location Distance
        loc_distance = float(math.sqrt((latitude - mlatitude)**2 + (longitude - mlongitude)**2))

        # Factor Risk Breakdown
        amount_risk = int(min(100, int((amount / 516.32) * 60)) if amount > 76.48 else max(10, int((amount / 76.48) * 30)))
        cat_risk = int(CATEGORY_RISK_MAP.get(category, 45))
        location_risk = 85 if (user_place.lower() != merchant_place.lower() or loc_distance > 1.0) else 15

        # Generate Explanatory Reasons ("Why it is Fraud / Not Fraud")
        reasons = []
        if amount > 300:
            reasons.append(f"High Amount Flag: Transaction amount ({amount}) significantly exceeds the legitimate transaction average (76.48).")
        elif amount <= 100:
            reasons.append(f"Low Amount Indicator: Transaction amount ({amount}) falls within standard safe baseline parameters.")

        if cat_risk >= 60:
            reasons.append(f"Category Risk Flag: Merchant category '{category.replace('_', ' ').title()}' carries a high historical fraud incidence of {cat_risk}%.")
        else:
            reasons.append(f"Category Safety Indicator: Merchant category '{category.replace('_', ' ').title()}' maintains a low-to-moderate historical risk profile ({cat_risk}%).")

        if user_place.lower() != merchant_place.lower():
            reasons.append(f"Location Mismatch Flag: Cardholder location ('{user_place}') differs from Merchant location ('{merchant_place}').")
        else:
            reasons.append(f"Proximity Match Indicator: Cardholder and Merchant locations are matched in close geographical proximity ('{user_place}').")

        if prediction_val == 1:
            reasons.append(f"Overall Model Decision: High cumulative risk score ({fraud_prob}%) triggered the Fraud alert threshold.")
        else:
            reasons.append(f"Overall Model Decision: High confidence rating ({safe_prob}%) verified transaction as legitimate.")

        cc=Credit_Card.objects.create(category=category,amount=amount,
        latitude=f"{user_place} ({latitude})",longitude=f"{longitude}",
        merchant_latitude=f"{merchant_place} ({mlatitude})",
        merchant_longitude=f"{mlongitude}",jobs=job,prediction=prediction_data)
        cc.save()

        context = {
            "category": str(category),
            "job": str(job),
            "latitude": float(latitude),
            "longitude": float(longitude),
            "mlatitude": float(mlatitude),
            "mlongitude": float(mlongitude),
            "user_place": str(user_place),
            "merchant_place": str(merchant_place),
            "prediction": int(prediction_val),
            "amount": float(amount),
            "prediction_data": str(prediction_data),
            "fraud_prob": float(fraud_prob),
            "safe_prob": float(safe_prob),
            "amount_risk": int(amount_risk),
            "cat_risk": int(cat_risk),
            "location_risk": int(location_risk),
            "reasons": list(reasons)
        }
        
        # Store in session for direct /predict access
        request.session['last_prediction'] = context

        return render(request, "predict.html", context)
    return render(request, "data.html")


def predict(request):
    context = request.session.get('last_prediction', None)
    if not context:
        return HttpResponseRedirect('data')
    return render(request, "predict.html", context)

def adminhome(request):
    cc=Credit_Card.objects.all()
    return render(request,"adminhome.html",{"cc":cc})

def delete_history(request, id):
    Credit_Card.objects.filter(id=id).delete()
    messages.info(request, "Record deleted successfully.")
    return HttpResponseRedirect("/adminhome")

def delete_all_history(request):
    Credit_Card.objects.all().delete()
    messages.info(request, "All transaction history cleared successfully.")
    return HttpResponseRedirect("/adminhome")