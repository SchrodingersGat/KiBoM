
from __future__ import print_function

import sys
import urllib
	
import time
import json

from collections import defaultdict
class Query :
	def __init__(self,term,store_id,api_key,signature=None,timestamp=None,customer_id=None,offset=0,number_of_results=25,rohs=None,in_stock=None,response_group="small",format="XML",strip_xml_namespace=False,json_callback=None):
		"""

		:param str term:
		:param str store_id:
		:param str api_key:
		:param signature:
		:param timestamp:
		:param customer_id:
		:param offset:
		:param number_of_results:
		:param rohs:
		:param in_stock:
		:param response_group:
		:param format:
		:param strip_xml_namespace:
		:param json_callback:
		"""
		self.json_callback = json_callback
		self.strip_xml_namespace = strip_xml_namespace
		self.format = format.upper()
		self.response_group = response_group
		self.in_stock = in_stock
		self.rohs = rohs
		self.number_of_results = number_of_results
		self.offset = offset
		self.term = term
		self.store = store_id
		self.api = api_key
		self.signature = signature
		self.timestamp = timestamp
		self.customer_id = customer_id
		
	def __str__(self):
		out =""
		if self.format not in ["XML","JSON"] :
			raise ValueError("{} format invalid. Format must be JSON or XML".format(self.format))
		xml = self.format == "XML"
		
		if not xml :
			out += "callInfo.responseDataFormat=JSON&"
			if self.json_callback is not None :
				out += "callInfo.callback={}&".format(self.json_callback)
		else :
			if self.strip_xml_namespace :
				out += "callInfo.omitXmlSchema=true&"
		
		
		previous = 0
		keyword= False
		for i in range(0,self.term.count(":")) :
			prev_ini = previous
			for key in ["any","id","manuPartNum"] :
				if self.term.find(":",previous) == self.term.find(key,previous) +len(key) :
					previous = self.term.find(":",previous) +1
					if key == "any" :
						keyword = True
					break
			if previous == prev_ini :
				raise ValueError("Invalid term {}".format(self.term))
		out += "term={}&".format(self.term)
		out += "storeInfo.id={}&".format(self.store)
		out += "callInfo.apiKey={}&".format(self.api)
		
		if self.signature is not None and self.timestamp is not None and self.customer_id is not None :
			out+="userInfo.signature={}&userInfo.timestamp={}&userInfo.customerId={}&".format(self.signature,self.timestamp,self.customer_id)
		
		if keyword :
			out+="resultsSettings.offset={}&resultsSettings.numberOfResults={}&".format(self.offset,self.number_of_results)
		
		if self.rohs or self.in_stock :
			refine = (("rohsCompliant," if self.rohs else "")+("inStock" if self.in_stock else ""))[:-1]
			out+="resultsSettings.refinements.filters={}&".format(refine)
		if self.response_group != "small" :
			out+="resultsSettings.responseGroup="+self.response_group
		
		return out
		
class Farnell:
	#Base HTTP address for API calls. Can be accessed from anywhere.
	base_address = "https://api.element14.com/catalog/products?"
	
	def __init__(self,api_key, store_id = "uk", api_call_per_second = 2):
		"""

		:param str api_key: Retrieved by going to https://partner.element14.com
		:param str store_id: Id of the store to look in. May be the full address
							(uk.farnell.com) or only the prefix if the end is
							.farnell.com
		:param int api_call_per_second: Maximum API calls per second
		"""
		
		self.api_key  = api_key
		self.store_id = store_id + (".farnell.com" if "." not in store_id else "")
		self.api_cooldown = 1.0/api_call_per_second
		self.last_call_time = 0.0
		
	def wait_api_cooldown(self):
		"""
		Wait for API to be available again
		"""
		delta = time.clock() - self.last_call_time
		if delta < self.api_cooldown :
			time.sleep(self.api_cooldown - delta)
	
	
	
	def _request_send(self,req):
		"""
		Low level function to send api call (set the timer)
		
		:param str req: End of the URL to send
		"""
		
		self.wait_api_cooldown()
		if sys.version_info < (3,) :
			ret = urllib.urlopen(Farnell.base_address + str(req)).read()
		else :
			ret = urllib.request.urlopen(Farnell.base_address + str(req)).read()
		self.last_call_time = time.clock()
		return ret
	
	def retrieve_price(self,parts):
		"""

		:param  dict parts:
		:rtype: object
		"""
	
		query_search = "id:" + "%20".join([str(x) for x in parts.keys()])
		q = Query(query_search,self.store_id,self.api_key,response_group="prices",format="JSON")
		result = json.loads(self._request_send(q))
		
		output = defaultdict(dict)
		
		
		for product in result["premierFarnellPartNumberReturn"]["products"] :
			prod_id = product["sku"]
			min_order = int(product["translatedMinimumOrderQuality"])
			
			
			#output[prod_id]["order_qty"]
			order_qty = parts[prod_id] + (min_order - parts[prod_id] % min_order)
			order_price = None
			for price in product["prices"] :
				if int(price["from"]) <= order_qty <= int(price["to"]) :
					order_price = float(price["cost"])
					break
					
			output[prod_id]["order_qty"] = order_qty
			output[prod_id]["unit_price"] = order_price
		
		return output
			
			
			
		
		
if __name__ == "__main__" :
	print("Query Test")
	t = Query("id:80056","fr.farnell.com","monApi")
	print("Simple\t",t)
	
	db = Farnell("API_Number","fr")

	print(db.retrieve_price({"2725932":2,"8648689":2}))
