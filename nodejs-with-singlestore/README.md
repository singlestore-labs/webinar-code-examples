# NodeJS With SingleStore Expenses Demo App

## Getting Started

1. Download an SSL certificate using this [link](https://portal.singlestore.com/static/ca/singlestore_bundle.pem).
2. Place the SSL certificate in the root directory of the project.
3. Create a `.env` file based on the `.env.example` file.
4. Install the dependencies by running `npm install`.
5. Load data into a database by running `npm run load`.
6. Run the server by running `npm run start`.

## API

#### Get All Expenses

```
GET http://localhost:3000/expenses
```

#### Get Filtered Expenses

```
GET http://localhost:3000/expenses?merchant=Airbnb&category=Travel
```

#### Get Expenses Record by ID

```
GET http://localhost:3000/expenses/:id
```

#### Update Expenses Record by ID

```
PUT http://localhost:3000/expenses/:id
```

#### Delete Expenses Record by ID

```
DELETE http://localhost:3000/expenses/:id
```

#### Search Expenses

```
POST http://localhost:3000/expenses/search

{
    "query": "Travel with Airbnb"
}
```

#### Ask Assistant

```
POST http://localhost:3000/expenses/ask

{
    "query": "How much have I spent on Netfix?"
}
```