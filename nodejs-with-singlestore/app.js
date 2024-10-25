const express = require("express");
const { ChatCompletionTool } = require("@singlestore/ai");
const z = require("zod");
const { ai, database } = require("./lib/db");

const app = express();
app
  .use(express.json())
  .use((error, _req, res, next) => {
    console.error(error.stack);
    res.status(500).send(error.message || "Internal Server Error");
  });
;

const expensesTable = database.table.use("expenses");

app.get("/expenses", async (req, res, next) => {
  try {
    const { merchant, category } = req.query;

    const rows = await expensesTable.find({
      where: {
        merchant,
        category,
      },
    });

    res.status(200).json(rows);
  } catch (error) {
    next(error);
  }
});

app.get("/expenses/:id", async (req, res, next) => {
  try {
    const [row] = await expensesTable.find({ where: { id: req.params.id } });
    res.status(200).json(row);
  } catch (error) {
    next(error);
  }
});

app.put("/expenses/:id", async (req, res, next) => {
  try {
    const { id, ...values } = req.body;
    await expensesTable.update(values, { id: req.params.id });
    res.status(200).send();
  } catch (error) {
    next(error);
  }
});

app.delete("/expenses/:id", async (_req, res, next) => {
  try {
    await expensesTable.delete({ id: res.params.id });
    res.status(200).send();
  } catch (error) {
    next(error);
  }
});

app.post("/expenses/search", async (req, res, next) => {
  try {
    const { query } = req.body;

    const tableSchema = await expensesTable.showColumnsInfo(true);

    const completion = await ai.chatCompletions.create({
      model: "gpt-4o",
      prompt: `\
      User prompt: ${query}
      Table schema: ${JSON.stringify(tableSchema)}

      Based on the table schema, parse the user's prompt into parameters.
      Include only the JSON value without any formatting in your response to make it ready for use with the JS JSON.parse method.
      If there is an issue return an empty JSON value.
    `,
    });

    const { category, merchant, amount } = JSON.parse(completion.content);

    const rows = await expensesTable.find({
      where: {
        category,
        merchant,
        amount: amount ? Number(amount) : undefined,
      },
    });

    res.status(200).json(rows);
  } catch (error) {
    console.log(error);
    next(error);
  }
});

app.post("/expenses/ask", async (req, res, next) => {
  try {
    const { query } = req.body;

    const queryTableTool = new ChatCompletionTool({
      name: "query_table",
      description:
        "Generates and executes a MySQL SELECT query based on a natural language prompt, adhering to the provided table schema.",
      params: z.object({
        prompt: z.string().describe("A natural language description of the data you wish to retrieve from the table."),
      }),
      call: async (params) => {
        let value = "";
        const schema = await expensesTable.showColumnsInfo();

        const gptQuery = await ai.chatCompletions.create({
          stream: false,
          model: "gpt-4o",
          prompt: params.prompt,
          systemRole: `\
            You are a MySQL database expert.
            Generate a valid MySQL SELECT query based on the following table schema: ${JSON.stringify(schema)}

            The query must adhere to these rules:
            - Only SELECT operations are allowed.

            Respond with the MySQL query only, without any formatting.
            For example: "SELECT * FROM expenses"
          `,
        });

        if (gptQuery && "content" in gptQuery && typeof gptQuery.content === "string") {
          const [rows] = await database.query(gptQuery.content);
          value = JSON.stringify(rows);
        }

        return { name: "query_table", params, value };
      },
    });

    const completion = await ai.chatCompletions.create({
      model: "gpt-4o",
      prompt: query,
      stream: false,
      systemRole: `\
        You are a knowledgeable assistant focused on helping the user with queries related to the "expenses" table.\
        Provide accurate and relevant answers based on the structure and data in the "expenses" table, and assist with any related tasks or requests.
      `,
      tools: [queryTableTool],
    });

    res.status(200).send(completion.content);
  } catch (error) {
    next(error);
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, async () => {
  console.log(`Server is running on port ${PORT}`);
});
