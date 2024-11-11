const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.TABLE_NAME;

exports.handler = async (event) => {
  try {
    const email = event.query.email;
    const email_suffix = email.split('@')[1];

    const result = await dynamo.send(
      new GetCommand({
        TableName: tableName,
        Key: { email_suffix },
      })
    );

    return {
      statusCode: 200,
      body: JSON.stringify(result.Item || { message: "Library not found" }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
