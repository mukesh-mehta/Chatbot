from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from rasa_dm.actions.action import Action
from rasa_dm.policies.keras_policy import KerasPolicy
from rasa_dm.events import SetSlot,PauseConversation


from bs4 import BeautifulSoup
#from OTP import sendSms as SMS
from rasa_dm.channels.facebook import MessengerBot
from goibibo.GoAPICalls import goibibo
from txt2num import text2num
from operator import itemgetter
from date import magicdate
import json

logger = logging.getLogger(__name__)
access_token = #facebook page access token

MB = MessengerBot(access_token)

#****************************************************
class ActionHowCanHelp(Action):
	def name(self):
		return "ask_howcanhelp"

	def run(self,dispatcher,tracker,domain):
		details = MB.get_user_details(dispatcher.sender)
		try:
			msg="Hello " +str(details['first_name']) +", I am your Travel assistant.I can help you book flights."
		except:
			msg="Hello! your Travel assistant.I can help you book flights."
		start_msg={
		"text":msg,
		"quick_replies":[
		{
		"content_type":"text",
		"title":'one way flight',
		"payload":"one way flight"
		},
		{
		"content_type":"text",
		"title":'Return Flight',
		"payload":"Return Flight"
		}]}
		MB.send_fb_message(dispatcher.sender,start_msg)
		return[]
#****************************************************
class ActionHelpMore(Action):
	def name(self):
		return "ask_helpmore"

	def run(self,dispatcher,tracker,domain):
		dispatcher.utter_message("is there anything more that I can help with?")
		#MB.send_custom_message(dispatcher.sender,start_elements)
		return[]
#****************************************************
class ActionStoreOrigin(Action):
	def name(self):
		return "store_origin"

	def run(self, dispatcher, tracker, domain):
		value = next((x["value"] for x in tracker.latest_message.entities if x['entity'] == 'location'), None)
		return [SetSlot("origin", value)]
#*****************************************************
class ActionStoreDestination(Action):
	def name(self):
		return "store_destination"

	def run(self, dispatcher, tracker, domain):
		value = next((x["value"] for x in tracker.latest_message.entities if x['entity'] == 'location'), None)
		return [SetSlot("destination", value)]
#*****************************************************
class ActionStoreReturnDate(Action):
	def name(self):
		return "store_return_date"

	def run(self, dispatcher, tracker, domain):
		value = next((x["value"] for x in tracker.latest_message.entities if x['entity'] == 'date'), None)
		return [SetSlot("return_date", value)]
#*****************************************************
class ActionStoreDate(Action):
	def name(self):
		return "store_date"

	def run(self, dispatcher, tracker, domain):
		value = next((x["value"] for x in tracker.latest_message.entities if x['entity'] == 'date'), None)
		return [SetSlot("date_on", value)]		
#*****************************************************
class ActionStoreReturnBook(Action):
	def name(self):
		return "store_return_book"

	def run(self, dispatcher, tracker, domain):
		value = tracker.latest_message.text
		return [SetSlot("book_return", value),SetSlot("count",0)]
#******************************************************
class ActionStoreBook(Action):
	def name(self):
		return "store_book"

	def run(self, dispatcher, tracker, domain):
		value = tracker.latest_message.text
		return [SetSlot("book", value),SetSlot("count", 0)]
#******************************************************
class ActionCleanSlots(Action):
	def name(self):
		return "clean_slots"

	def run(self, dispatcher, tracker, domain): 
		return [SetSlot("date",'' ),SetSlot("destination",'' ),SetSlot("origin",'' ),SetSlot("count",0 ),SetSlot("flight_oneway",'' ),SetSlot("flight_return",'' ),SetSlot("location",'' )]
#**********************************************
class ActionMoreUpdates(Action):
	@classmethod
	def name(cls):
		return 'ask_moreupdates'

	@classmethod
	def run(cls, dispatcher, tracker, domain):
		dispatcher.utter_message("anything else you'd like to modify?")
		print(tracker.latest_message.intent)
		print(tracker.latest_message.entities)
		return[SetSlot("count",0),SetSlot("flight_oneway", None),SetSlot("flight_return", None)]
