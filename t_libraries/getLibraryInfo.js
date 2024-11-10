const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.TABLE_NAME;

exports.handler = async (event) => {
  try {
    const email = event.query.email;
    const email_suffix = email.split('@')[1];

    const result = await dynamo.send(
      new QueryCommand({
        TableName: tableName,
        IndexName: 'email_suffix-index',
        KeyConditionExpression: 'email_suffix = :suffix',
        ExpressionAttributeValues: {
          ':suffix': email_suffix,
        },
      })
    );

    return {
      statusCode: 200,
      body: JSON.stringify(result.Items[0] || { message: "Library not found" }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
