# CoffeApiProject
This project is about practicing creating your RESTFUL API by using Flask Frameware and POSTman tool to create our API Documentation.
![overview](https://user-images.githubusercontent.com/57592040/163733886-8f4ca1ce-43d0-4bf9-b300-63bb73995329.gif)

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

and to achive that we need to create how this service actually work from our server side and here our Flask web application will deal with is as below:
```py
@app.route("/get-api-token", methods=["GET"])
def get_api_token():
    api_token = secrets.token_hex(16)
    if request.method == "GET":
        data = request.get_json()
        users_name = db.session.query(User).filter_by(username=data.get("username")).first()
        if users_name:
            return jsonify(created={"API TOKEN": users_name.api_token})
        else:
            new_user = User(username=data.get("username"),
                            password=data.get("password"),
                            api_token=api_token)
            db.session.add(new_user)
            db.session.commit()
            return jsonify(created={"API TOKEN": api_token})
     else:
         return jsonify(error={"Wrong request": "You need to use GET Request."})
```
To explain this route function we need to take it as three blocks:
first block generated an API Token and it seems like that but it actually about generate a key to give a user more abilities.
And to generate this key I used secrets pre-loaded library to generate a hex token that have 16 bits.
Then we need to store the user data and his API token in a database so I created one as below:
```py
# User TABLE Registration
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    api_token = db.Column(db.String(250), unique=True, nullable=False)
```
So when the user send and GET request with his username and password the user API token will be generated and be save in a database as well, finally the user will get his response that include the Token.
![api token](https://user-images.githubusercontent.com/57592040/163731763-c654c833-ecbf-4ac0-93f4-9bc88b703e18.gif)

As you see I use POSTman tool to test my API and create an API Documentation .
### HTTP GET - /all
This endpoint will Read records and view all cafes available as a json structure you don't need a token for this service. 
And I create this service on flask as below:
```py
@app.route("/all", methods=["GET"])
def all_cafes():
    if request.method == "GET":
        cafes = db.session.query(Cafe).all()
        return jsonify(all_cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Wrong request": "You need to use GET Request."})
```
### HTTP GET- /random
This endpoint will provide a random cafe service and the service code and it is not requared an API Token will be like this :
```py
@app.route("/random", methods=["GET"])
def random():
    if request.method == "GET":
        all_cafe = db.session.query(Cafe).all()
        random_cafe = choice(all_cafe)
        return jsonify(cafe={random_cafe.name: random_cafe.to_dict()})
    else:
        return jsonify(error={"Method Not Allowed": "The method is not allowed for the requested URL."}), 405
```
## HTTP GET - /search
This end point will provide a search about a cafe by it's location and you can limit your search results as well.
An example of the request `/search?loc=Peckham&limit=1` and the code of this service will look like this:
```py
@app.route("/search", methods=["GET"])
def search():
    if request.method == "GET":
        loc = request.args.get("loc")
        results = db.session.query(Cafe).filter(Cafe.location == loc).all()
        limit = int(request.args.get("limit")) if request.args.get("limit") is not None else len(results)
        results = db.session.query(Cafe).filter(Cafe.location == loc).all()
        return jsonify(results=[result.to_dict() for result in results[:limit]]) if len(
            results) and limit != 0 else jsonify(
            error={"Not found": "We did not have a cafe in  this location or you can not use a zero limit."}), 404
```
### HTTP POST - /add
This end point will provide adding new cafe to the database and it reqiured an API token pass with the request headers as below:
```py
headers = {
  'x-api-key': 'ApiSecretKey'
}
```
