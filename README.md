# CoffeApiProject
This project is about practicing creating your RESTFUL API by using Flask Frameware and POSTman tool.
## Designing your API Servecies
When you start thinking about building your own RESTful API you need to know what services you are going to provide throw it to the end user.
So with this practice we are going to build a Cafes informations providers API that mean we are going to create a cafes database to collects cafes data as below:
Cafe name, Cafe location, Cafe image, Cafe available seats, coffee prices and if it have toliet, wifi, sockets, and can take calls.
## Create Route and Endpoints
So Now we need to focuse on which route we are gonna use and which endpoints we will provide to offer different services.
For route will be a localhost for now `127.0.0.1:5000` as flask provide and the endpoints and it services will be as below:
### HTTP GET - /get-api-token
This end point will give a user a API Token that will allow the user to add cafe, update the coffee price and delete a cafe from a database.
To get an API Token you need to send your choosen username  and your password as a json data stracture to the body request and we are going to use HTTP GET request as below:
```py
url = "http://127.0.0.1:5000/get-api-token"

payload = "{
            "username":"shalaby",
            "password":12345678}"

response = requests.request("GET", url, data=payload)
print(response.text)
```
and the user will get a an API Token as json to use it for the services that need an API token.
```
{
    "created": {
        "API TOKEN": "47e7e654a032567625b46b7ce8cef994"
    }
}
```

and to achive that we need to create how this service actually work from our server side and here our Flask web aoolication will deal with is as below:
```py