#************************************
class ActionFlightOffer(Action):
	@classmethod
	def name(cls):
		return 'flight_offer'

	@classmethod
	def run(cls, dispatcher, tracker, domain):
		elements=[{
		"title":"Air India Sale",
		"subtitle":"Airfares starting @ Rs. 425* (all inclusive) \nValid till:20th Nov 2017"
		},{
		"title":"Qatar Airways Sale",
		"subtitle":"Discounts upto 35%% on Europe/UK/USA flights \nValid till:23rd Nov 2017"
		},{
		"title":"Destination Abroad",
		"subtitle":"Get upto Rs.15000 off on Int'l flights!\nValid till:24th Nov 2017"
		}]
		MB.send_custom_message(dispatcher.sender,elements)
		return[]
#*******************************************************
class ActionSearchFlight(Action):
	@classmethod
	def name(cls):
		return 'search_flights'

	@classmethod
	def run(cls, dispatcher, tracker, domain):
		origin = tracker.get_slot('origin')
		destination = tracker.get_slot('destination')
		try:
			people=text2num(tracker.get_slot('people'))
		except:
			people=tracker.get_slot('people')
		print(origin)
		print(destination)
		date = tracker.get_slot('date_on')
		date = str(magicdate.magicdate(date))
		print(date)
		count=tracker.get_slot('count')
		if count is None:
			start=0
		else:
			start=count
		print(start)
		end=start+3
		print(end)
		try:
			flight_oneway=tracker.get_slot('flight_oneway')
			if flight_oneway is None:
				print('none')
				flight=goibibo.getFlightsResp(origin,destination,date,people)
				flight["onward"] = sorted(flight["onward"], key=itemgetter('fare'))
			else:
				flight=	flight_oneway
				flight["onward"] = sorted(flight["onward"], key=itemgetter('fare'))
			elements=[]
			heading={
			"title": str(flight["onward"][0]["origin"])+" To "+str(flight["onward"][0]["destination"]),
			"subtitle": str(date),
			"image_url": "http://i.ebayimg.com/00/s/Mzk4WDUwMA==/z/YJEAAMXQlgtS-0Yc/$_3.JPG?set_id=2",
			}
			elements.append(heading)
			for i in range(start,end):
				buttons=[]
				button={
					"type":"postback",
					"title":"Book",
					"payload":str(flight["onward"][i]["flight_number"])+" "+str(flight["onward"][i]["origin"])+" "+str(flight["onward"][i]["destination"])+" "+str(flight["onward"][i]["departure"])+" "+str(flight["onward"][i]["arrival"])+" "+str(flight["onward"][i]["basefare"])+" "+str(flight["onward"][i]["fare"])
					}
				buttons.append(button)	
				element = {
				"title":str(flight["onward"][i]['airline']),
				"subtitle":"Fare: "+str(flight["onward"][i]['fare'])+" Duration: "+str(flight["onward"][i]['duration'])+"\nDeparture: "+ str(flight["onward"][i]['departure_time'])+" Arrival: "+ str(flight["onward"][i]['arrival_time']),
				"buttons":buttons
				}
				elements.append(element)
			button=[
			{
			"title": "View More",
			"type": "postback",
			"payload": "More"           
			}]
			MB.send_custom_list_message(dispatcher.sender,elements,button)
		except:
			elements=[
			{
			"title":"Sorry!",
			"subtitle":"I am still learning,I could not figure out what you want. you can start over.",
			"buttons":[
			{
			"type":"postback",
			"title":"Start Over",
			"payload":"Get started"
			}]
			}]
			MB.send_custom_message(dispatcher.sender,elements)
		return [SetSlot("flight_oneway", flight), SetSlot("count",end),SetSlot("origin",origin),SetSlot("destination",destination),SetSlot("people",people),SetSlot("date_on",date)]
