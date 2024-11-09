import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.TABLE_NAME;

export const handler = async (event) => {
  try {
    const libraryData = JSON.parse(event.body);
    await dynamo.send(
      new PutCommand({
        TableName: tableName,
        Item: {
          tenant_id: libraryData.tenant_id,
          suffix_email: libraryData.suffix_email,
          reserv_time: libraryData.reserv_time,
          reserv_environ_time: libraryData.reserv_environ_time,
          color: libraryData.color,
          photo_url: libraryData.photo_url,
        },
      })
    );

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Library created successfully" }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
