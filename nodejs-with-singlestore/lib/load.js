const csv = require("csv-parser");
const path = require("path");
const fs = require("fs");
const { database } = require("./db");

(async () => {
  try {
    await database.table.drop("expenses");

    const table = await database.table.create({
      name: "expenses",
      columns: {
        id: { type: "BIGINT", autoIncrement: true, primaryKey: true },
        createdAt: { type: "DATETIME(6)", default: "CURRENT_TIMESTAMP(6)" },
        merchant: { type: "VARCHAR(128)" },
        category: { type: "VARCHAR(64)" },
        amount: { type: "DECIMAL(10, 2)" },
      },
    });

    const dataset = await (() => {
      return new Promise((resolve, reject) => {
        const result = [];
        fs.createReadStream(path.resolve(process.cwd(), "dataset.csv"))
          .pipe(csv())
          .on("data", ({ createdAt, merchant, category, amount }) => {
            result.push({
              createdAt: new Date(createdAt),
              merchant,
              category,
              amount: Number(amount),
            });
          })
          .on("error", (error) => reject(error))
          .on("end", () => resolve(result));
      });
    })();

    await table.insert(dataset);

    process.exit(0);
  } catch (error) {
    console.error(error);
    process.exit(1);
  }
})();