#*************************************************************
class ActionItinerary(Action):
	@classmethod
	def name(self):
		return 'show_itinerary'

	def run(self, dispatcher, tracker, domain):
		print("ITIHNGGFB")
		import random
		from goibibo.Configs.IATADatabase import iata_dicts
		details = MB.get_user_details(dispatcher.sender)
		num_people=tracker.get_slot('people')
		name=[]
		if num_people==1:
			name.append(tracker.latest_message.text)
		else:
			name_text=tracker.latest_message.text
			name=name_text.split(',')
		info = tracker.get_slot('book')
		print(info)
		return_info=tracker.get_slot('book_return')
		info_=[]
		if return_info is None:
			info_=[info]
		#if info is None:
		#	info_=[return_info]	
		else:
			info_=[info,return_info]
		print(info_)	
		payload_data=[]	
		for info in info_:
			data={}
			data['flight_number']=info.split(" ")[0]
			data['departure']=info.split(" ")[1]
			departure=info.split(" ")[1]
			data['arrival']=info.split(" ")[2]
			arrival=info.split(" ")[2]
			departure_time=info.split(" ")[3]
			data['departure_time'] = str(departure_time[0:13]+":"+departure_time[13:15])
			arrival_time=info.split(" ")[4]
			data['arrival_time'] = str(arrival_time[0:13]+":"+arrival_time[13:15])
			data['class_'] = "economy"
			data['basefare']=info.split(" ")[5]
			data['fare']=info.split(" ")[6]
			departure_city=None
			arrival_city = None
			for iata_dict in iata_dicts:
				if(iata_dicts[iata_dict]['code'].lower()==departure.lower()):
					data['departure_city']= iata_dicts[iata_dict]['city']

				if(iata_dicts[iata_dict]['code'].lower()==arrival.lower()):
					data['arrival_city']= iata_dicts[iata_dict]['city']
			payload_data.append(data)
			
		#MB.send_fb_message(dispatcher.sender,message_guidedflow)
		passenger_info=[]
		passenger_segment_info=[]
		i=1

		for nam in name:
			M={
				"name": nam,
				"ticket_number": str(random.randint(8156,8716)),
				"passenger_id": "p00"+str(i)
				}
			print(M)	
			passenger_info.append(M)
			i+=1
		for i in range(0,len(payload_data)):
			for q in range(0,len(name)):
				MN={
					"segment_id": "s00"+str(i+1),
					"passenger_id": "p00"+str(q+1),
					"seat": random.choice("ABCDEF")+str(random.randint(1,116)),
					"seat_type": payload_data[0]['class_']
					}
				passenger_segment_info.append(MN)

		flight_info=[]
		j=1
		for p in payload_data:
			n={
			"connection_id": "c00"+str(j),
			"segment_id": "s00"+str(j),
			"flight_number": p['flight_number'],
			"departure_airport": {
			"airport_code": p['departure'],
			"city": p['departure_city']
			},
			"arrival_airport": {
			"airport_code": p['arrival'],
			"city": p['arrival_city']
			},
			"flight_schedule": {
			"departure_time": p['departure_time'],
			"arrival_time": p['arrival_time']
			},
			"travel_class": p['class_']
			}
			flight_info.append(n)
			j+=1

		if return_info is None:
		#if info is None:
			price=[
			{
			"title": "Base fare",
			"amount":payload_data[0]['basefare'],
			"currency": "INR"
			}]
		else:
			price=[
			{
			"title": "Base fare",
			"amount":str(int(payload_data[0]['basefare'])+int(payload_data[1]['basefare'])),
			"currency": "INR"
			}]
		if return_info is None:
		#if info is None:
			fare=payload_data[0]['fare']
		else:
			fare=str(int(payload_data[0]['fare'])+int(payload_data[1]['fare']))

		payload= {
		"template_type": "airline_itinerary",
		"intro_message": "Here is your flight itinerary.",
		"locale": "en_US",
		"theme_color": "#dc3f00",
		"pnr_number": str(random.randint(85487956,87167186)),
		"passenger_info":passenger_info ,
		"flight_info": flight_info,
		"passenger_segment_info": passenger_segment_info,
		"price_info": price,
		"total_price":fare,
		"currency": "INR"
		}
		from pprint import pprint
		pprint(payload)
		MB.send_itinerary(dispatcher.sender,payload)
		return []
