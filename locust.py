from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    ''' Locust Stress Test '''
    # Note 1: Test can be started in a terminal with: locust -f locust.py
    # Note 2: Test results can be accessed at: http://localhost:8089/
    # Note 3: Test must be run locally and not on the web app's server
    wait_time = between(1, 5)   # users spawn rate
    
    # Uncomment lines 8 to 12 to test the Get Datasets webpage
    # @task
    # def get_datasets_page(self):
    #     self.client.get("/machine")
    #     self.client.get("/machine/itu_basket_gni/None")
    #     self.client.get("/machine/itu_basket_gni/country")
    
    # Uncomment lines 15 to 19 to test the Index webpage 
    # @task
    # def index_page(self):
    #     self.client.get("/index")
    #     self.client.get("/static/html/graph_adop.html")
    #     self.client.get("/static/html/graph_use.html")

    # Uncomment lines 22 to 24 to test the Data Listing webpage: Top Level Domain Listing
    # @task
    # def data_listing(self):
    #     self.client.get("/tld")

    # Uncomment lines 27 to 29 to test the Data Listing webpage's subpage : Top Level Domain - Anguilla
    # @task
    # def data_listing_subpage(self):
    #     self.client.get("/tld/Anguilla")