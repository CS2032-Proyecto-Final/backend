const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, PutCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.TABLE_NAME;

exports.handler = async (event) => {
  try {
    const libraryData = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    await dynamo.send(
      new PutCommand({
        TableName: tableName,
        Item: {
          tenant_id: libraryData.tenant_id,
          email_suffix: libraryData.email_suffix,
          reserv_book_time: libraryData.reserv_book_time,
          reserv_env_time: libraryData.reserv_env_time,
          color: libraryData.color,
          logo_url: libraryData.logo_url,
          background_url: libraryData.background_url,
          env_types: libraryData.env_types,
          full_name: libraryData.full_name
        },
      })
    );

    return {
      statusCode: 200,
      body: {
        message: "Library created successfully",
        data: libraryData
      }
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while creating the library"
      }
    };
  }
};