#***********************************************************
class ActionReturnFlight(Action):
	@classmethod
	def name(cls):
		return 'search_return_flights'

	@classmethod
	def run(cls,dispatcher,tracker,domain):
		print('return_flight running')
		origin = tracker.get_slot('origin')
		destination = tracker.get_slot('destination')
		print(origin)
		print(destination)
		try:
			people=text2num(tracker.get_slot('people'))
		except:
			people=tracker.get_slot('people')
		date = tracker.get_slot('date_on')
		date = str(magicdate.magicdate(date))
		return_date=tracker.get_slot('return_date')
		return_date = str(magicdate.magicdate(return_date))
		print(date)
		print(return_date)
		count=tracker.get_slot('count')
		if count is None:
			start=0
		else:
			start=count
		end=start+3
		try:
			flight_return=tracker.get_slot('flight_return')
			if flight_return is None:
				print('none')
				flight=goibibo.getFlightsResp_return(origin,destination,date,return_date,people)
				flight["return"] = sorted(flight["return"], key=itemgetter('fare'))
			else:
				flight=	flight_return
				flight["return"] = sorted(flight["return"], key=itemgetter('fare'))
			elements=[]
			heading={
			"title": str(flight["return"][0]["origin"])+" To "+str(flight["return"][0]["destination"]),
			"subtitle": str(return_date),
			"image_url": "http://i.ebayimg.com/00/s/Mzk4WDUwMA==/z/YJEAAMXQlgtS-0Yc/$_3.JPG?set_id=2",
			}
			elements.append(heading)
			for i in range(start,end):
				buttons=[]
				button={
					"type":"postback",
					"title":"Book",
					"payload":str(flight["return"][i]["flight_number"])+" "+str(flight["return"][i]["origin"])+" "+str(flight["return"][i]["destination"])+" "+str(flight["return"][i]["departure"])+" "+str(flight["return"][i]["arrival"])+" "+str(flight["return"][i]["basefare"])+" "+str(flight["return"][i]["fare"])
					}
				buttons.append(button)	
				element = {
				"title":str(flight["return"][i]['airline']),
				"subtitle":"Fare: "+str(flight["return"][i]['fare'])+" Duration: "+str(flight["return"][i]['duration'])+"\nDeparture: "+ str(flight["return"][i]['departure_time'])+" Arrival: "+ str(flight["return"][i]['arrival_time']),
				"buttons":buttons
				}
				elements.append(element)
			button=[
			{
			"title": "View More",
			"type": "postback",
			"payload": "More"           
			}]
			MB.send_custom_list_message(dispatcher.sender,elements,button)
		except:
			elements=[
			{
			"title":"Sorry!",
			"subtitle":"I am still learning,I could not figure out what you want. you can start over.",
			"buttons":[
			{
			"type":"postback",
			"title":"Start Over",
			"payload":"Get started"
			}]
			}]
			MB.send_custom_message(dispatcher.sender,elements)
		return [SetSlot("flight_return", flight), SetSlot("count",end),SetSlot("origin",origin),SetSlot("destination",destination),SetSlot("people",people),SetSlot("date_on",date)]
#****************************************************
class ActionCancel(Action):
	@classmethod
	def name(self):
		return 'cancel'

	def run(self, dispatcher, tracker, domain):
		msg="Do you want to end current conversation?"
		cancel={
		"text":msg,
		"quick_replies":[
		{
		"content_type":"text",
		"title":'yes',
		"payload":"yes"
		},
		{
		"content_type":"text",
		"title":"No",
		"payload":"No"
		}]}
		MB.send_fb_message(dispatcher.sender,cancel)
		return []
#****************************************************
class ActionBye(Action):

	@classmethod
	def name(self):
		return 'say_bye'

	def run(self, dispatcher, tracker, domain):
		from emoji import core
		quick_reply={
		"text":"I believe, you found what you were looking for. Please feel free to ping me in case you need me. Always happy to help.\nPlease give feedback.",
		"quick_replies":[
		{
		"content_type":"text",
		"title":core.emojize(':thumbs_up:'),
		"payload":"good"
		},
		{
		"content_type":"text",
		"title":core.emojize(':thumbs_down:'),
		"payload":"very bad"
		}]}
		MB.send_fb_message(dispatcher.sender,quick_reply)
		return[]
#********************************************************************	
class RasaPolicy(KerasPolicy):
    def _build_model(self, num_features, num_actions, max_history_len):
        """Build a keras model and return a compiled model.
        :param max_history_len: The maximum number of historical turns used to decide on next action"""
        from keras.layers import LSTM, Activation, Masking, Dense
        from keras.models import Sequential

        n_hidden = 80  # size of hidden layer in LSTM
        # Build Model
        model = Sequential()
        model.add(Masking(-1, batch_input_shape=(None, max_history_len, num_features)))
        model.add(LSTM(n_hidden, batch_input_shape=(None, max_history_len, num_features)))
        model.add(Dense(input_dim=n_hidden, output_dim=num_actions))
        model.add(Activation('softmax'))

        model.compile(loss='categorical_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        logger.debug(model.summary())
        return model