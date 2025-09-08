import requests
import time
import click

def test_connection():
    url = 'https://atukpostgrest.clubwise.com/'
    try:
        start = time.perf_counter()
        response = requests.head(url, timeout=5)
        end = time.perf_counter()
        response_time = end - start
        if response.status_code < 400:
            print(f"Server is reachable (status code: {response.status_code}) in {response_time:.2f}s")
            return 1
        else:
            print(f"Server responded, but with error status code: {response.status_code} in {response_time:.2f}s")
            return 0
    except requests.exceptions.ConnectionError:
        print("Failed to connect: Server unreachable.")
        return 0
    except requests.exceptions.Timeout:
        print(f"Connection timed out after {timeout} seconds.")
        return 0
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 0
        
        
class QueryWrapper:
    def __init__(self, query):
        self.query = query
    def full_url(self):
        if self.query.query_type == "Constructor":
            return self.query.compose_url()
        elif self.query.query_type == "Raw":
            return self.query.full_query
        else:
            return None
    
    def get_table(self):
        if self.query.query_type == "Constructor":
            return self.query.endpoint
        else:
            return None
    
    def get_select(self):
        if self.query.query_type == "Constructor":
            return self.query._params.get('select')
        else:
            return None
    def get_filters(self):
        if self.query.query_type == "Constructor":
            return getattr(self.query, "_filters", None)
        else:
            return None
    def get_orders(self):
        if self.query.query_type == "Constructor":
            return self.query._params.get('order')
        else:
            return None
    def get_limit(self):
        if self.query.query_type == "Constructor":
            return self.query._params.get('limit')
        else:
            return None
    def run(self):
        if self.query.query_type == "Constructor":
            return self.query.fetch(diagnostic=True)
        elif self.query.query_type == "Raw":
            return self.query.fetch()
        else:
            return None