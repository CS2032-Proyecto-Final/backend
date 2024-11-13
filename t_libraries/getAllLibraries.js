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
        ProjectionExpression: "tenant_id, logo_url, full_name"
      })
    );

    if (!result.Items || result.Items.length === 0) {
      return {
        statusCode: 404,
        body: {
          message: "No tenants found"
        }
      };
    }

    return {
      statusCode: 200,
      body: result.Items
    };

  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred during the scan operation"
      }
    };
  }
};
