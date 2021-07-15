import os, io
from rest_framework.views import APIView
import json
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import View
from rest_framework import views
from rest_framework.parsers import MultiPartParser,FileUploadParser
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import serializers
from google.cloud import vision
import pandas as pd
import re
import phonenumbers
from urlextract import URLExtract
import tldextract
import difflib
import itertools
from pathlib import Path

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from phonenumbers import timezone
from phonenumbers import geocoder
from urlextract import URLExtract
from pathlib import Path
import requests
from urllib.parse import urlencode






class FileView(views.APIView):
    parser_classes = (JSONParser, MultiPartParser)



    def post(self, request, format='None'):
        up_file = request.FILES['file']
        # do some stuff with uploaded image

        


        BASE_DIR = Path(__file__).resolve().parent.parent


        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f"{BASE_DIR}/file_name"

        client = vision.ImageAnnotatorClient()

        
        # file_name = '1'
        # image_path = f'{BASE_DIR}/{file_name}'
        # title_path= f'{BASE_DIR}/{file_name1}'
        
        with up_file.open("rb") as image_file:
            content = image_file.read()
       
        # construct an iamge instance
        image = vision.Image(content=content)
       


        """
        # or we can pass the image url
        image = vision.types.Image()
        image.source.image_uri = ''
        """
       



        api_key = ""

        data_type = 'json'
        endpoint = f"https://maps.googleapis.com/maps/api/geocode/{data_type}"

        def extract_adr(address_or_postalcode, data_type = 'json'):
            endpoint = f"https://maps.googleapis.com/maps/api/geocode/{data_type}"
            params = {"address": address_or_postalcode, "key": api_key}
            url_params = urlencode(params)
            url = f"{endpoint}?{url_params}"
            r = requests.get(url)
            if r.status_code not in range(200, 299):
                return {}
            address = ''
            try:
                address = r.json()['results'][0]['formatted_address']
            except:
                pass
            return address

        # annotate Image Response
        response = client.text_detection(image=image)  # returns TextAnnotation

        df = pd.DataFrame(columns=['locale', 'description'])

        
        texts = response.text_annotations

        del response     # to clean-up the system memory
        print(texts[0].description)

        
       





        for text in texts:

            df = df.append(
                dict(
                    locale=text.locale,
                    description=text.description
                ),
                ignore_index=True
            )

        a = df['description'][0]

        df1 = df.iloc[1:]


        list_values = df1['description'].to_list()
        print(list_values)


        



        # phone country
        for find_phone in phonenumbers.PhoneNumberMatcher(list_values, ""):
            tel = phonenumbers.format_number(find_phone.number, phonenumbers.PhoneNumberFormat.E164)
            country_number = phonenumbers.parse(tel, "")
            country_tup = timezone.time_zones_for_number(country_number)
            country = geocoder.description_for_number(country_number, "eu")
            # print(country)

          


        #find adress
        adres_row = extract_adr({list_values})
        
        
        return HttpResponse( json.dumps( list_values , safe = False ))
