# import requests
# import sys
# import traceback
# import urllib


# class UrlShortenTinyurl:
#     URL = "http://tinyurl.com/api-create.php"
#     status_code = False
#     short_url = False
#     def shorten(self, url_long):
#         try:
#             url = self.URL + "?" \
#                 + urllib.parse.urlencode({"url": url_long})
#             res = requests.get(url)
#             self.status_code = res.status_code
#             self.short_url = res.text
#         except Exception as e:
#             self.short_url = False