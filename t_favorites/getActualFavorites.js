const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.FAVORITES_TABLE_NAME;

exports.handler = async (event) => {
  try {
    const tenant_id = event.query.tenant_id;
    const email = event.query.email;

    // Consulta solo los elementos favoritos que tienen `isFavorite` como `true`
    const result = await dynamo.send(
      new QueryCommand({
        TableName: tableName,
        KeyConditionExpression: "tenant_id = :tenant_id AND begins_with(#emailIsbn, :email)",
        FilterExpression: "isFavorite = :trueVal",
        ExpressionAttributeNames: {
          "#emailIsbn": "email#isbn"
        },
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
          ":email": email,
          ":trueVal": true
        },
      })
    );

    // Formatear solo los items con `isFavorite: true`
    const actualFavorites = result.Items.map((item) => ({
      isbn: item["email#isbn"].split("#")[1],
      isFavorite: item.isFavorite,
    }));

    return {
      statusCode: 200,
      body: actualFavorites,
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while retrieving favorite items",
      },
    };
  }
};
