const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, GetCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.TABLE_NAME;

exports.handler = async (event) => {
  try {
    const tenant_id = event.query.tenant_id;

    const result = await dynamo.send(
      new GetCommand({
        TableName: tableName,
        Key: { tenant_id },
      })
    );

    return result.Item;
  } catch (error) {
    return error;
  }
};
