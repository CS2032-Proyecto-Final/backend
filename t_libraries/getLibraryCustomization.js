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

    if (!result.Item) {
      return "Tenant not found";
    }

    const { color, photo_url } = result.Item;
    return { color, photo_url };

  } catch (error) {
    return error;
  }
};