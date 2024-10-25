const { AI } = require("@singlestore/ai");
const { SingleStoreClient } = require("@singlestore/client");
const fs = require("fs");
require("dotenv").config();

const ai = new AI({ openAIApiKey: process.env.OPENAI_API_KEY });
const client = new SingleStoreClient({ ai });

const connection = client.connect({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  port: Number(process.env.DB_PORT),
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  ssl: {
    ca: fs.readFileSync("./singlestore_bundle.pem"),
  },
});

const database = connection.database.use(process.env.DB_NAME);

module.exports = {
  ai,
  client,
  connection,
  database,
};
