const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, ScanCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.TABLE_NAME;

exports.handler = async (event) => {
  try {
    const result = await dynamo.send(
      new ScanCommand({
        TableName: tableName,
        ProjectionExpression: "tenant_id, photo_url, full_name"
      })
    );

    if (!result.Items || result.Items.length === 0) {
      return {
        statusCode: 404,
        body: "No tenants found"
      };
    }

    return result.Items;

  } catch (error) {
    return error;
  }
};
