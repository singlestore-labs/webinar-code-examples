const { AI } = require("@singlestore/ai");
const { SingleStoreClient } = require("@singlestore/client");
const fs = require("fs");
const path = require('path');
require("dotenv").config();

const ai = new AI({ openAIApiKey: process.env.OPENAI_API_KEY });
const client = new SingleStoreClient({ ai });

const certPath = path.join(__dirname, 'singlestore_bundle.pem');
console.log('Looking for cert at:', certPath);

const connection = client.connect({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  port: Number(process.env.DB_PORT),
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  ssl: {
    ca: fs.readFileSync(certPath),
  },
});

const database = connection.database.use(process.env.DB_NAME);

module.exports = {
  ai,
  client,
  connection,
  database,
};
