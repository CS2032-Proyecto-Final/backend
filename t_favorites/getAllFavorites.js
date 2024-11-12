const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.FAVORITES_TABLE_NAME;

exports.handler = async (event) => {
  try {
    // Obtenemos tenant_id y email desde query en el evento
    const tenant_id = event.query.tenant_id;
    const email = event.query.email;

    // Ejecutamos la consulta en DynamoDB
    const result = await dynamo.send(
      new QueryCommand({
        TableName: tableName,
        KeyConditionExpression: "tenant_id = :tenant_id AND begins_with(#emailIsbn, :email)",
        ExpressionAttributeNames: {
          "#emailIsbn": "email#isbn"
        },
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
          ":email": email,
        },
      })
    );

    // Formateamos los resultados para devolver tanto favoritos activos como inactivos
    const allFavorites = result.Items.map((item) => ({
      isbn: item["email#isbn"].split("#")[1],
      isFavorite: item.isFavorite,
    }));

    return {
      statusCode: 200,
      body: allFavorites,
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while retrieving favorites",
      },
    };
  }
};
