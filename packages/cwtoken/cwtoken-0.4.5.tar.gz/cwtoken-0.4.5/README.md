cwtoken Technical Reference
===========================

cwtoken simplifies working with PostgREST APIs by:

- Automatically handling **access token generation**
- Provides a query constructor for URL generation, and a diagnostic mode for debugging
- Making authenticated **GET requests** to PostgREST endpoints
- Providing a **CLI** for quick testing and usage
- Including a user-friendly **GUI** for building and running queries without code

---

cwapi — API Client
------------------

Represents an authenticated connection to the PostgREST API. All queries are created via this object.

Constructor:

client = cwapi(
    api_token: str,
    clubcode: str = None,        # required if access_token not provided
    access_token: str = None,
    base_url: str = "https://atukpostgrest.clubwise.com/"
)

Attributes:

- client.access_token — automatically fetched if not provided
- client.headers — dict of headers including Authorization
- client.clubcode — club code used

Methods:

- client.table(endpoint: str) -> query  
  Returns a query constructor object for building endpoint queries. Supports method chaining.

- client.raw_query(full_query: str) -> RawQuery  
  Returns a raw query object for executing a fully specified URL.

query — Table-based Query Constructor
-------------------------------------

- Created via client.table(endpoint)
- Supports chained methods:

q = client.table("member") \
          .select("member_no", "first_name") \
          .filters("date_of_birth=gt.1980-01-01") \
          .order("first_name", desc=True) \
          .limit(10)

Methods:

- .select(*columns) — adds columns to select
- .filters(*filters) — raw PostgREST filter strings
- .order(*columns, desc=False) — orders results
- .limit(n) — limits results
- .fetch(diagnostic=False) -> pandas.DataFrame — executes query

RawQuery — Direct URL Query
---------------------------

- Created via client.raw_query(full_query)
- method:

df = client.raw_query("member?select=first_name&limit=10").fetch()

- .fetch() -> pandas.DataFrame — executes URL request
- Bypasses query builder chaining; used for pre-formed URLs

CLI Functions
-------------

### test_connection()

Pings the API server to check if it's reachable.

Can be run from the CLI:

cwtoken test

### cwtoken gui
Launches the graphical interface for building and executing queries.

Run it from the CLI like this:

cwtoken gui

Notes on Usage
--------------

- Queries are always linked to a client.
- Method chaining is supported for the query object.
- Both query and RawQuery return pandas.DataFrame on .fetch().
- RawQuery can be used for fully constructed URLs without using the query builder.